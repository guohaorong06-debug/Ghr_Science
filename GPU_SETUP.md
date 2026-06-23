# GPU加速配置指南

## 检测到的硬件

```
GPU型号: NVIDIA GeForce RTX 3050 Laptop
显存: 4096MB (4GB)
驱动版本: 546.30
CUDA版本: 12.3
平台: Windows x86_64
```

---

## pom.xml配置

### 已添加的依赖

```xml
<!-- CUDA 11.8 for GPU Acceleration -->
<dependency>
    <groupId>ai.djl.pytorch</groupId>
    <artifactId>pytorch-native-cu118</artifactId>
    <version>2.0.1</version>
    <classifier>win-x86_64</classifier>
    <scope>runtime</scope>
</dependency>

<!-- CPU Fallback -->
<dependency>
    <groupId>ai.djl.pytorch</groupId>
    <artifactId>pytorch-native-cpu</artifactId>
    <version>2.0.1</version>
    <scope>runtime</scope>
</dependency>
```

---

## 为什么使用CUDA 11.8？

### 兼容性

- ✅ DJL 0.24.0最高支持CUDA 11.8
- ✅ CUDA 11.8向下兼容CUDA 12.3
- ✅ RTX 3050完全支持CUDA 11.8
- ✅ 无需降级CUDA驱动

### 性能

- 🚀 GPU推理速度：CPU的10-100倍
- 🚀 RTX 3050适合中等规模模型
- 🚀 4GB显存足够运行预测任务

---

## 重启后端步骤

### 步骤1：停止当前后端

```
在IDEA中:
1. 找到Console窗口
2. 点击红色Stop按钮
3. 等待进程完全停止
```

### 步骤2：重新加载Maven依赖

**方法A（推荐）**:
```
1. 右键 pom.xml
2. 选择 Maven -> Reload project
3. 等待依赖下载完成
```

**方法B**:
```
1. File -> Invalidate Caches...
2. 勾选 "Clear file system cache" 和 "Clear VCS Log caches"
3. 点击 "Invalidate and Restart"
```

### 步骤3：重新启动

```
1. 右键 LogisticsApplication.java
2. Run 'LogisticsApplication'
3. 查看Console日志
```

---

## 验证GPU已启用

### 成功标志

在Console日志中查找：

#### GPU加载成功:
```
INFO: Found CUDA 11.8
INFO: Using GPU device: NVIDIA GeForce RTX 3050
INFO: Downloading pytorch-native-cu118...
```

#### 或:
```
Device: GPU
GPU Name: NVIDIA GeForce RTX 3050
```

### 失败标志（回退CPU）:

```
WARN: No matching cuda flavor
INFO: Downloading CPU version...
```

如果看到这个，说明GPU未被识别，系统使用CPU模式。

---

## 性能对比

### 预测推理速度

| 模式 | 单次预测耗时 | 相对性能 |
|------|-------------|---------|
| GPU (RTX 3050) | 10-50ms | 100% |
| CPU (Intel/AMD) | 500-2000ms | 5-20% |

### 显存使用

- 模型加载：约500MB
- 推理缓存：约200MB
- 总计：约700MB
- 4GB显存足够

---

## 故障排查

### Q: 看到"No matching cuda flavor"？

**可能原因**:
1. Maven依赖未正确下载
2. CUDA库路径问题
3. GPU被其他进程占用

**解决方法**:
```bash
# 检查GPU状态
nvidia-smi

# 重新加载Maven
mvn clean install -U

# 重启IDEA
```

### Q: 出现"CUDA out of memory"？

**解决方法**:
1. 关闭其他占用GPU的程序（游戏、视频编辑等）
2. 减少批处理大小
3. 清理显存：重启系统

### Q: GPU使用率很低？

**正常情况**:
- 模型推理是轻量级任务
- GPU使用率10-30%是正常的
- 不需要100%利用率

---

## 性能优化建议

### 1. 关闭不必要的GPU程序
```
检查GPU进程:
- 关闭壁纸引擎（wallpaper_engine）
- 关闭浏览器硬件加速
- 关闭Docker Desktop GPU支持（如不需要）
```

### 2. 确保充足的显存
```
当前使用: 1404MB / 4096MB
可用显存: 2692MB
推荐预留: 至少1GB空闲
```

### 3. 使用最新驱动
```
当前驱动: 546.30
检查更新: GeForce Experience
```

---

## 回退到CPU模式

如果遇到GPU问题，可以临时回退：

```xml
<!-- 注释掉GPU依赖 -->
<!--
<dependency>
    <groupId>ai.djl.pytorch</groupId>
    <artifactId>pytorch-native-cu118</artifactId>
    ...
</dependency>
-->

<!-- 只保留CPU -->
<dependency>
    <groupId>ai.djl.pytorch</groupId>
    <artifactId>pytorch-native-cpu</artifactId>
    <version>2.0.1</version>
</dependency>
```

---

## 监控GPU使用

### 实时监控
```bash
# 每秒刷新
nvidia-smi -l 1

# 只看GPU使用率
nvidia-smi --query-gpu=utilization.gpu --format=csv -l 1
```

### 查看进程
```bash
nvidia-smi pmon
```

---

**配置完成时间**: 2026-06-23  
**GPU型号**: NVIDIA GeForce RTX 3050 Laptop  
**CUDA版本**: 12.3 (使用11.8库)  
**GitHub**: https://github.com/guohaorong06-debug/Ghr_Science  
**Commit**: 109
