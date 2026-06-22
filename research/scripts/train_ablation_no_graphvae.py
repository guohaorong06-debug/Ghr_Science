"""
消融实验：训练不带GraphVAE的模型
"""

import sys
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
import json
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

sys.path.append(str(Path(__file__).parent.parent))

# 简化版模型（移除GraphVAE）
class ProposedWithoutGraphVAE(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

        # 1. 时序编码器（LSTM代替GraphVAE）
        self.temporal_encoder = nn.LSTM(
            input_size=config['num_nodes'],
            hidden_size=config['hidden_dim'],
            num_layers=2,
            batch_first=True
        )

        # 2. Normalizing Flow（保留）
        from models.normalizing_flow import NormalizingFlow
        self.normalizing_flow = NormalizingFlow(
            input_dim=config['forecast_horizon'],
            context_dim=config['context_dim'],
            num_flows=config['num_flows']
        )

        # 3. 上下文编码
        self.context_encoder = nn.Sequential(
            nn.Linear(config['hidden_dim'] + config['external_dim'], config['context_dim']),
            nn.ReLU(),
            nn.Linear(config['context_dim'], config['context_dim'])
        )

        # 4. 分位数预测头
        self.quantile_head = nn.Linear(config['context_dim'], config['forecast_horizon'] * 3)

    def forward(self, x_history, external_features):
        batch_size = x_history.size(0)

        # LSTM编码
        lstm_out, _ = self.temporal_encoder(x_history)
        temporal_features = lstm_out[:, -1, :]

        # 上下文
        combined = torch.cat([temporal_features, external_features], dim=-1)
        context = self.context_encoder(combined)

        # 分位数
        quantile_preds = self.quantile_head(context)
        quantile_preds = quantile_preds.view(batch_size, self.config['forecast_horizon'], 3)

        # Normalizing Flow采样
        num_samples = 5 if self.training else 100
        samples = self.normalizing_flow.sample(context, num_samples=num_samples)

        p10 = torch.quantile(samples, 0.1, dim=1)
        p50 = torch.quantile(samples, 0.5, dim=1)
        p90 = torch.quantile(samples, 0.9, dim=1)

        return {
            'p10': p10,
            'p50': p50,
            'p90': p90,
            'quantile_preds': quantile_preds,
            'samples': samples
        }


# 数据集（简化版）
class DemandDataset(Dataset):
    def __init__(self, data_path, history_window=14, forecast_horizon=7):
        self.history_window = history_window
        self.forecast_horizon = forecast_horizon
        df = pd.read_csv(data_path)
        df['date'] = pd.to_datetime(df['date'])
        pivot_data = df.pivot(index='date', columns='grid_id', values='volume')
        pivot_data = pivot_data.fillna(0)
        self.data = pivot_data.values
        self.scaler = StandardScaler()
        self.data = self.scaler.fit_transform(self.data)

    def __len__(self):
        return len(self.data) - self.history_window - self.forecast_horizon + 1

    def __getitem__(self, idx):
        x = self.data[idx:idx + self.history_window]
        y = self.data[idx + self.history_window:idx + self.history_window + self.forecast_horizon]
        return torch.FloatTensor(x), torch.FloatTensor(y)


def evaluate(model, dataloader):
    model.eval()
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for x, y in tqdm(dataloader, desc='Evaluating', leave=False):
            x, y = x.cuda(), y.cuda()
            external_features = torch.zeros(x.size(0), 10, device='cuda')
            outputs = model(x, external_features)
            pred = outputs['p50'].cpu().numpy()
            target = y.mean(dim=2).cpu().numpy()
            all_preds.append(pred)
            all_targets.append(target)

    all_preds = np.concatenate(all_preds, axis=0)
    all_targets = np.concatenate(all_targets, axis=0)
    mae = np.mean(np.abs(all_preds - all_targets))
    rmse = np.sqrt(np.mean((all_preds - all_targets) ** 2))
    return mae, rmse


def main():
    print("=" * 60)
    print("消融实验：Proposed w/o GraphVAE")
    print("=" * 60)

    data_path = Path("../data/processed/demand_grid.csv")
    dataset = DemandDataset(data_path, 14, 7)

    total_len = len(dataset)
    train_len = int(total_len * 0.7)
    val_len = int(total_len * 0.15)

    train_dataset = torch.utils.data.Subset(dataset, range(0, train_len))
    val_dataset = torch.utils.data.Subset(dataset, range(train_len, train_len + val_len))
    test_dataset = torch.utils.data.Subset(dataset, range(train_len + val_len, total_len))

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32)

    config = {
        'num_nodes': 60,
        'history_window': 14,
        'forecast_horizon': 7,
        'hidden_dim': 128,
        'context_dim': 64,
        'external_dim': 10,
        'num_flows': 8
    }

    model = ProposedWithoutGraphVAE(config).cuda()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    print("\n快速训练（10 epochs）...")
    for epoch in range(10):
        model.train()
        for x, y in train_loader:
            x, y = x.cuda(), y.cuda()
            external_features = torch.zeros(x.size(0), 10, device='cuda')
            outputs = model(x, external_features)
            loss = criterion(outputs['p50'], y.mean(dim=2))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1}/10")

    test_mae, test_rmse = evaluate(model, test_loader)

    result = {
        "model": "Proposed_without_GraphVAE",
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "MAE": float(test_mae),
            "RMSE": float(test_rmse)
        }
    }

    output_dir = Path("../experiments/ablation")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "without_graphvae.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n[SUCCESS] 测试集 MAE: {test_mae:.4f}, RMSE: {test_rmse:.4f}")


if __name__ == "__main__":
    main()
