# 🚀 智能物流决策系统 - 启动指南

---

## 📋 推荐启动方案

### ⭐ 方案1：使用IntelliJ IDEA（最稳定，推荐）

**优势**：
- ✅ 100%成功率
- ✅ 实时查看日志
- ✅ 方便调试和断点
- ✅ 代码热重载
- ✅ 完整的开发工具支持

**步骤**：

#### 1. 启动数据库
```bash
cd D:\Ghr_Science\docker
docker compose up -d mysql redis
```

#### 2. 运行后端
- 用IDEA打开 `backend` 项目
- 找到 `LogisticsApplication.java`
- 右键 → Run 'LogisticsApplication'
- 在Console中实时查看日志
- 启动成功后访问: http://localhost:8080

#### 3. 运行前端
```bash
cd D:\Ghr_Science\frontend
npm install  # 仅首次需要
npm run dev
```
- 终端实时显示日志
- 访问: http://localhost:5173

---

### ⭐ 方案2：一键启动脚本（简单快捷）

**使用方法**：

#### Windows
```bash
# 启动所有服务
D:\Ghr_Science\start-local.bat

# 停止所有服务
关闭弹出的后端/前端窗口
docker compose down
```

#### Linux/Mac
```bash
# 添加执行权限（仅首次）
chmod +x start-local.sh

# 启动
./start-local.sh
```

**特点**：
- ✅ 自动启动MySQL、Redis、后端、前端
- ✅ 独立窗口显示日志
- ✅ 实时查看运行状态
- ✅ 关闭窗口即停止服务

---

### ⭐ 方案3：Docker完整部署（生产环境）

**注意**：当前Docker存在启动问题，建议使用方案1或2

```bash
cd D:\Ghr_Science\docker

# 重新构建并启动
docker compose down
docker compose build backend
docker compose up -d

# 查看日志
docker logs -f logistics-backend
docker logs -f logistics-frontend
```

---

## 📊 查看实时日志

### 方案1（IDEA）
- 后端：IDEA的Console窗口自动显示
- 前端：命令行窗口自动显示

### 方案2（start-local.bat）
- 后端：查看弹出的"物流系统-后端"窗口
- 前端：查看弹出的"物流系统-前端"窗口

### 方案3（Docker）
```bash
# 查看后端日志
docker logs -f logistics-backend

# 查看前端日志
docker logs -f logistics-frontend

# 查看所有日志
docker compose logs -f
```

---

## 🎯 访问地址

### 主要服务
- **前端**: http://localhost:5173
- **后端**: http://localhost:8080
- **Swagger文档**: http://localhost:8080/swagger-ui/index.html
- **API文档**: http://localhost:8080/v3/api-docs

### 数据库连接
- **MySQL**: localhost:3306
  - 用户名: root
  - 密码: logistics2026
  - 数据库: logistics

- **Redis**: localhost:6379
  - 无密码

---

## 👤 测试账号

```
管理员:
  用户名: admin
  密码: 123456
  权限: 全部

运营员:
  用户名: operator
  密码: 123456
  权限: 业务操作

访客:
  用户名: guest
  密码: 123456
  权限: 只读
```

---

## 🛑 停止服务

### 方案1（IDEA）
- IDEA: 点击Stop按钮
- 前端: Ctrl+C 或关闭终端
- 数据库: `docker compose down`

### 方案2（start-local.bat）
- 直接关闭后端/前端窗口
- 或在窗口中按 Ctrl+C
- 数据库: `docker compose down`

### 方案3（Docker）
```bash
docker compose down
```

---

## ⚡ 快速命令

### 完全重启
```bash
# 停止所有
docker compose down
taskkill /F /IM java.exe  # Windows
pkill java  # Linux/Mac

# 重新启动
start-local.bat  # 或使用IDEA
```

### 只重启后端
```bash
# IDEA: 点击重启按钮
# 或在后端窗口: Ctrl+C 后重新运行
```

### 只重启前端
```bash
cd frontend
npm run dev
```

---

## 💡 常见问题

### Q: 端口被占用
```bash
# 检查8080端口
netstat -ano | findstr "8080"

# 检查5173端口
netstat -ano | findstr "5173"

# 杀死占用进程
taskkill /PID <PID> /F
```

### Q: 数据库连接失败
```bash
# 检查MySQL是否运行
docker ps | grep mysql

# 查看MySQL日志
docker logs logistics-mysql

# 重启MySQL
docker restart logistics-mysql
```

### Q: 前端无法访问后端
- 检查后端是否启动成功（查看日志）
- 检查CORS配置
- 确认后端端口8080未被占用

---

## 🎊 推荐工作流

**开发模式（推荐）**：
1. 启动数据库: `docker compose up -d mysql redis`
2. IDEA运行后端（实时调试）
3. 命令行运行前端（热重载）
4. 代码修改自动生效

**演示模式**：
1. 运行 `start-local.bat`
2. 等待启动完成
3. 直接访问系统

**生产模式**：
1. 修复Docker问题后
2. 使用 `docker compose up -d`
3. 完整容器化部署

---

**建议使用方案1（IDEA）获得最佳开发体验！** ✨
