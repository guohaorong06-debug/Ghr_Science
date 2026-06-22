# 智能物流需求概率预测 - 研究代码

本目录包含完整的科研实验代码，用于支撑论文写作和模型训练。

## 📂 目录结构

```
research/
├── data/
│   ├── raw/              # 原始NYC TLC数据
│   ├── processed/        # 预处理后的网格化数据
│   └── metadata.json     # 数据集描述
├── experiments/
│   ├── baseline/         # 15+基线模型实验结果
│   └── proposed/         # 创新模型实验结果
├── models/
│   ├── checkpoints/      # 训练检查点
│   └── final/            # 最终模型（TorchScript）
├── outputs/
│   ├── figures/          # 论文图表
│   ├── tables/           # LaTeX表格
│   └── logs/             # 训练日志
├── scripts/
│   ├── 1_download_data.py       # 数据下载
│   ├── 2_preprocess.py          # 数据预处理
│   ├── 3_train_baseline.py      # 基线模型训练
│   ├── 4_train_proposed.py      # 创新模型训练
│   ├── 5_evaluate_all.py        # 统一评估
│   └── 6_generate_plots.py      # 生成论文图表
├── notebooks/            # Jupyter探索性分析
├── requirements.txt      # Python依赖
└── README.md            # 本文件
```

## 🚀 快速开始

### 1. 创建Python虚拟环境

```bash
conda create -n logistics python=3.10
conda activate logistics
pip install -r requirements.txt
```

### 2. 下载数据

```bash
cd scripts
python 1_download_data.py
```

**注意**: NYC TLC完整数据约100GB+，建议：
- 先下载2019-2022年数据（约30GB）
- 使用外置硬盘或云存储

### 3. 数据预处理

```bash
python 2_preprocess.py
```

输出：`data/processed/demand_grid.csv` (60个网格的每日需求量)

### 4. 训练基线模型

```bash
python 3_train_baseline.py
```

自动运行15+基线模型并保存结果到 `experiments/baseline/`

### 5. 训练创新模型

```bash
python 4_train_proposed.py
```

训练图变分自编码器+标准化流模型

### 6. 生成对比结果

```bash
python 5_evaluate_all.py
python 6_generate_plots.py
```

输出论文图表到 `outputs/figures/`

## 📊 实验结果格式

每个实验结果保存为JSON：

```json
{
  "model": "ProposedModel_GraphVAE_NormalizingFlow",
  "timestamp": "2026-06-22T12:00:00",
  "metrics": {
    "MAE": 42.15,
    "RMSE": 65.23,
    "CRPS": 28.67,
    "PICP_90": 0.924,
    "MPIW_90": 118.45
  },
  "training_time_seconds": 3200,
  "comparison": {
    "best_baseline": "DeepAR",
    "improvement_MAE": "15.3%",
    "improvement_CRPS": "22.7%"
  }
}
```

## 📖 论文相关

### 评估指标

- **MAE** (Mean Absolute Error): 平均绝对误差
- **RMSE** (Root Mean Square Error): 均方根误差
- **CRPS** (Continuous Ranked Probability Score): 概率预测精度
- **PICP** (Prediction Interval Coverage Probability): 区间覆盖率
- **MPIW** (Mean Prediction Interval Width): 平均区间宽度

### 基线模型列表

1. ARIMA
2. Prophet
3. LSTM
4. GRU
5. Transformer
6. Informer
7. Autoformer
8. DCRNN
9. STGCN
10. Graph WaveNet
11. DeepAR
12. MQ-CNN
13. Variational Transformer
14. CSDI
15. TFT (Temporal Fusion Transformer)

### 创新点

1. **自适应异质性图生成**: 图变分自编码器动态建模空间依赖
2. **时变不确定性估计**: 条件标准化流实现非对称多模态分布
3. **决策感知损失**: 高分位数加权优化资源配置
4. **可解释性**: GNNExplainer追溯预警来源

## 🔧 开发注意事项

### GPU加速

```python
# 检查CUDA可用性
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
```

### 实验追踪

所有实验结果自动保存到 `experiments/`，包含：
- 模型配置
- 训练超参数
- 评估指标
- 时间戳

### 模型导出

训练完成后导出TorchScript用于Java后端：

```python
script_model = torch.jit.script(model)
script_model.save("models/final/demand-forecast.pt")
```

## 📝 TODO

- [ ] 实现完整的GraphVAE网络结构
- [ ] 实现NormalizingFlow可逆层
- [ ] 实现决策感知损失函数
- [ ] 集成GNNExplainer可解释性
- [ ] 添加消融实验脚本
- [ ] 实现Diebold-Mariano统计检验
- [ ] 绘制论文级图表（Matplotlib）
- [ ] 生成LaTeX表格代码

## 📧 联系方式

项目仓库: https://github.com/guohaorong06-debug/Ghr_Science
