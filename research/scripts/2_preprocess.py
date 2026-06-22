"""
数据预处理：将出租车数据转换为网格化需求数据
支持新旧两种格式：
- 旧格式：含 pickup_longitude / pickup_latitude
- 新格式：含 PULocationID（通过内置映射转换为经纬度）

修正：增加了日期范围过滤（2018-2023年），避免异常日期
"""

import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json

# ---------- 配置 ----------
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

GRID_ROWS = 10
GRID_COLS = 6

# 有效年份范围（过滤异常日期）
MIN_YEAR = 2018
MAX_YEAR = 2023

# ---------- 内置 LocationID -> (lon, lat) 映射（曼哈顿区域中心） ----------
LOCATION_CENTROIDS = {
    # 曼哈顿上城 (Upper Manhattan)
    238: (-73.938, 40.865),  # Washington Heights
    239: (-73.937, 40.845),  # Inwood
    240: (-73.939, 40.825),  # Hamilton Heights
    241: (-73.946, 40.810),  # Manhattanville
    242: (-73.948, 40.795),  # Morningside Heights
    243: (-73.950, 40.780),  # Harlem
    244: (-73.952, 40.770),  # East Harlem
    245: (-73.955, 40.755),  # Upper East Side
    246: (-73.960, 40.745),  # Upper West Side
    # 中城 (Midtown)
    247: (-73.970, 40.735),  # Clinton
    248: (-73.972, 40.725),  # Midtown
    249: (-73.975, 40.715),  # Murray Hill
    250: (-73.978, 40.705),  # Gramercy
    251: (-73.982, 40.695),  # East Village
    252: (-73.985, 40.685),  # West Village
    # 下城 (Lower Manhattan)
    253: (-73.988, 40.675),  # SoHo
    254: (-73.992, 40.665),  # TriBeCa
    255: (-73.995, 40.655),  # Chinatown
    256: (-74.000, 40.645),  # Financial District
    257: (-74.005, 40.635),  # Battery Park
    # 额外补充（防止少量未覆盖的 ID）
    1: (-73.995, 40.750),
    2: (-73.980, 40.720),
    3: (-73.970, 40.700),
    4: (-73.960, 40.680),
}

def get_lon_lat_from_location(location_id):
    """通过 LocationID 获取经纬度，若不在映射中则返回 None"""
    return LOCATION_CENTROIDS.get(location_id)

# ---------- 网格分配函数 ----------
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

# ---------- 处理单个文件 ----------
def process_file(filepath):
    """处理单个Parquet文件，自动适配格式"""
    try:
        df = pd.read_parquet(filepath)

        # ---- 检测列名 ----
        cols = df.columns.tolist()
        has_coords = ('pickup_longitude' in cols and 'pickup_latitude' in cols)
        has_puloc = ('PULocationID' in cols)

        if has_coords:
            # ---- 旧格式：直接用经纬度 ----
            df = df[['tpep_pickup_datetime', 'pickup_longitude', 'pickup_latitude']].copy()
            df.columns = ['datetime', 'lon', 'lat']
            df['lon'] = df['lon'].astype(float)
            df['lat'] = df['lat'].astype(float)

        elif has_puloc:
            # ---- 新格式：通过 PULocationID 映射经纬度 ----
            df = df[['tpep_pickup_datetime', 'PULocationID']].copy()
            df.columns = ['datetime', 'location_id']

            # 映射经纬度
            df['lon'] = df['location_id'].apply(lambda x: get_lon_lat_from_location(x)[0] if get_lon_lat_from_location(x) else np.nan)
            df['lat'] = df['location_id'].apply(lambda x: get_lon_lat_from_location(x)[1] if get_lon_lat_from_location(x) else np.nan)

            # 丢弃无法映射的记录（即不在曼哈顿内）
            df = df.dropna(subset=['lon', 'lat'])

        else:
            print(f"⚠️ 跳过 {filepath.name}: 缺少必要的列 (pickup_longitude/pickup_latitude 或 PULocationID)")
            return None

        # ---- 统一处理 ----
        # 转换日期，错误时转为 NaT
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

        # 丢弃日期无效的行
        df = df.dropna(subset=['datetime'])

        # ---- 关键修正：过滤异常年份 ----
        df = df[(df['datetime'].dt.year >= MIN_YEAR) & (df['datetime'].dt.year <= MAX_YEAR)]

        if len(df) == 0:
            print(f"⚠️ {filepath.name}: 日期过滤后无有效记录")
            return None

        # 提取日期（仅日期部分，不含时间）
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

# ---------- 主函数 ----------
def main():
    print("=" * 60)
    print("数据预处理：网格化需求统计（兼容新旧格式）")
    print("=" * 60)

    parquet_files = sorted(RAW_DIR.glob("*.parquet"))
    print(f"发现文件: {len(parquet_files)} 个")

    all_demands = []

    for filepath in tqdm(parquet_files, desc="处理文件"):
        demand = process_file(filepath)
        if demand is not None and not demand.empty:
            all_demands.append(demand)

    if not all_demands:
        print("❌ 没有成功处理任何文件，请检查数据格式或映射表。")
        return

    # ---------- 合并数据（统一日期类型并去重） ----------
    print("\n合并数据...")
    final_df = pd.concat(all_demands, ignore_index=True)

    # 确保 date 列为 Timestamp（无时区）
    final_df['date'] = pd.to_datetime(final_df['date'])

    # 若仍有重复（以防万一），聚合求和
    final_df = final_df.groupby(['date', 'grid_id'], as_index=False)['volume'].sum()

    # 填充缺失日期（某些网格某天可能无数据）
    print("填充缺失日期...")
    date_range = pd.date_range(start=final_df['date'].min(), end=final_df['date'].max(), freq='D')
    grid_ids = range(60)

    full_index = pd.MultiIndex.from_product([date_range, grid_ids], names=['date', 'grid_id'])
    final_df = final_df.set_index(['date', 'grid_id']).reindex(full_index, fill_value=0).reset_index()

    # ---------- 保存结果 ----------
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