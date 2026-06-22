"""
NYC TLC出租车数据下载脚本

数据源: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
下载范围: 2010-2022年黄色出租车数据
"""

import os
import requests
from tqdm import tqdm
from pathlib import Path

# 配置
DATA_DIR = Path("../data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
YEARS = range(2019, 2023)  # 先下载2019-2022年数据（完整数据量大，按需扩展）
MONTHS = range(1, 13)

def download_file(url, dest_path):
    """下载单个文件"""
    if dest_path.exists():
        print(f"✅ 已存在: {dest_path.name}")
        return True

    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))

            with open(dest_path, 'wb') as f, tqdm(
                desc=dest_path.name,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

            print(f"✅ 下载成功: {dest_path.name}")
            return True
        else:
            print(f"❌ 下载失败 {url}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 下载出错 {url}: {e}")
        return False

def main():
    print("=" * 60)
    print("NYC TLC数据下载工具")
    print("=" * 60)
    print(f"保存目录: {DATA_DIR.absolute()}")
    print(f"下载年份: {YEARS.start}-{YEARS.stop - 1}")
    print("=" * 60)

    download_list = []
    for year in YEARS:
        for month in MONTHS:
            filename = f"yellow_tripdata_{year}-{month:02d}.parquet"
            url = f"{BASE_URL}/{filename}"
            dest = DATA_DIR / filename
            download_list.append((url, dest))

    print(f"\n总文件数: {len(download_list)}")
    input("按Enter开始下载...")

    success_count = 0
    for url, dest in download_list:
        if download_file(url, dest):
            success_count += 1

    print("\n" + "=" * 60)
    print(f"下载完成: {success_count}/{len(download_list)}")
    print("=" * 60)

    # 保存元数据
    metadata = {
        "source": "NYC TLC Trip Record Data",
        "url": "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page",
        "years": list(YEARS),
        "file_count": success_count,
        "data_dir": str(DATA_DIR.absolute())
    }

    import json
    with open(DATA_DIR / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

if __name__ == "__main__":
    main()
