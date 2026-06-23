# 后端启动详细指南

## 当前状态
- ✅ 前端已启动（端口5173）
- ❌ 后端未启动（端口8080）
- ⚠️ 前端无法连接后端API

## 立即操作

### 方法1：使用IntelliJ IDEA（推荐）

#### 步骤1：打开项目
```
1. 启动 IntelliJ IDEA
2. 选择 "Open" 或 "Open Project"
3. 浏览到: D:\Ghr_Science\backend
4. 点击 "OK"
5. 等待IDEA索引完成
```

#### 步骤2：运行应用
```
1. 在项目视图中展开:
   backend/src/main/java/com/logistics/

2. 找到文件:
   LogisticsApplication.java

3. 右键点击该文件

4. 选择:
   "Run 'LogisticsApplication.main()'"
   
5. 查看Console窗口的输出
```

#### 步骤3：确认启动成功
在Console窗口中查找以下信息：
```
Started LogisticsApplication in X.XXX seconds (process running for X.XXX)
Tomcat started on port(s): 8080 (http)
```

看到这两行表示启动成功！

---

### 方法2：使用Maven命令行

打开新的CMD窗口：
```cmd
cd D:\Ghr_Science\backend
mvn spring-boot:run
```

等待看到：
```
Started LogisticsApplication in X.XXX seconds
```

---

## 启动后的操作

### 1. 刷新浏览器
- 回到浏览器: http://localhost:5173
- 按 F5 刷新页面
- 前端会自动重新连接后端

### 2. 测试登录
- 用户名: `admin`
- 密码: `123456`
- 点击登录

### 3. 访问Swagger API文档
- 打开: http://localhost:8080/swagger-ui/index.html
- 查看所有可用API

---

## 常见问题

### Q: IDEA没有"Run"选项？
**A**: 确保已安装Java 17
- 检查: File → Project Structure → Project SDK
- 应该显示: Java 17 或更高版本

### Q: 端口8080被占用？
**A**: 查找并关闭占用进程
```cmd
netstat -ano | findstr "8080"
taskkill /PID <PID号> /F
```

### Q: 数据库连接失败？
**A**: 确认数据库已启动
```cmd
cd D:\Ghr_Science\docker
docker compose up -d mysql redis
docker ps
```

应该看到 `logistics-mysql` 和 `logistics-redis` 在运行

---

## 完整启动顺序

```
1. 启动数据库
   cd D:\Ghr_Science\docker
   docker compose up -d mysql redis
   等待30秒

2. 启动后端
   使用IDEA运行 LogisticsApplication.java
   等待看到 "Started LogisticsApplication"

3. 启动前端（已完成）
   cd D:\Ghr_Science\frontend
   npm run dev
   
4. 访问系统
   http://localhost:5173
   登录: admin / 123456
```

---

**提示**: 确保按顺序启动，数据库必须在后端之前启动！
