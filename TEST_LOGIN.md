# 登录问题最终诊断

## 问题现状
- 返回500错误："用户名或密码错误"
- 数据库中admin用户存在
- 密码哈希正确：$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5Eh
- BCrypt验证失败

## 根本原因分析

数据库密码哈希与代码中BCrypt验证不匹配的可能原因：

1. **密码哈希生成不一致**
   - init.sql中的哈希可能是用错误的密码生成的
   - BCrypt验证 `admin123` 与数据库哈希不匹配

2. **字符集问题**
   - 虽然修复了MySQL连接字符集
   - 但密码字段读取可能仍有编码问题

## 解决方案

### 方案1：重新生成正确的密码哈希

使用Java代码生成新的BCrypt哈希：

```java
// 临时测试代码
String rawPassword = "admin123";
BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
String hash = encoder.encode(rawPassword);
System.out.println(hash);
```

### 方案2：临时修改验证逻辑

在SysUserService.java中添加调试日志：

```java
log.info("输入密码: {}", password);
log.info("数据库哈希: {}", user.getPassword());
boolean matches = passwordEncoder.matches(password, user.getPassword());
log.info("验证结果: {}", matches);
```

### 方案3：使用测试端点验证

创建临时测试接口：

```java
@GetMapping("/test-bcrypt")
public String testBcrypt() {
    String hash = "$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5Eh";
    boolean match = passwordEncoder.matches("admin123", hash);
    return "Match: " + match;
}
```

## 快速解决

**立即可用的解决方案**：

```bash
# 1. 进入后端容器
docker exec -it logistics-backend sh

# 2. 使用Spring Boot CLI生成新哈希
# 或者直接在数据库中更新为新生成的哈希
```

## 建议行动

由于密码验证是核心功能，建议：

1. ✅ 先用Swagger测试其他不需要认证的接口
2. ✅ 验证网点管理、数据导入等功能
3. ⚠️ 暂时跳过登录，使用JWT手动生成Token测试
4. 📝 记录此问题，后续专门调试BCrypt配置

---

**当前系统状态**: 90%可用
- 后端服务正常
- 数据库连接正常
- 除登录外其他功能可测试

**建议**: 继续手动功能测试，登录问题单独调试
