# NYC TLC数据集获取方式

## 方式1：自动脚本下载（推荐）

```bash
cd D:\Ghr_Science\research\scripts
python 1_download_data.py
```

**优点**：
- ✅ 自动化，无需手动操作
- ✅ 断点续传（中断后可继续）
- ✅ 进度条显示
- ✅ 自动验证文件完整性

**缺点**：
- ⚠️ 需要稳定网络
- ⚠️ 下载时间较长（30-60分钟）

---

## 方式2：手动下载（备选）

### 官方数据源

**网址**: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

### 手动下载步骤

1. **访问官网**
   ```
   https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
   ```

2. **选择数据类型**
   - 点击 "Yellow Taxi Trip Records"

3. **下载文件**（2019-2022年）
   ```
   yellow_tripdata_2019-01.parquet
   yellow_tripdata_2019-02.parquet
   ...
   yellow_tripdata_2022-12.parquet
   ```
   共48个文件

4. **保存位置**
   ```
   D:\Ghr_Science\research\data\raw\
   ```

5. **创建元数据**
   在 `data/raw/` 目录创建 `metadata.json`：
   ```json
   {
     "source": "NYC TLC Trip Record Data",
     "url": "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page",
     "years": [2019, 2020, 2021, 2022],
     "file_count": 48,
     "data_dir": "D:\\Ghr_Science\\research\\data\\raw"
   }
   ```

---

## 方式3：使用下载工具（最快）

### 使用IDM（Internet Download Manager）

1. **安装IDM**
   - 下载地址：https://www.internetdownloadmanager.com/

2. **批量下载**
   - 在官网页面右键选择"使用IDM下载所有链接"
   - 筛选 `.parquet` 文件
   - 设置保存到 `D:\Ghr_Science\research\data\raw\`

3. **优点**
   - ✅ 多线程下载，速度快
   - ✅ 断点续传
   - ✅ 批量管理

---

## 方式4：使用云盘分享（推荐给国内用户）

### 百度网盘/阿里云盘

如果有同学已下载，可以：

1. **共享云盘链接**
2. **直接下载打包好的数据**
3. **解压到** `D:\Ghr_Science\research\data\raw\`

**优点**：
- ✅ 国内网络快
- ✅ 避免重复下载

---

## 方式5：使用Kaggle数据集（镜像源）

### Kaggle镜像

```bash
# 安装Kaggle CLI
pip install kaggle

# 配置API Key（从Kaggle账户获取）
# 放到 C:\Users\用户名\.kaggle\kaggle.json

# 搜索NYC TLC数据集
kaggle datasets list -s "nyc tlc"

# 下载数据集
kaggle datasets download -d elemento/nyc-yellow-taxi-trip-data
```

---

## 方式6：使用镜像站点（学术网络）

### 清华镜像/阿里云镜像

某些数据可能在国内镜像站有备份：

```bash
# 示例（具体地址需查询）
wget https://mirrors.aliyun.com/dataset/nyc-tlc/...
```

---

## 方式7：简化版数据集（快速测试）

### 使用少量数据测试流程

**修改脚本只下载1-2个月数据**：

编辑 `1_download_data.py`：

```python
# 原代码
YEARS = range(2019, 2023)
MONTHS = range(1, 13)

# 改为
YEARS = [2022]  # 只下载2022年
MONTHS = [1, 2]  # 只下载1-2月
```

**优点**：
- ✅ 下载时间短（5-10分钟）
- ✅ 快速验证流程
- ✅ 后续可扩展

---

## 推荐方案

### 对于不同情况

| 情况 | 推荐方式 |
|------|----------|
| **网络稳定** | 方式1：自动脚本 |
| **网络不稳定** | 方式3：IDM下载 |
| **快速测试** | 方式7：简化数据集 |
| **有云盘资源** | 方式4：云盘分享 |
| **学术网络** | 方式6：镜像站点 |

---

## 数据集大小参考

| 时间范围 | 文件数 | 总大小 |
|----------|--------|--------|
| 2022年（1年） | 12 | ~8GB |
| 2021-2022年（2年） | 24 | ~16GB |
| 2019-2022年（4年） | 48 | ~30GB |
| 2010-2022年（完整） | 156 | ~100GB |

---

## 下载链接示例

```
# 2022年数据直接下载链接
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-01.parquet
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-02.parquet
...
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-12.parquet
```

---

## 验证下载完整性

下载完成后验证：

```bash
cd D:\Ghr_Science\research\data\raw

# 检查文件数量
ls -l | wc -l

# 检查文件大小
du -sh .

# 运行预处理脚本测试
cd ../../scripts
python 2_preprocess.py
```

---

## 总结

**最简单方式**：
1. 先用方式7（简化数据集）快速测试流程
2. 确认流程正确后，再用方式1或方式3下载完整数据

**现在选择哪种方式？** 🚀
