"""
条件标准化流 (Conditional Normalizing Flow)

用于生成时变、非对称的概率分布
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class AffineCouplingLayer(nn.Module):
    """
    仿射耦合层 (Affine Coupling Layer)

    可逆变换：y = x_masked + (1 - mask) * (x * exp(s(x_masked, c)) + t(x_masked, c))
    """

    def __init__(self, input_dim, hidden_dim, context_dim, mask):
        super().__init__()
        self.mask = nn.Parameter(mask, requires_grad=False)

        # 尺度网络 (scale)
        self.scale_net = nn.Sequential(
            nn.Linear(input_dim + context_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
            nn.Tanh()  # 限制尺度范围
        )

        # 平移网络 (translation)
        self.shift_net = nn.Sequential(
            nn.Linear(input_dim + context_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim)
        )

    def forward(self, x, context, reverse=False):
        """
        前向或逆向变换

        Args:
            x: [batch, input_dim]
            context: [batch, context_dim] 条件信息（时间、天气等）
            reverse: 是否逆向（推理时使用）

        Returns:
            y: 变换后的张量
            log_det: 对数行列式（用于计算似然）
        """
        if not reverse:
            return self._forward(x, context)
        else:
            return self._inverse(x, context)

    def _forward(self, x, context):
        """前向变换"""
        x_masked = x * self.mask

        # 拼接条件信息
        s = self.scale_net(torch.cat([x_masked, context], dim=-1))
        t = self.shift_net(torch.cat([x_masked, context], dim=-1))

        # 仿射变换
        y = x_masked + (1 - self.mask) * (x * torch.exp(s) + t)

        # 计算log-determinant
        log_det = torch.sum((1 - self.mask) * s, dim=-1)

        return y, log_det

    def _inverse(self, y, context):
        """逆向变换（推理时使用）"""
        y_masked = y * self.mask

        s = self.scale_net(torch.cat([y_masked, context], dim=-1))
        t = self.shift_net(torch.cat([y_masked, context], dim=-1))

        # 逆仿射变换
        x = y_masked + (1 - self.mask) * ((y - t) * torch.exp(-s))

        log_det = -torch.sum((1 - self.mask) * s, dim=-1)

        return x, log_det


class NormalizingFlow(nn.Module):
    """
    条件标准化流模型

    通过堆叠多个可逆变换层，将简单分布（高斯）变换为复杂分布
    """

    def __init__(self, input_dim, context_dim, num_flows=8, hidden_dim=128):
        super().__init__()
        self.input_dim = input_dim
        self.num_flows = num_flows

        # 创建交替的mask模式
        self.flows = nn.ModuleList()
        for i in range(num_flows):
            # 交替mask（偶数层mask前半部分，奇数层mask后半部分）
            mask = self._create_mask(input_dim, i % 2 == 0)
            self.flows.append(
                AffineCouplingLayer(input_dim, hidden_dim, context_dim, mask)
            )

        # 条件编码器（将时间、天气等特征编码为context向量）
        self.context_encoder = nn.Sequential(
            nn.Linear(context_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, context_dim)
        )

    def _create_mask(self, dim, mask_first_half):
        """创建mask"""
        mask = torch.zeros(dim)
        if mask_first_half:
            mask[:dim // 2] = 1
        else:
            mask[dim // 2:] = 1
        return mask

    def forward(self, x, context, reverse=False):
        """
        前向或逆向传播

        Args:
            x: [batch, input_dim] 如果reverse=False，是基分布样本；否则是观测值
            context: [batch, context_dim] 条件信息
            reverse: 是否逆向

        Returns:
            y: 变换后的张量
            log_det_sum: 总的log-determinant
        """
        # 编码条件信息
        context = self.context_encoder(context)

        log_det_sum = 0

        if not reverse:
            # 正向：基分布 -> 复杂分布
            for flow in self.flows:
                x, log_det = flow(x, context, reverse=False)
                log_det_sum = log_det_sum + log_det
        else:
            # 逆向：复杂分布 -> 基分布（推理时使用）
            for flow in reversed(self.flows):
                x, log_det = flow(x, context, reverse=True)
                log_det_sum = log_det_sum + log_det

        return x, log_det_sum

    def log_prob(self, x, context):
        """
        计算对数似然 p(x|context)

        Args:
            x: [batch, input_dim] 观测值
            context: [batch, context_dim]

        Returns:
            log_prob: [batch] 对数概率
        """
        # 逆向变换到基分布
        z, log_det_sum = self.forward(x, context, reverse=True)

        # 基分布的对数概率（标准高斯）
        log_prob_z = -0.5 * (torch.sum(z ** 2, dim=-1) + self.input_dim * np.log(2 * np.pi))

        # 变量变换公式
        log_prob_x = log_prob_z + log_det_sum

        return log_prob_x

    def sample(self, context, num_samples=1):
        """
        从条件分布中采样

        Args:
            context: [batch, context_dim]
            num_samples: 采样数量

        Returns:
            samples: [batch, num_samples, input_dim]
        """
        batch_size = context.size(0)

        # 从基分布（标准高斯）采样
        z = torch.randn(batch_size, num_samples, self.input_dim, device=context.device)

        samples = []
        for i in range(num_samples):
            # 正向变换到目标分布
            x, _ = self.forward(z[:, i, :], context, reverse=False)
            samples.append(x.unsqueeze(1))

        return torch.cat(samples, dim=1)


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("Normalizing Flow模块测试")
    print("=" * 60)

    # 参数设置
    input_dim = 7  # 预测7天
    context_dim = 32  # 条件特征维度（时间、天气、历史等）
    num_flows = 8
    hidden_dim = 128
    batch_size = 16

    # 创建模型
    model = NormalizingFlow(input_dim, context_dim, num_flows, hidden_dim)
    print(f"模型参数量: {sum(p.numel() for p in model.parameters()):,}")

    # 创建随机输入
    x = torch.randn(batch_size, input_dim)  # 观测值
    context = torch.randn(batch_size, context_dim)  # 条件信息

    # 测试前向传播
    print("\n测试前向传播...")
    z, log_det = model(x, context, reverse=False)
    print(f"输入形状: {x.shape}")
    print(f"变换后形状: {z.shape}")
    print(f"Log-determinant形状: {log_det.shape}")

    # 测试逆向传播
    print("\n测试逆向传播...")
    x_recon, log_det_inv = model(z, context, reverse=True)
    recon_error = torch.mean((x - x_recon) ** 2)
    print(f"重构误差: {recon_error.item():.6f}")

    # 测试对数似然计算
    print("\n测试对数似然...")
    log_prob = model.log_prob(x, context)
    print(f"Log-likelihood形状: {log_prob.shape}")
    print(f"平均log-likelihood: {log_prob.mean().item():.4f}")

    # 测试采样
    print("\n测试采样...")
    model.eval()
    with torch.no_grad():
        samples = model.sample(context, num_samples=100)
    print(f"采样形状: {samples.shape}")
    print(f"采样均值: {samples.mean(dim=1).mean().item():.4f}")
    print(f"采样标准差: {samples.std(dim=1).mean().item():.4f}")

    print("\n✅ Normalizing Flow模块测试通过")
