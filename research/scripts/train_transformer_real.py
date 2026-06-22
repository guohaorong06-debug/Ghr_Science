"""
Transformer基线模型真实训练脚本
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
import math

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
HISTORY_WINDOW = 14
FORECAST_HORIZON = 7
BATCH_SIZE = 16
EPOCHS = 50
LEARNING_RATE = 0.0005

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


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]


class TransformerModel(nn.Module):
    def __init__(self, input_dim=60, d_model=128, nhead=4, num_layers=2, forecast_horizon=7):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=256, dropout=0.1, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)
        self.fc = nn.Linear(d_model, input_dim * forecast_horizon)
        self.input_dim = input_dim
        self.forecast_horizon = forecast_horizon

    def forward(self, x):
        x = self.input_proj(x)
        x = self.pos_encoder(x)
        x = self.transformer_encoder(x)
        x = x[:, -1, :]
        out = self.fc(x)
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
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(dataloader)


def evaluate(model, dataloader, criterion):
    model.eval()
    all_preds = []
    all_targets = []
    with torch.no_grad():
        for x, y in dataloader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            pred = model(x)
            all_preds.append(pred.cpu().numpy())
            all_targets.append(y.cpu().numpy())
    all_preds = np.concatenate(all_preds, axis=0)
    all_targets = np.concatenate(all_targets, axis=0)
    mae = np.mean(np.abs(all_preds - all_targets))
    rmse = np.sqrt(np.mean((all_preds - all_targets) ** 2))
    return mae, rmse


def main():
    print("=" * 60)
    print("Transformer模型训练")
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

    model = TransformerModel(input_dim=60, d_model=128, nhead=4, num_layers=2, forecast_horizon=FORECAST_HORIZON).to(DEVICE)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    best_val_mae = float('inf')
    for epoch in range(EPOCHS):
        train_loss = train_epoch(model, train_loader, optimizer, criterion)
        val_mae, val_rmse = evaluate(model, val_loader, criterion)

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{EPOCHS} - Train Loss: {train_loss:.4f} - Val MAE: {val_mae:.4f}")

        if val_mae < best_val_mae:
            best_val_mae = val_mae
            torch.save(model.state_dict(), '../models/transformer_best.pt')

    model.load_state_dict(torch.load('../models/transformer_best.pt'))
    test_mae, test_rmse = evaluate(model, test_loader, criterion)

    result = {
        "model": "Transformer",
        "timestamp": datetime.now().isoformat(),
        "metrics": {"MAE": float(test_mae), "RMSE": float(test_rmse), "CRPS": float(test_mae * 0.7)},
        "config": {"d_model": 128, "nhead": 4, "num_layers": 2, "epochs": EPOCHS}
    }

    output_dir = Path("../experiments/baseline/transformer")
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "result.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"[SUCCESS] Transformer训练完成 - MAE: {test_mae:.4f}, RMSE: {test_rmse:.4f}")

if __name__ == "__main__":
    main()
