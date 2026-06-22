# 登录失败问题排查报告

**问题**: 登录返回500错误
**现象**: `{"code":500,"message":null,"data":null}`
**根本原因**: MySQL字符编码配置问题

## 已尝试的解决方案

1. ✅ 修改application.yml (characterEncoding: utf8mb4 → UTF-8)
2. ✅ 修改docker-compose.yml环境变量
3. ✅ 重启后端容器
4. ❌ 问题依然存在

## 当前诊断

### 容器状态
- 所有容器正常运行
- 后端成功启动（Tomcat on port 8080）
- MySQL数据库正常
- Redis缓存正常

### 环境变量
- ✅ SPRING_DATASOURCE_URL 已设置为UTF-8
- ✅ 环境变量在容器中可见

### 错误追踪
- 后端日志显示SQL异常
- 仍然提示 `Unsupported character encoding 'utf8mb4'`
- 说明jar包内嵌配置未被环境变量覆盖

## 根本问题

**Spring Boot配置优先级问题**：
- jar包内的application.yml仍使用utf8mb4
- 环境变量SPRING_DATASOURCE_URL未能完全覆盖
- 可能是HikariCP初始化时读取了内嵌配置

## 终极解决方案

### 方案1：完全重新构建镜像（推荐）
```bash
cd D:\Ghr_Science\docker
docker-compose down
docker rmi docker-backend -f
docker system prune -f
docker-compose build --no-cache backend
docker-compose up -d
```

### 方案2：使用外部配置文件
```bash
# 1. 创建外部配置
cat > D:\Ghr_Science\docker\application-prod.yml << EOL
spring:
  datasource:
    url: jdbc:mysql://mysql:3306/logistics?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai
EOL

# 2. 挂载配置文件到容器
# 修改docker-compose.yml添加volumes:
#   - ../docker/application-prod.yml:/app/config/application.yml
```

### 方案3：直接修改MySQL驱动参数
```yaml
# docker-compose.yml
environment:
  SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/logistics?useUnicode=true&connectionCollation=utf8mb4_unicode_ci&serverTimezone=Asia/Shanghai
```

## 建议行动

**立即执行方案1**，彻底重新构建：
1. 确认application.yml已修改为UTF-8
2. 完全删除旧镜像和缓存
3. 强制无缓存构建
4. 重新启动所有服务
5. 测试登录功能

## 验证步骤

构建完成后：
```bash
# 1. 检查jar包内配置
docker exec logistics-backend sh -c "unzip -p /app/app.jar BOOT-INF/classes/application.yml | grep characterEncoding"

# 2. 测试登录
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 3. 查看日志
docker logs logistics-backend --tail 50 | grep -i error
```

## 最后手段

如果重建仍失败，修改Java代码直接移除字符集参数：
```java
// SysUserService.java
// 修改密码验证逻辑，临时跳过数据库查询
```

---

**报告生成时间**: 2026-06-22 15:20:00
**需要用户手动执行**: 方案1（重新构建）
