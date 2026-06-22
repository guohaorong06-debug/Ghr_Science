# 部署说明文档

## 🚀 快速部署

### 本地开发环境

#### 前置要求
- JDK 17+
- Node.js 18+
- Docker Desktop
- MySQL 8.0
- Redis 7.2

#### 启动步骤

**1. 启动基础设施**
```bash
cd docker
docker-compose up -d mysql redis
```

**2. 启动后端**
```bash
cd backend
# 设置环境变量
export JWT_SECRET="logistics-system-secret-key-2026-change-this-in-production-min-256-bits"
export MYSQL_PASSWORD="logistics2026"

# IDEA中运行或命令行
mvn spring-boot:run
```

**3. 启动前端**
```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173`

---

### Docker完整部署

#### 一键部署（推荐）

**Windows:**
```cmd
cd docker
deploy.bat
```

**Linux/Mac:**
```bash
cd docker
chmod +x deploy.sh
./deploy.sh
```

#### 手动部署
```bash
cd docker
docker-compose down
docker-compose up -d --build
```

#### 访问地址
- **前端**: http://localhost
- **后端**: http://localhost:8080
- **API文档**: http://localhost:8080/swagger-ui/index.html

#### 默认账号
- 用户名: `admin`
- 密码: `admin123`

---

## 📱 PWA安装

### 电脑端
1. 访问 http://localhost
2. 浏览器地址栏右侧点击"安装"图标
3. 确认安装

### 手机端
1. 用手机浏览器访问部署地址
2. 浏览器菜单 → "添加到主屏幕"
3. 图标出现在桌面，点击即可全屏使用

---

## 🔧 配置说明

### 环境变量

#### 后端 (application.yml)
```yaml
spring:
  datasource:
    url: ${SPRING_DATASOURCE_URL:jdbc:mysql://localhost:3306/logistics}
    username: ${SPRING_DATASOURCE_USERNAME:root}
    password: ${MYSQL_PASSWORD:logistics2026}
  data:
    redis:
      host: ${SPRING_DATA_REDIS_HOST:localhost}
      password: ${REDIS_PASSWORD:}

jwt:
  secret: ${JWT_SECRET:changeme-please-set-env-variable}
  expiration: 7200000
```

#### 前端 (vite.config.ts)
```typescript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,
    },
  },
}
```

---

## 📊 容器管理

### 查看日志
```bash
# 所有服务
docker-compose logs -f

# 单个服务
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 重启服务
```bash
docker-compose restart backend
```

### 停止服务
```bash
docker-compose down
```

### 清理数据（危险操作）
```bash
docker-compose down -v  # 删除所有数据卷
```

---

## 🌐 生产部署

### 阿里云/腾讯云部署

**1. 购买服务器**
- 配置：2核4G起步
- 系统：Ubuntu 22.04 LTS
- 安全组：开放80、443端口

**2. 安装Docker**
```bash
curl -fsSL https://get.docker.com | bash -s docker
sudo systemctl start docker
sudo systemctl enable docker
```

**3. 上传代码**
```bash
# 本地打包
git archive --format=tar.gz --output=logistics.tar.gz HEAD

# 上传到服务器
scp logistics.tar.gz user@server:/home/user/

# 服务器解压
ssh user@server
tar -xzf logistics.tar.gz
cd Ghr_Science/docker
```

**4. 配置域名（可选）**
```bash
# 修改 nginx.conf
server_name your-domain.com;

# 申请SSL证书（Let's Encrypt）
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

**5. 启动服务**
```bash
./deploy.sh
```

**6. 设置开机自启**
```bash
# 编辑 /etc/systemd/system/logistics.service
sudo systemctl enable logistics
```

---

## 🔐 安全建议

### 生产环境必做
1. **修改默认密码**
   - MySQL root密码
   - 管理员账号密码

2. **配置环境变量**
   ```bash
   export JWT_SECRET=$(openssl rand -base64 32)
   ```

3. **启用HTTPS**
   - 使用Nginx反向代理
   - 配置SSL证书

4. **限制端口访问**
   - 仅开放80/443
   - MySQL/Redis不对外暴露

5. **定期备份**
   ```bash
   docker exec logistics-mysql mysqldump -u root -p logistics > backup.sql
   ```

---

## 📈 性能优化

### 后端优化
- JVM参数调优: `-Xms1g -Xmx2g`
- 数据库连接池: HikariCP默认配置已优化
- Redis缓存: 热点数据缓存

### 前端优化
- Gzip压缩: Nginx已配置
- 静态资源CDN
- Service Worker离线缓存

---

## 🐛 故障排查

### 前端无法访问
```bash
# 检查容器状态
docker ps | grep frontend

# 查看日志
docker logs logistics-frontend

# 检查Nginx配置
docker exec -it logistics-frontend nginx -t
```

### 后端连接失败
```bash
# 检查后端日志
docker logs logistics-backend

# 检查数据库连接
docker exec -it logistics-mysql mysql -u root -p

# 检查网络
docker network inspect logistics-net
```

### 数据库初始化失败
```bash
# 手动执行初始化脚本
docker exec -i logistics-mysql mysql -u root -plogistics2026 logistics < backend/src/main/resources/db/init.sql
```

---

## 📞 技术支持

项目仓库: https://github.com/guohaorong06-debug/Ghr_Science
