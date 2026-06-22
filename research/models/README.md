# 模型模块

这个目录包含创新模型的所有组件。

## 文件说明

### 核心模型
- `graph_vae.py` - 图变分自编码器（空间依赖建模）
- `normalizing_flow.py` - 条件标准化流（概率分布生成）
- `proposed_model.py` - 完整的集成模型

### 使用方法

```python
from models.proposed_model import create_model

# 创建模型
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

# 前向传播
outputs = model(x_history, edge_index, external_features)

# 计算损失
loss_dict = model.compute_loss(outputs, targets, adj_true, capacity_threshold)
```

## 模型特点

### 1. GraphVAE
- 基于GCN的变分编码器
- 动态生成空间依赖图
- 支持60个节点（物流网格）

### 2. Normalizing Flow
- 8层仿射耦合层
- 条件化非对称分布
- 可逆变换保证可采样

### 3. 决策感知损失
- CRPS主损失
- 分位数辅助损失  
- 业务导向资源错配惩罚
- False Negative加权3倍

## 创新点

1. **自适应异质性图生成** - GraphVAE动态学习网点关联
2. **时变不确定性估计** - Normalizing Flow生成非对称分布
3. **决策感知优化** - 直接最小化资源错配成本
4. **端到端概率预测** - 输出完整的预测分布

## 测试

每个模块都包含独立测试代码：

```bash
python models/graph_vae.py
python models/normalizing_flow.py
python models/proposed_model.py
```
