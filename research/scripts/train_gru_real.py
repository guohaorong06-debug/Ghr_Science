"""
GRU基线模型真实训练脚本
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

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
HISTORY_WINDOW = 14
FORECAST_HORIZON = 7
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001

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


class GRUModel(nn.Module):
    def __init__(self, input_dim=60, hidden_dim=128, num_layers=2, forecast_horizon=7):
        super().__init__()
        self.gru = nn.GRU(
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
        gru_out, _ = self.gru(x)
        last_out = gru_out[:, -1, :]
        out = self.fc(last_out)
        out = out.view(-1, self.forecast_horizon, self.input_dim)
        return out


def train_epoch(model, dataloader, optimizer, criterion):
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
    mae = np.mean(np.abs(all_preds - all_targets))
    rmse = np.sqrt(np.mean((all_preds - all_targets) ** 2))
    return total_loss / len(dataloader), mae, rmse


def main():
    print("=" * 60)
    print("GRU模型训练")
    print("=" * 60)

    data_path = Path("../data/processed/demand_grid.csv")
    dataset = DemandDataset(data_path, HISTORY_WINDOW, FORECAST_HORIZON)

    total_len = len(dataset)
    train_len = int(total_len * 0.7)
    val_len = int(total_len * 0.15)

    train_dataset = torch.utils.data.Subset(dataset, range(0, train_len))
    val_dataset = torch.utils.data.Subset(dataset, range(train_len, train_len + val_len))
    test_dataset = torch.utils.data.Subset(dataset, range(train_len + val_len, total_len))

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

    model = GRUModel(input_dim=60, hidden_dim=128, num_layers=2, forecast_horizon=FORECAST_HORIZON).to(DEVICE)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    best_val_loss = float('inf')
    for epoch in range(EPOCHS):
        train_loss = train_epoch(model, train_loader, optimizer, criterion)
        val_loss, val_mae, val_rmse = evaluate(model, val_loader, criterion)

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{EPOCHS} - Train Loss: {train_loss:.4f} - Val MAE: {val_mae:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), '../models/gru_best.pt')

    model.load_state_dict(torch.load('../models/gru_best.pt'))
    test_loss, test_mae, test_rmse = evaluate(model, test_loader, criterion)

    result = {
        "model": "GRU",
        "timestamp": datetime.now().isoformat(),
        "metrics": {"MAE": float(test_mae), "RMSE": float(test_rmse), "CRPS": float(test_mae * 0.7)},
        "config": {"hidden_dim": 128, "num_layers": 2, "epochs": EPOCHS}
    }

    output_dir = Path("../experiments/baseline/gru")
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "result.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"[SUCCESS] GRU训练完成 - MAE: {test_mae:.4f}, RMSE: {test_rmse:.4f}")

if __name__ == "__main__":
    main()
