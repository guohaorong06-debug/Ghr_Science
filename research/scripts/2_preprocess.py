"""
数据预处理：将出租车数据转换为网格化需求数据

输入: data/raw/*.parquet (NYC TLC原始数据)
输出: data/processed/demand_grid.csv (60个网格的每日需求量)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json

# 配置
RAW_DIR = Path("../data/raw")
PROCESSED_DIR = Path("../data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# 曼哈顿边界（经纬度）
MANHATTAN_BOUNDS = {
    'lon_min': -74.02,
    'lon_max': -73.93,
    'lat_min': 40.70,
    'lat_max': 40.88
}

# 网格划分（6x10 = 60个网格）
GRID_ROWS = 10
GRID_COLS = 6

def assign_grid(lon, lat):
    """将经纬度分配到网格ID (0-59)"""
    if not (MANHATTAN_BOUNDS['lon_min'] <= lon <= MANHATTAN_BOUNDS['lon_max'] and
            MANHATTAN_BOUNDS['lat_min'] <= lat <= MANHATTAN_BOUNDS['lat_max']):
        return None

    lon_range = MANHATTAN_BOUNDS['lon_max'] - MANHATTAN_BOUNDS['lon_min']
    lat_range = MANHATTAN_BOUNDS['lat_max'] - MANHATTAN_BOUNDS['lat_min']

    col = int((lon - MANHATTAN_BOUNDS['lon_min']) / lon_range * GRID_COLS)
    row = int((lat - MANHATTAN_BOUNDS['lat_min']) / lat_range * GRID_ROWS)

    col = min(col, GRID_COLS - 1)
    row = min(row, GRID_ROWS - 1)

    return row * GRID_COLS + col

def process_file(filepath):
    """处理单个Parquet文件"""
    try:
        df = pd.read_parquet(filepath)

        # 过滤并提取关键列
        df = df[['tpep_pickup_datetime', 'pickup_longitude', 'pickup_latitude']].copy()
        df.columns = ['datetime', 'lon', 'lat']

        # 转换日期
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['date'] = df['datetime'].dt.date

        # 分配网格
        df['grid_id'] = df.apply(lambda row: assign_grid(row['lon'], row['lat']), axis=1)
        df = df.dropna(subset=['grid_id'])
        df['grid_id'] = df['grid_id'].astype(int)

        # 按日期和网格统计
        daily_demand = df.groupby(['date', 'grid_id']).size().reset_index(name='volume')

        return daily_demand

    except Exception as e:
        print(f"❌ 处理失败 {filepath.name}: {e}")
        return None

def main():
    print("=" * 60)
    print("数据预处理：网格化需求统计")
    print("=" * 60)

    parquet_files = sorted(RAW_DIR.glob("*.parquet"))
    print(f"发现文件: {len(parquet_files)} 个")

    all_demands = []

    for filepath in tqdm(parquet_files, desc="处理文件"):
        demand = process_file(filepath)
        if demand is not None:
            all_demands.append(demand)

    # 合并所有数据
    print("\n合并数据...")
    final_df = pd.concat(all_demands, ignore_index=True)

    # 填充缺失日期（某些网格某天可能无数据）
    print("填充缺失日期...")
    date_range = pd.date_range(start=final_df['date'].min(), end=final_df['date'].max(), freq='D')
    grid_ids = range(60)

    full_index = pd.MultiIndex.from_product([date_range, grid_ids], names=['date', 'grid_id'])
    final_df = final_df.set_index(['date', 'grid_id']).reindex(full_index, fill_value=0).reset_index()

    # 保存
    output_path = PROCESSED_DIR / "demand_grid.csv"
    final_df.to_csv(output_path, index=False)
    print(f"\n✅ 保存成功: {output_path}")
    print(f"   数据形状: {final_df.shape}")
    print(f"   日期范围: {final_df['date'].min()} 至 {final_df['date'].max()}")
    print(f"   网格数量: {final_df['grid_id'].nunique()}")

    # 统计信息
    stats = {
        "total_records": len(final_df),
        "date_range": [str(final_df['date'].min()), str(final_df['date'].max())],
        "grid_count": 60,
        "mean_volume": float(final_df['volume'].mean()),
        "std_volume": float(final_df['volume'].std()),
        "max_volume": int(final_df['volume'].max()),
        "min_volume": int(final_df['volume'].min())
    }

    with open(PROCESSED_DIR / "stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    print("\n统计信息:")
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
