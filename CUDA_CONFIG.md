# CUDA配置说明

## 修改内容

**文件**: `backend/pom.xml`

**修改**:
```xml
<!-- 原配置 -->
<dependency>
    <groupId>ai.djl.pytorch</groupId>
    <artifactId>pytorch-native-cpu</artifactId>
    <version>2.0.1</version>
</dependency>

<!-- 新配置 -->
<dependency>
    <groupId>ai.djl.pytorch</groupId>
    <artifactId>pytorch-native-auto</artifactId>
    <version>2.0.1</version>
</dependency>
```

---

## 工作原理

### 自动检测流程

1. **DJL启动时检测系统环境**
2. **检查NVIDIA GPU**
3. **检查CUDA安装 (11.7/11.8)**
4. **根据检测结果自动选择**:
   - 有CUDA → 下载GPU版本
   - 无CUDA → 使用CPU版本

---

## 测试方法

### 步骤1：重启后端

```
1. 在IDEA Console中点击Stop按钮（红色方块）
2. 或按快捷键: Ctrl+F2
3. 等待进程完全停止
```

### 步骤2：重新启动

```
1. 右键 LogisticsApplication.java
2. 选择 "Run 'LogisticsApplication'"
3. 查看Console输出
```

### 步骤3：查看检测结果

#### 如果检测到CUDA（有GPU）:
```
Found CUDA 11.X
Using GPU device: NVIDIA ...
Downloading pytorch-native-cu11X...
```

#### 如果未检测到CUDA（无GPU）:
```
No matching cuda flavor for win-x86_64 found
Downloading CPU version...
```

---

## 支持的配置

### GPU加速（需要）:
- ✅ NVIDIA GPU
- ✅ CUDA 11.7 或 11.8
- ✅ Windows/Linux/Mac

### CPU模式（始终可用）:
- ✅ 任何系统
- ✅ 无需GPU
- ✅ 功能完全相同

---

## 优势

### 单一配置
- ✅ 一套代码适用所有环境
- ✅ 开发机器（有GPU）自动加速
- ✅ 服务器（无GPU）自动回退
- ✅ 无需手动切换

### 性能
- 🚀 GPU: 推理速度快10-100倍
- ✅ CPU: 完全可用，稍慢

### 兼容性
- ✅ 跨平台
- ✅ 向后兼容
- ✅ 自动适配

---

## 常见问题

### Q: 我如何知道用的是GPU还是CPU？
**A**: 查看启动日志
- GPU: 会显示 "Using GPU device"
- CPU: 会显示 "Downloading CPU version"

### Q: 我有NVIDIA GPU但没检测到？
**A**: 检查CUDA安装
```bash
nvidia-smi          # 查看GPU
nvcc --version      # 查看CUDA版本
```
需要CUDA 11.7或11.8

### Q: CPU模式性能够用吗？
**A**: 完全够用
- 对于演示和开发：完全足够
- 对于生产环境：建议使用GPU

### Q: 如何强制使用CPU？
**A**: 修改pom.xml，改回
```xml
<artifactId>pytorch-native-cpu</artifactId>
```

---

## 日志示例

### GPU模式日志:
```
INFO: Found placeholder platform from: cu117-win-x86_64:2.0.1
INFO: Using GPU device: NVIDIA GeForce RTX 3090
INFO: Downloading pytorch-native-cu117...
```

### CPU模式日志:
```
WARN: No matching cuda flavor for win-x86_64 found: cu065
INFO: Downloading CPU version...
INFO: Downloading torch_cpu.dll...
```

---

**修改完成时间**: 2026-06-23  
**GitHub**: https://github.com/guohaorong06-debug/Ghr_Science  
**Commit**: 106
