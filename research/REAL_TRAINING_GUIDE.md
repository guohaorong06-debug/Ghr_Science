# 真实模型训练 - 快速开始指南

## 🚀 立即开始训练

### 方式1：训练LSTM基线模型（推荐先运行）

```bash
# 1. 激活环境
conda activate logistics

# 2. 进入脚本目录
cd D:\Ghr_Science\research\scripts

# 3. 运行LSTM训练（约10-20分钟）
python train_lstm_real.py
```

**预期输出**：
- ✅ 训练50个epoch
- ✅ 生成 `../models/lstm_best.pt`
- ✅ 生成 `../experiments/baseline/lstm/result.json`
- ✅ 显示真实的MAE/RMSE指标

---

### 方式2：训练创新模型（GraphVAE + Flow）

```bash
# 继续在同一目录
python train_proposed_real.py
```

**预期输出**：
- ✅ 训练100个epoch（约30-60分钟）
- ✅ 生成 `../models/proposed_best.pt`
- ✅ 生成 `../experiments/proposed/result.json`
- ✅ 使用真实的GraphVAE和Normalizing Flow

---

## 📋 训练前检查

### 必需文件
```
✅ research/data/processed/demand_grid.csv (已有)
✅ research/models/graph_vae.py (已有)
✅ research/models/normalizing_flow.py (已有)
✅ research/models/proposed_model.py (已有)
✅ research/scripts/train_lstm_real.py (新建)
✅ research/scripts/train_proposed_real.py (新建)
```

### 依赖检查
```bash
# 检查PyTorch
python -c "import torch; print(torch.__version__)"

# 如果缺少依赖，安装
pip install torch pandas numpy scikit-learn
```

---

## ⚙️ 训练配置

### LSTM配置
```python
HISTORY_WINDOW = 14  # 使用14天历史
FORECAST_HORIZON = 7  # 预测7天
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001
```

### Proposed Model配置
```python
HISTORY_WINDOW = 14
FORECAST_HORIZON = 7
BATCH_SIZE = 16  # 更小因为模型更复杂
EPOCHS = 100
LEARNING_RATE = 0.001
```

---

## 📊 预期结果

### LSTM模型
```
训练集: ~850个样本
验证集: ~180个样本
测试集: ~180个样本

模型参数量: ~2,000,000

预期指标:
  MAE: 40-60
  RMSE: 60-90
```

### Proposed Model
```
训练集: ~850个样本
验证集: ~180个样本
测试集: ~180个样本

模型参数量: ~2,500,000

预期指标:
  MAE: 35-55 (应该比LSTM更好)
  RMSE: 55-85
```

---

## 🐛 常见问题

### Q1: CUDA不可用？
```bash
# 训练会自动使用CPU，速度慢但可用
# 如需GPU加速，安装CUDA版本PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Q2: 内存不足？
```python
# 减小batch_size
BATCH_SIZE = 8  # 或更小
```

### Q3: 训练时间太长？
```python
# 减少epochs
EPOCHS = 20  # LSTM
EPOCHS = 50  # Proposed
```

---

## ✅ 训练完成后

### 检查输出文件
```bash
# LSTM
ls ../models/lstm_best.pt
ls ../experiments/baseline/lstm/result.json

# Proposed Model
ls ../models/proposed_best.pt
ls ../experiments/proposed/result.json
```

### 查看结果
```bash
# 查看LSTM结果
cat ../experiments/baseline/lstm/result.json

# 查看Proposed结果
cat ../experiments/proposed/result.json
```

---

## 🎯 下一步

### 1. 对比结果
```bash
python 5_evaluate_all.py  # 生成对比表格
```

### 2. 生成图表
```bash
python 6_generate_plots.py  # 生成论文图表
```

### 3. 导出模型供Java使用
```python
# 添加到训练脚本末尾
script_model = torch.jit.script(model)
script_model.save('../models/lstm_script.pt')
```

---

## 🎊 快速开始命令（复制粘贴）

```bash
# 一次性运行所有训练
conda activate logistics
cd D:\Ghr_Science\research\scripts

# 训练LSTM（10-20分钟）
python train_lstm_real.py

# 训练Proposed（30-60分钟）
python train_proposed_real.py

# 查看结果
echo "LSTM结果:"
cat ../experiments/baseline/lstm/result.json
echo ""
echo "Proposed结果:"
cat ../experiments/proposed/result.json
```

---

**准备完成！现在可以开始真实训练了！** 🚀
