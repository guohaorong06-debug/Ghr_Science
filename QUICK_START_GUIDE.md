# 🚀 快速启动指南

## 方法1：简化启动脚本（推荐）

### 步骤
```bash
1. 双击运行: D:\Ghr_Science\quick-start.bat
   - 只启动MySQL和Redis
   - 显示详细提示
   - 不会闪退

2. 使用IDEA启动后端:
   - 打开backend项目
   - 找到LogisticsApplication.java
   - 右键 → Run
   - 查看Console日志

3. 启动前端:
   - 打开新终端
   - cd D:\Ghr_Science\frontend
   - npm run dev
```

---

## 方法2：手动分步启动（最稳定）

### 步骤1：启动数据库
```bash
cd D:\Ghr_Science\docker
docker compose up -d mysql redis
```

### 步骤2：启动后端（IDEA）
```
1. IDEA打开 D:\Ghr_Science\backend
2. 找到 src/main/java/com/logistics/LogisticsApplication.java
3. 右键 → Run 'LogisticsApplication'
4. 等待Console显示: Started LogisticsApplication
```

### 步骤3：启动前端
```bash
cd D:\Ghr_Science\frontend
npm run dev
```

---

## 方法3：命令行手动启动

### 打开3个独立CMD窗口

**窗口1 - 数据库**:
```bash
cd D:\Ghr_Science\docker
docker compose up -d mysql redis
docker compose logs -f
```

**窗口2 - 后端**:
```bash
cd D:\Ghr_Science\backend
mvn spring-boot:run
```

**窗口3 - 前端**:
```bash
cd D:\Ghr_Science\frontend
npm run dev
```

---

## 访问地址

```
前端: http://localhost:5173
后端: http://localhost:8080
Swagger: http://localhost:8080/swagger-ui/index.html
```

---

## 测试账号

```
admin / 123456      (管理员)
operator / 123456   (运营员)
guest / 123456      (访客)
```

---

## 常见问题

### Q: start-local.bat 闪退？
**A**: 可能是路径或权限问题
- 使用 quick-start.bat 代替
- 或右键"以管理员身份运行"
- 或使用上述手动方法

### Q: 端口被占用？
**A**: 检查并关闭占用进程
```bash
netstat -ano | findstr "8080"
netstat -ano | findstr "5173"
taskkill /PID <PID> /F
```

### Q: Docker启动失败？
**A**: 确保Docker Desktop正在运行
```bash
docker info
```

---

**推荐**: 使用方法1（quick-start.bat + IDEA）最简单稳定！
