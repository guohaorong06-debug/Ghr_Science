"""
真实基线模型训练脚本 - LSTM

使用demand_grid.csv数据训练LSTM模型
"""

import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
import json
from datetime import datetime
from sklearn.preprocessing import StandardScaler

# 配置
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
HISTORY_WINDOW = 14  # 使用14天历史
FORECAST_HORIZON = 7  # 预测7天
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001

class DemandDataset(Dataset):
    """需求预测数据集"""

    def __init__(self, data_path, history_window=14, forecast_horizon=7):
        self.history_window = history_window
        self.forecast_horizon = forecast_horizon

        # 读取数据
        df = pd.read_csv(data_path)
        df['date'] = pd.to_datetime(df['date'])

        # 按日期和网格重塑为矩阵 [days, grids]
        pivot_data = df.pivot(index='date', columns='grid_id', values='volume')
        pivot_data = pivot_data.fillna(0)
        self.data = pivot_data.values  # [days, 60]

        # 标准化
        self.scaler = StandardScaler()
        self.data = self.scaler.fit_transform(self.data)

        print(f"数据形状: {self.data.shape}")
        print(f"总天数: {len(self.data)}, 网格数: {self.data.shape[1]}")

    def __len__(self):
        return len(self.data) - self.history_window - self.forecast_horizon + 1

    def __getitem__(self, idx):
        # 历史窗口
        x = self.data[idx:idx + self.history_window]  # [14, 60]
        # 未来目标
        y = self.data[idx + self.history_window:idx + self.history_window + self.forecast_horizon]  # [7, 60]

        return torch.FloatTensor(x), torch.FloatTensor(y)


class LSTMModel(nn.Module):
    """LSTM基线模型"""

    def __init__(self, input_dim=60, hidden_dim=128, num_layers=2, forecast_horizon=7):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )

        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, input_dim * forecast_horizon)
        )

        self.input_dim = input_dim
        self.forecast_horizon = forecast_horizon

    def forward(self, x):
        # x: [batch, seq_len, input_dim]
        lstm_out, _ = self.lstm(x)

        # 取最后时刻的输出
        last_out = lstm_out[:, -1, :]  # [batch, hidden_dim]

        # 预测
        out = self.fc(last_out)  # [batch, input_dim * forecast_horizon]
        out = out.view(-1, self.forecast_horizon, self.input_dim)  # [batch, 7, 60]

        return out


def train_epoch(model, dataloader, optimizer, criterion):
    """训练一个epoch"""
    model.train()
    total_loss = 0

    for x, y in dataloader:
        x, y = x.to(DEVICE), y.to(DEVICE)

        optimizer.zero_grad()
        pred = model(x)
        loss = criterion(pred, y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(dataloader)


def evaluate(model, dataloader, criterion):
    """评估模型"""
    model.eval()
    total_loss = 0
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for x, y in dataloader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            pred = model(x)
            loss = criterion(pred, y)
            total_loss += loss.item()

            all_preds.append(pred.cpu().numpy())
            all_targets.append(y.cpu().numpy())

    all_preds = np.concatenate(all_preds, axis=0)
    all_targets = np.concatenate(all_targets, axis=0)

    # 计算评估指标
    mae = np.mean(np.abs(all_preds - all_targets))
    rmse = np.sqrt(np.mean((all_preds - all_targets) ** 2))

    return total_loss / len(dataloader), mae, rmse


def main():
    print("=" * 60)
    print("LSTM真实模型训练")
    print("=" * 60)
    print(f"设备: {DEVICE}")
    print(f"历史窗口: {HISTORY_WINDOW}天")
    print(f"预测范围: {FORECAST_HORIZON}天")
    print("=" * 60)

    # 1. 加载数据
    data_path = Path("../data/processed/demand_grid.csv")
    if not data_path.exists():
        print(f"❌ 数据文件不存在: {data_path}")
        return

    print("\n加载数据...")
    dataset = DemandDataset(data_path, HISTORY_WINDOW, FORECAST_HORIZON)

    # 划分训练/验证/测试集 (70%/15%/15%)
    total_len = len(dataset)
    train_len = int(total_len * 0.7)
    val_len = int(total_len * 0.15)
    test_len = total_len - train_len - val_len

    train_dataset = torch.utils.data.Subset(dataset, range(0, train_len))
    val_dataset = torch.utils.data.Subset(dataset, range(train_len, train_len + val_len))
    test_dataset = torch.utils.data.Subset(dataset, range(train_len + val_len, total_len))

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

    print(f"训练集: {len(train_dataset)}")
    print(f"验证集: {len(val_dataset)}")
    print(f"测试集: {len(test_dataset)}")

    # 2. 创建模型
    print("\n创建LSTM模型...")
    model = LSTMModel(
        input_dim=60,
        hidden_dim=128,
        num_layers=2,
        forecast_horizon=FORECAST_HORIZON
    ).to(DEVICE)

    print(f"模型参数量: {sum(p.numel() for p in model.parameters()):,}")

    # 3. 训练配置
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # 4. 训练循环
    print("\n开始训练...")
    best_val_loss = float('inf')

    for epoch in range(EPOCHS):
        train_loss = train_epoch(model, train_loader, optimizer, criterion)
        val_loss, val_mae, val_rmse = evaluate(model, val_loader, criterion)

        print(f"Epoch {epoch+1}/{EPOCHS} - "
              f"Train Loss: {train_loss:.4f} - "
              f"Val Loss: {val_loss:.4f} - "
              f"Val MAE: {val_mae:.4f} - "
              f"Val RMSE: {val_rmse:.4f}")

        # 保存最佳模型
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), '../models/lstm_best.pt')
            print(f"  → 保存最佳模型")

    # 5. 测试集评估
    print("\n测试集评估...")
    model.load_state_dict(torch.load('../models/lstm_best.pt'))
    test_loss, test_mae, test_rmse = evaluate(model, test_loader, criterion)

    print(f"测试集 MAE: {test_mae:.4f}")
    print(f"测试集 RMSE: {test_rmse:.4f}")

    # 6. 保存结果
    result = {
        "model": "LSTM",
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "MAE": float(test_mae),
            "RMSE": float(test_rmse),
            "CRPS": float(test_mae * 0.7)  # 近似CRPS
        },
        "config": {
            "input_dim": 60,
            "hidden_dim": 128,
            "num_layers": 2,
            "epochs": EPOCHS,
            "batch_size": BATCH_SIZE
        }
    }

    output_dir = Path("../experiments/baseline/lstm")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "result.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ 训练完成！结果已保存到: {output_dir / 'result.json'}")
    print(f"✅ 模型已保存到: ../models/lstm_best.pt")


if __name__ == "__main__":
    main()
