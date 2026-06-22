# 模型训练快速指南

**开始时间**: 2026-06-22  
**预计时间**: 首次训练约2-4小时（取决于数据量和GPU）

---

## 📋 完整操作步骤

### 步骤0：环境准备（10分钟）

```bash
# 1. 创建Python环境
conda create -n logistics python=3.10
conda activate logistics

# 2. 安装依赖
cd D:\Ghr_Science\research
pip install -r requirements.txt

# 3. 验证PyTorch和CUDA
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
```

---

### 步骤1：下载NYC数据（30-60分钟）

```bash
cd scripts
python 1_download_data.py
```

**说明**：
- 自动下载2019-2022年NYC出租车数据
- 数据大小：约30GB
- 保存位置：`data/raw/`
- 进度条显示下载进度

**注意**：
- 需要稳定网络连接
- 如果下载中断，重新运行会自动跳过已下载文件

---

### 步骤2：数据预处理（20-40分钟）

```bash
python 2_preprocess.py
```

**功能**：
- 读取Parquet文件
- 将经纬度转换为6x10网格（60个网格）
- 按日期统计每个网格的包裹量
- 输出：`data/processed/demand_grid.csv`

**输出示例**：
```csv
date,grid_id,volume
2019-01-01,0,850
2019-01-01,1,920
2019-01-01,2,1100
...
```

---

### 步骤3：训练基线模型（1-2小时）

```bash
python 3_train_baseline.py
```

**说明**：
- 自动训练15+基线模型
- 包括：ARIMA, Prophet, LSTM, GRU, Transformer, DeepAR等
- 每个模型训练2-8分钟
- 结果保存到：`experiments/baseline/results.json`

**进度提示**：
```
✅ ARIMA 完成 (MAE: 45.23, CRPS: 32.45)
✅ Prophet 完成 (MAE: 48.12, CRPS: 35.67)
✅ LSTM 完成 (MAE: 42.89, CRPS: 30.21)
...
```

---

### 步骤4：训练创新模型（30-60分钟）

```bash
python 4_train_proposed.py
```

**说明**：
- 训练GraphVAE + NormalizingFlow模型
- 使用GPU加速（如果可用）
- 自动保存最佳模型检查点
- 输出：`experiments/proposed/result.json`

**训练监控**：
```
Epoch 1/100: Loss=0.4523, CRPS=28.67
Epoch 10/100: Loss=0.3421, CRPS=25.34
Best model saved at epoch 87
```

---

### 步骤5：统一评估（5分钟）

```bash
python 5_evaluate_all.py
```

**功能**：
- 读取所有实验结果
- 生成对比表格（CSV + LaTeX）
- 计算相对改进百分比
- 输出排行榜

**输出示例**：
```
模型对比表 (按CRPS排序)
==================================================
Rank  Model              MAE     RMSE    CRPS
--------------------------------------------------
1     ProposedModel      42.15   65.23   28.67  ⭐
2     DeepAR             48.56   72.31   32.45
3     LSTM               50.23   75.89   35.67
...
```

---

### 步骤6：生成论文图表（5分钟）

```bash
python 6_generate_plots.py
```

**输出**：
- `outputs/figures/model_comparison_bar.png` - 模型对比柱状图
- `outputs/figures/forecast_waterfall.png` - 预测瀑布图
- `outputs/figures/reliability_diagram.png` - 可靠性校准图

所有图表300 DPI，适合论文投稿。

---

## 🎯 关键输出文件

### 实验结果
```
experiments/
├── baseline/
│   ├── results.json          # 所有基线模型结果
│   ├── arima/
│   ├── lstm/
│   └── ...
└── proposed/
    └── result.json            # 创新模型结果
```

### 论文素材
```
outputs/
├── figures/                   # 论文图表（PNG + PDF）
│   ├── model_comparison_bar.png
│   ├── forecast_waterfall.png
│   └── reliability_diagram.png
├── tables/                    # 对比表格
│   ├── model_comparison.csv
│   ├── model_comparison.tex
│   └── improvements.json
└── logs/                      # 训练日志
```

### 模型权重
```
models/
├── checkpoints/               # 训练检查点
└── final/
    └── demand-forecast.pt     # 最终TorchScript模型（用于Java后端）
```

---

## 📊 实验结果格式

所有结果保存为JSON格式，便于Claude读取用于论文写作：

```json
{
  "model": "ProposedModel_GraphVAE_NormalizingFlow",
  "timestamp": "2026-06-22T16:00:00",
  "config": {
    "num_nodes": 60,
    "hidden_dim": 128,
    "latent_dim": 32
  },
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

---

## ⚙️ 高级配置（可选）

### 使用GPU训练

```python
# 在训练脚本中已自动配置
device = "cuda" if torch.cuda.is_available() else "cpu"
```

### 调整超参数

修改 `4_train_proposed.py` 中的配置：
```python
config = {
    "num_nodes": 60,
    "hidden_dim": 128,      # 可调整为64, 256
    "latent_dim": 32,       # 可调整为16, 64
    "learning_rate": 1e-3,  # 可调整为1e-4, 5e-4
    "epochs": 100,          # 可调整为50, 200
    "batch_size": 32        # 可调整为16, 64
}
```

### 使用更多数据

修改 `1_download_data.py`：
```python
YEARS = range(2010, 2023)  # 扩展到2010-2022年（更大数据集）
```

---

## 🐛 常见问题

### Q1: CUDA不可用？
```bash
# 安装CUDA版本的PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Q2: 内存不足？
- 减小batch_size
- 减小hidden_dim
- 使用更少的历史数据

### Q3: 下载速度慢？
- 使用代理
- 分批下载（修改YEARS范围）

### Q4: 训练时间太长？
- 使用GPU
- 减少epochs
- 减小模型规模

---

## 🎓 完成训练后

### 集成到Java后端

1. **找到导出的模型文件**：
   ```
   models/final/demand-forecast.pt
   ```

2. **复制到Docker容器**：
   ```bash
   docker cp models/final/demand-forecast.pt logistics-backend:/app/models/
   ```

3. **在前端上传新模型**：
   - 访问 http://localhost
   - 进入"模型管理"页面
   - 上传 `.pt` 文件
   - 点击"激活"

4. **测试真实预测**：
   - 进入"需求预测"页面
   - 选择网点和日期
   - 查看真实模型的预测结果

---

## 📝 论文写作支持

训练完成后，使用Claude + Zotero + MATLAB：

```bash
# 1. Claude读取实验结果
cat experiments/baseline/results.json
cat experiments/proposed/result.json

# 2. 自动生成论文草稿
# Claude会根据JSON数据生成各章节

# 3. MATLAB绘制专业图表
# 使用MATLAB MCP工具

# 4. Zotero管理文献
# 使用Zotero MCP工具
```

---

## 🎉 开始训练

现在你可以开始了：

```bash
conda activate logistics
cd D:\Ghr_Science\research\scripts
python 1_download_data.py
```

**预计总耗时**: 3-5小时（首次完整运行）

**祝训练顺利！** 🚀
