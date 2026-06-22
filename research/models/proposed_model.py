"""
完整的创新模型：GraphVAE + Normalizing Flow + Decision-aware Loss

将三个组件整合为端到端的概率预测模型
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from pathlib import Path
import sys

# 添加models目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from models.graph_vae import GraphVAE, build_initial_graph
from models.normalizing_flow import NormalizingFlow


class ProposedModel(nn.Module):
    """
    完整的创新模型

    架构：
    1. GraphVAE: 学习动态空间依赖
    2. Temporal Encoder: 编码历史时序特征
    3. Normalizing Flow: 生成非对称概率分布
    4. Decision-aware Loss: 业务导向优化
    """

    def __init__(self, config):
        super().__init__()
        self.config = config

        # 1. 图变分自编码器（空间建模）
        self.graph_vae = GraphVAE(
            num_nodes=config['num_nodes'],
            input_dim=config['history_window'],
            hidden_dim=config['hidden_dim'],
            latent_dim=config['latent_dim']
        )

        # 2. 时序编码器（LSTM）
        self.temporal_encoder = nn.LSTM(
            input_size=config['num_nodes'],
            hidden_size=config['hidden_dim'],
            num_layers=2,
            batch_first=True,
            dropout=0.2
        )

        # 3. 条件特征融合
        self.condition_fusion = nn.Sequential(
            nn.Linear(config['hidden_dim'] + config['latent_dim'] + config['external_dim'], config['context_dim']),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(config['context_dim'], config['context_dim'])
        )

        # 4. 标准化流（分布生成）
        self.normalizing_flow = NormalizingFlow(
            input_dim=config['forecast_horizon'],
            context_dim=config['context_dim'],
            num_flows=config['num_flows'],
            hidden_dim=config['hidden_dim']
        )

        # 5. 分位数预测头（辅助监督）
        self.quantile_head = nn.Sequential(
            nn.Linear(config['context_dim'], config['hidden_dim']),
            nn.ReLU(),
            nn.Linear(config['hidden_dim'], config['forecast_horizon'] * 3)  # P10, P50, P90
        )

    def forward(self, x_history, edge_index, external_features=None):
        """
        前向传播

        Args:
            x_history: [batch, history_window, num_nodes] 历史需求
            edge_index: [2, num_edges] 初始图结构
            external_features: [batch, external_dim] 天气、节假日等

        Returns:
            outputs: 包含预测分布参数、邻接矩阵等的字典
        """
        batch_size = x_history.size(0)

        # 1. 空间依赖建模（GraphVAE）
        # 使用最近一天的数据作为节点特征
        x_recent = x_history[:, -1, :]  # [batch, num_nodes]

        # 对batch中每个样本单独处理GraphVAE
        adj_list = []
        mu_spatial_list = []
        logvar_spatial_list = []

        for i in range(batch_size):
            adj_recon, mu_s, logvar_s = self.graph_vae(x_recent[i].unsqueeze(0).T, edge_index)
            adj_list.append(adj_recon)
            mu_spatial_list.append(mu_s.mean(dim=0))  # 聚合所有节点的潜在表示
            logvar_spatial_list.append(logvar_s.mean(dim=0))

        adj_batch = torch.stack(adj_list)  # [batch, num_nodes, num_nodes]
        mu_spatial = torch.stack(mu_spatial_list)  # [batch, latent_dim]
        logvar_spatial = torch.stack(logvar_spatial_list)

        # 2. 时序特征编码（LSTM）
        lstm_out, (h_n, c_n) = self.temporal_encoder(x_history)
        h_temporal = h_n[-1]  # [batch, hidden_dim] 取最后一层的hidden state

        # 3. 条件特征融合
        if external_features is None:
            external_features = torch.zeros(batch_size, self.config['external_dim'], device=x_history.device)

        context = torch.cat([h_temporal, mu_spatial, external_features], dim=-1)
        context = self.condition_fusion(context)  # [batch, context_dim]

        # 4. 分位数预测（辅助输出）
        quantile_preds = self.quantile_head(context)  # [batch, horizon * 3]
        quantile_preds = quantile_preds.view(batch_size, self.config['forecast_horizon'], 3)

        # 5. 采样预测分布（Normalizing Flow）
        samples = self.normalizing_flow.sample(context, num_samples=self.config.get('num_samples', 100))
        # samples: [batch, num_samples, horizon]

        # 计算分位数
        p10 = torch.quantile(samples, 0.1, dim=1)
        p50 = torch.quantile(samples, 0.5, dim=1)
        p90 = torch.quantile(samples, 0.9, dim=1)

        outputs = {
            'samples': samples,  # [batch, num_samples, horizon]
            'p10': p10,  # [batch, horizon]
            'p50': p50,
            'p90': p90,
            'quantile_preds': quantile_preds,  # 辅助预测
            'adj_matrix': adj_batch,  # [batch, num_nodes, num_nodes]
            'mu_spatial': mu_spatial,
            'logvar_spatial': logvar_spatial,
            'context': context
        }

        return outputs

    def compute_loss(self, outputs, targets, adj_true, capacity_threshold):
        """
        决策感知损失函数

        Args:
            outputs: forward()的输出
            targets: [batch, horizon] 真实值
            adj_true: [batch, num_nodes, num_nodes] 真实邻接矩阵
            capacity_threshold: 处理能力阈值

        Returns:
            loss_dict: 包含各项损失的字典
        """
        batch_size = targets.size(0)

        # 1. CRPS损失（主损失）
        crps_loss = self._crps_loss(outputs['samples'], targets)

        # 2. 分位数损失（辅助监督）
        quantile_loss = self._quantile_loss(
            outputs['quantile_preds'],
            targets,
            quantiles=[0.1, 0.5, 0.9]
        )

        # 3. GraphVAE损失
        vae_loss, recon_loss, kl_loss = 0, 0, 0
        for i in range(batch_size):
            l, r, k = self.graph_vae.loss_function(
                outputs['adj_matrix'][i],
                adj_true[i],
                outputs['mu_spatial'][i].unsqueeze(0),
                outputs['logvar_spatial'][i].unsqueeze(0)
            )
            vae_loss += l
            recon_loss += r
            kl_loss += k
        vae_loss /= batch_size

        # 4. 决策感知损失（资源错配成本）
        decision_loss = self._decision_aware_loss(
            outputs['p90'],  # 使用90%分位数做决策
            targets,
            capacity_threshold
        )

        # 总损失
        total_loss = (
            crps_loss +
            0.3 * quantile_loss +
            0.1 * vae_loss +
            0.5 * decision_loss
        )

        loss_dict = {
            'total': total_loss,
            'crps': crps_loss,
            'quantile': quantile_loss,
            'vae': vae_loss,
            'vae_recon': recon_loss,
            'vae_kl': kl_loss,
            'decision': decision_loss
        }

        return loss_dict

    def _crps_loss(self, samples, targets):
        """
        CRPS (Continuous Ranked Probability Score) 损失

        衡量预测分布与真实值的距离
        """
        # samples: [batch, num_samples, horizon]
        # targets: [batch, horizon]

        targets_expanded = targets.unsqueeze(1)  # [batch, 1, horizon]

        # CRPS = E[|X - y|] - 0.5 * E[|X - X'|]
        term1 = torch.mean(torch.abs(samples - targets_expanded), dim=1)  # [batch, horizon]

        num_samples = samples.size(1)
        samples_i = samples.unsqueeze(2)  # [batch, num_samples, 1, horizon]
        samples_j = samples.unsqueeze(1)  # [batch, 1, num_samples, horizon]
        term2 = torch.mean(torch.abs(samples_i - samples_j), dim=(1, 2))  # [batch, horizon]

        crps = term1 - 0.5 * term2
        return crps.mean()

    def _quantile_loss(self, preds, targets, quantiles):
        """
        分位数损失

        preds: [batch, horizon, 3] 预测的三个分位数
        targets: [batch, horizon]
        quantiles: [0.1, 0.5, 0.9]
        """
        total_loss = 0
        for i, q in enumerate(quantiles):
            pred_q = preds[:, :, i]
            errors = targets - pred_q
            loss_q = torch.max((q - 1) * errors, q * errors)
            total_loss += loss_q.mean()

        return total_loss / len(quantiles)

    def _decision_aware_loss(self, pred_p90, targets, capacity_threshold):
        """
        决策感知损失

        惩罚导致资源错配的预测误差：
        - 高估（False Positive）：浪费资源
        - 低估（False Negative）：服务失败（更严重）

        Args:
            pred_p90: [batch, horizon] 90%分位数预测
            targets: [batch, horizon] 真实需求
            capacity_threshold: 处理能力阈值
        """
        # 预测决策：预测是否超载
        pred_overload = (pred_p90 > capacity_threshold).float()

        # 真实情况：实际是否超载
        true_overload = (targets > capacity_threshold).float()

        # False Negative (低估)：预测正常但实际超载 - 更严重
        fn_mask = (pred_overload == 0) & (true_overload == 1)
        fn_loss = fn_mask.float() * torch.abs(targets - pred_p90) * 3.0  # 权重3倍

        # False Positive (高估)：预测超载但实际正常
        fp_mask = (pred_overload == 1) & (true_overload == 0)
        fp_loss = fp_mask.float() * torch.abs(targets - pred_p90) * 1.0

        # True cases 也保留小权重
        correct_mask = (pred_overload == true_overload)
        correct_loss = correct_mask.float() * torch.abs(targets - pred_p90) * 0.1

        total_loss = (fn_loss + fp_loss + correct_loss).mean()

        return total_loss


def create_model(config=None):
    """
    创建模型实例

    Args:
        config: 配置字典，如果为None则使用默认配置

    Returns:
        model: ProposedModel实例
    """
    if config is None:
        config = {
            'num_nodes': 60,
            'history_window': 14,  # 用14天历史预测7天未来
            'forecast_horizon': 7,
            'hidden_dim': 128,
            'latent_dim': 32,
            'context_dim': 64,
            'external_dim': 10,  # 天气、节假日等
            'num_flows': 8,
            'num_samples': 100
        }

    model = ProposedModel(config)
    return model


if __name__ == "__main__":
    # 测试完整模型
    print("=" * 60)
    print("完整创新模型测试")
    print("=" * 60)

    config = {
        'num_nodes': 60,
        'history_window': 14,
        'forecast_horizon': 7,
        'hidden_dim': 128,
        'latent_dim': 32,
        'context_dim': 64,
        'external_dim': 10,
        'num_flows': 8,
        'num_samples': 100
    }

    model = create_model(config)
    print(f"模型参数量: {sum(p.numel() for p in model.parameters()):,}")

    # 创建测试数据
    batch_size = 4
    x_history = torch.randn(batch_size, 14, 60)  # 14天历史
    external_features = torch.randn(batch_size, 10)
    targets = torch.randint(800, 1200, (batch_size, 7)).float()  # 7天未来
    adj_true = torch.rand(batch_size, 60, 60)
    adj_true = (adj_true + adj_true.transpose(1, 2)) / 2
    capacity_threshold = 1000.0

    # 构建初始图
    edge_index, _ = build_initial_graph(60)

    # 前向传播
    print("\n前向传播测试...")
    model.train()
    outputs = model(x_history, edge_index, external_features)

    print(f"采样形状: {outputs['samples'].shape}")
    print(f"P10形状: {outputs['p10'].shape}")
    print(f"P50形状: {outputs['p50'].shape}")
    print(f"P90形状: {outputs['p90'].shape}")
    print(f"邻接矩阵形状: {outputs['adj_matrix'].shape}")

    # 损失计算
    print("\n损失计算测试...")
    loss_dict = model.compute_loss(outputs, targets, adj_true, capacity_threshold)

    print(f"总损失: {loss_dict['total'].item():.4f}")
    print(f"CRPS损失: {loss_dict['crps'].item():.4f}")
    print(f"分位数损失: {loss_dict['quantile'].item():.4f}")
    print(f"VAE损失: {loss_dict['vae'].item():.4f}")
    print(f"决策感知损失: {loss_dict['decision'].item():.4f}")

    # 推理模式
    print("\n推理模式测试...")
    model.eval()
    with torch.no_grad():
        outputs_eval = model(x_history, edge_index, external_features)

    print(f"推理预测P50: {outputs_eval['p50'][0, :3]}")  # 前3天
    print(f"推理预测P90: {outputs_eval['p90'][0, :3]}")

    print("\n✅ 完整模型测试通过")
