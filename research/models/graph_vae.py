"""
图变分自编码器 (Graph Variational Autoencoder)

用于动态生成物流网点间的空间依赖关系图
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv


class GraphVAE(nn.Module):
    """
    图变分自编码器

    功能：
    1. 编码器：将节点特征编码为潜在表示（均值和方差）
    2. 重参数化：从潜在分布中采样
    3. 解码器：从潜在表示重构邻接矩阵

    Args:
        num_nodes: 节点数量（60个网格）
        input_dim: 输入特征维度（历史需求+外部特征）
        hidden_dim: 隐藏层维度
        latent_dim: 潜在空间维度
    """

    def __init__(self, num_nodes=60, input_dim=14, hidden_dim=128, latent_dim=32):
        super().__init__()
        self.num_nodes = num_nodes
        self.latent_dim = latent_dim

        # 编码器：两层GCN
        self.conv1 = GCNConv(input_dim, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, hidden_dim)

        # 潜在空间映射
        self.fc_mu = nn.Linear(hidden_dim, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim, latent_dim)

        # 解码器：MLP生成邻接矩阵
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_nodes)
        )

        # 批归一化
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        self.bn2 = nn.BatchNorm1d(hidden_dim)

    def encode(self, x, edge_index):
        """
        编码器：节点特征 -> 潜在分布参数

        Args:
            x: [num_nodes, input_dim] 节点特征
            edge_index: [2, num_edges] 边索引

        Returns:
            mu: [num_nodes, latent_dim] 均值
            logvar: [num_nodes, latent_dim] 对数方差
        """
        # 第一层GCN
        h = self.conv1(x, edge_index)
        h = self.bn1(h)
        h = F.relu(h)
        h = F.dropout(h, p=0.2, training=self.training)

        # 第二层GCN
        h = self.conv2(h, edge_index)
        h = self.bn2(h)
        h = F.relu(h)

        # 映射到潜在空间
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)

        return mu, logvar

    def reparameterize(self, mu, logvar):
        """
        重参数化技巧：从N(mu, var)中采样

        Args:
            mu: [num_nodes, latent_dim]
            logvar: [num_nodes, latent_dim]

        Returns:
            z: [num_nodes, latent_dim] 采样的潜在向量
        """
        if self.training:
            std = torch.exp(0.5 * logvar)
            eps = torch.randn_like(std)
            return mu + eps * std
        else:
            return mu

    def decode(self, z):
        """
        解码器：潜在向量 -> 邻接矩阵

        Args:
            z: [num_nodes, latent_dim]

        Returns:
            adj_recon: [num_nodes, num_nodes] 重构的邻接矩阵
        """
        # 每个节点独立解码
        h = self.decoder(z)  # [num_nodes, num_nodes]

        # 对称化邻接矩阵
        adj_recon = torch.sigmoid(h)  # [num_nodes, num_nodes]
        adj_recon = (adj_recon + adj_recon.T) / 2

        return adj_recon

    def forward(self, x, edge_index):
        """
        前向传播

        Args:
            x: [num_nodes, input_dim]
            edge_index: [2, num_edges]

        Returns:
            adj_recon: [num_nodes, num_nodes] 重构的邻接矩阵
            mu: [num_nodes, latent_dim] 均值
            logvar: [num_nodes, latent_dim] 对数方差
        """
        mu, logvar = self.encode(x, edge_index)
        z = self.reparameterize(mu, logvar)
        adj_recon = self.decode(z)

        return adj_recon, mu, logvar

    def loss_function(self, adj_recon, adj_true, mu, logvar, beta=0.01):
        """
        VAE损失函数

        Args:
            adj_recon: [num_nodes, num_nodes] 重构的邻接矩阵
            adj_true: [num_nodes, num_nodes] 真实邻接矩阵
            mu: [num_nodes, latent_dim]
            logvar: [num_nodes, latent_dim]
            beta: KL散度权重

        Returns:
            loss: 总损失
            recon_loss: 重构损失
            kl_loss: KL散度损失
        """
        # 重构损失（二元交叉熵）
        recon_loss = F.binary_cross_entropy(adj_recon, adj_true, reduction='sum')
        recon_loss = recon_loss / adj_true.size(0)

        # KL散度损失
        kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
        kl_loss = kl_loss / mu.size(0)

        # 总损失
        loss = recon_loss + beta * kl_loss

        return loss, recon_loss, kl_loss


def build_initial_graph(num_nodes=60, grid_shape=(10, 6)):
    """
    构建初始邻接矩阵（基于网格拓扑）

    Args:
        num_nodes: 节点数量
        grid_shape: 网格形状 (rows, cols)

    Returns:
        edge_index: [2, num_edges]
        edge_weight: [num_edges]
    """
    rows, cols = grid_shape
    edges = []

    for i in range(num_nodes):
        row, col = divmod(i, cols)

        # 上下左右邻居
        neighbors = []
        if row > 0:  # 上
            neighbors.append(i - cols)
        if row < rows - 1:  # 下
            neighbors.append(i + cols)
        if col > 0:  # 左
            neighbors.append(i - 1)
        if col < cols - 1:  # 右
            neighbors.append(i + 1)

        for j in neighbors:
            edges.append([i, j])

    edge_index = torch.tensor(edges, dtype=torch.long).t()
    edge_weight = torch.ones(edge_index.size(1))

    return edge_index, edge_weight


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("GraphVAE模块测试")
    print("=" * 60)

    # 参数设置
    num_nodes = 60
    input_dim = 14  # 14天历史
    hidden_dim = 128
    latent_dim = 32
    batch_size = 1

    # 创建模型
    model = GraphVAE(num_nodes, input_dim, hidden_dim, latent_dim)
    print(f"模型参数量: {sum(p.numel() for p in model.parameters()):,}")

    # 构建初始图
    edge_index, _ = build_initial_graph(num_nodes)

    # 创建随机输入
    x = torch.randn(num_nodes, input_dim)
    adj_true = torch.rand(num_nodes, num_nodes)
    adj_true = (adj_true + adj_true.T) / 2
    adj_true = (adj_true > 0.5).float()

    # 前向传播
    model.train()
    adj_recon, mu, logvar = model(x, edge_index)

    print(f"\n输入形状: {x.shape}")
    print(f"重构邻接矩阵形状: {adj_recon.shape}")
    print(f"潜在均值形状: {mu.shape}")
    print(f"潜在方差形状: {logvar.shape}")

    # 计算损失
    loss, recon_loss, kl_loss = model.loss_function(adj_recon, adj_true, mu, logvar)
    print(f"\n总损失: {loss.item():.4f}")
    print(f"重构损失: {recon_loss.item():.4f}")
    print(f"KL散度: {kl_loss.item():.4f}")

    # 推理模式
    model.eval()
    with torch.no_grad():
        adj_recon_eval, mu_eval, _ = model(x, edge_index)

    print(f"\n推理模式邻接矩阵非零元素: {(adj_recon_eval > 0.5).sum().item()}")

    print("\n✅ GraphVAE模块测试通过")
