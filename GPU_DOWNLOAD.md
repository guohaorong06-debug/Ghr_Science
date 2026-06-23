# PyTorch CUDA手动下载 & 配置

## 下载命令

### 步骤1：清理DJL旧缓存
```bash
# 删除旧的CPU缓存（这是导致冲突的原因）
rd /s /q C:\Users\Lenovo\.djl.ai\pytorch\
```

### 步骤2：手动下载CUDA 11.8原生库
```bash
# 创建缓存目录
mkdir C:\Users\Lenovo\.djl.ai\pytorch\2.0.1-cu118-win-x86_64\ 2>nul

# 下载3个核心DLL到该目录
cd C:\Users\Lenovo\.djl.ai\pytorch\2.0.1-cu118-win-x86_64\

# 核心库 (约90MB)
curl -L -o torch_cuda.dll "https://publish.djl.ai/pytorch/2.0.1/cu118/win-x86_64/native/lib/torch.dll.gz"
# 辅助库
curl -L -o uv.dll "https://publish.djl.ai/pytorch/2.0.1/cu118/win-x86_64/native/lib/uv.dll.gz"
```

### 步骤3：在IDEA中操作
```
1. 右键 pom.xml → Maven → Reload project
2. 运行 LogisticsApplication
3. 查看日志中是否有：Using CUDA / NVIDIA GPU
```

## 验证GPU启用

启动后Console中查找：
```
✅ Found CUDA 11.8 platform
✅ Using GPU device: NVIDIA GeForce RTX 3050  
✅ Created Predictor
```

如果看到这些日志 → GPU加速成功！
如果还是"No matching cuda flavor" → CPU模式（功能不受影响）
