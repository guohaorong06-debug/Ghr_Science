# 三层权限系统实施计划

**实施日期**: 2026-06-22  
**目标**: 完整的RBAC权限系统  
**设计参考**: 阿里、腾讯、美团、RuoYi

---

## 📊 总体进度：60% 完成

### ✅ Phase 1: 数据库设计 (100%)

**完成内容**:
- 5个核心表：sys_role, sys_permission, sys_role_permission, sys_user_role, guest_session
- 45+权限定义（覆盖所有模块）
- 3个系统角色：GUEST, USER, ADMIN
- 权限-角色关联配置
- 数据迁移脚本

**文件**:
- `backend/src/main/resources/db/upgrade_v2_rbac.sql`

---

### ✅ Phase 2: 实体与Mapper (100%)

**完成内容**:
- 6个实体类：SysRole, SysPermission, SysUserRole, GuestSession + 增强SysUser
- 4个Mapper：SysRoleMapper, SysPermissionMapper, SysUserRoleMapper, GuestSessionMapper
- JOIN查询优化
- 批量操作支持

**文件**:
- `entity/`: SysRole.java, SysPermission.java, SysUserRole.java, GuestSession.java
- `mapper/`: 对应4个Mapper接口

---

### ✅ Phase 3: 核心服务与拦截器 (100%)

**完成内容**:
- PermissionService：权限校验核心逻辑，Redis缓存
- GuestService：游客会话管理，自动过期清理
- PermissionAspect：AOP权限拦截器
- @RequirePermission注解：方法级权限控制
- AdminUserController：用户管理8个API
- GuestController：游客访问3个API

**文件**:
- `service/`: PermissionService.java, GuestService.java
- `aspect/`: PermissionAspect.java
- `annotation/`: RequirePermission.java
- `controller/`: AdminUserController.java, GuestController.java

---

### ⏳ Phase 4: 管理模块完善 (40%)

**待完成**:

#### 4.1 角色管理
```java
AdminRoleController:
- GET /list - 角色列表
- POST / - 创建角色
- PUT / - 编辑角色
- DELETE /{id} - 删除角色
- PUT /{id}/permissions - 配置权限
- GET /{id}/users - 查看角色用户
```

#### 4.2 审计日志
```java
AdminAuditController:
- GET /list - 日志列表（分页、筛选）
- GET /{id} - 日志详情
- GET /stats - 统计分析
- POST /export - 导出日志
```

#### 4.3 系统监控
```java
AdminMonitorController:
- GET /online-users - 在线用户
- GET /stats - 系统统计
- GET /metrics - 性能指标
- POST /kickout - 强制下线
```

#### 4.4 数据管理
```java
AdminDataController:
- POST /backup - 数据备份
- DELETE /clean - 数据清理
- GET /export - 全量导出
- POST /import - 批量导入
```

---

### ⏳ Phase 5: 前端权限控制 (0%)

**待完成**:

#### 5.1 前端权限指令
```javascript
// Vue自定义指令
v-permission="'system:user:add'"
v-role="'ADMIN'"
```

#### 5.2 路由守卫
```javascript
router.beforeEach((to, from, next) => {
  const permissions = store.getters.permissions
  if (hasPermission(to.meta.permission, permissions)) {
    next()
  } else {
    next('/403')
  }
})
```

#### 5.3 管理页面
```
新增页面：
- UserManage.vue - 用户管理
- RoleManage.vue - 角色管理
- PermissionMatrix.vue - 权限矩阵
- AuditLog.vue - 审计日志
- SystemMonitor.vue - 系统监控
- GuestLogin.vue - 游客入口
```

---

### ⏳ Phase 6: 测试与优化 (0%)

**待完成**:

#### 6.1 单元测试
- PermissionServiceTest
- GuestServiceTest
- PermissionAspectTest

#### 6.2 集成测试
- 权限校验流程测试
- 游客模式端到端测试
- 管理员操作测试

#### 6.3 性能优化
- Redis缓存预热
- 权限查询SQL优化
- 批量操作性能测试

---

## 🎯 设计亮点

### 1. 阿里RBAC模型
- 5表设计（用户-角色-权限）
- 灵活的多角色支持
- 细粒度权限控制

### 2. 腾讯权限继承
- 角色优先级排序
- 权限累加机制
- 系统内置角色保护

### 3. 美团资源树
- 权限按模块组织
- 父子权限关联
- 资源类型分类（menu/button/api）

### 4. RuoYi最佳实践
- @RequirePermission注解
- AOP统一拦截
- Redis多级缓存

### 5. 游客模式创新
- UUID临时身份
- Redis会话隔离
- 自动过期清理
- 只读权限限制

---

## 📈 代码统计

| 模块 | 文件数 | 代码行数 |
|------|--------|----------|
| 数据库 | 1 | ~300 |
| 实体类 | 6 | ~250 |
| Mapper | 4 | ~150 |
| Service | 2 | ~350 |
| Aspect | 1 | ~100 |
| Controller | 2 | ~200 |
| 注解 | 1 | ~50 |
| **总计** | **17** | **~1400** |

---

## ⏰ 剩余工作量估算

| Phase | 工作内容 | 预计时间 | 优先级 |
|-------|----------|----------|--------|
| Phase 4 | 4个管理Controller | 4小时 | P0 |
| Phase 5 | 前端5个页面 | 8小时 | P1 |
| Phase 6 | 测试与优化 | 4小时 | P2 |
| **总计** | - | **16小时** | - |

**预计完成时间**: 2天（工作日）或 3天（业余时间）

---

## 🚀 快速部署指南

### 1. 执行数据库升级

```bash
# 连接MySQL
mysql -uroot -p

# 选择数据库
USE logistics;

# 执行升级脚本
SOURCE D:/Ghr_Science/backend/src/main/resources/db/upgrade_v2_rbac.sql;

# 验证
SELECT COUNT(*) FROM sys_role;
SELECT COUNT(*) FROM sys_permission;
SELECT COUNT(*) FROM sys_role_permission;
```

### 2. 重启后端服务

```bash
cd D:\Ghr_Science
docker-compose restart backend

# 或在IDEA中重新运行LogisticsApplication
```

### 3. 测试游客模式

```bash
# 游客登录
curl -X POST http://localhost:8080/api/auth/guest/login

# 响应示例
{
  "code": 200,
  "data": {
    "guestId": "guest_abc123",
    "token": "eyJhbGci...",
    "expiresIn": 7200,
    "permissions": ["site:list", "site:view", ...]
  }
}
```

### 4. 测试管理员权限

```bash
# 管理员登录
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 访问用户管理（需要admin:user:list权限）
curl -X GET http://localhost:8080/api/admin/user/list \
  -H "Authorization: Bearer <token>"
```

---

## ⚠️ 注意事项

1. **数据备份**: 执行upgrade脚本前备份数据库
2. **权限配置**: 首次部署后检查角色权限配置
3. **缓存预热**: 启动后手动触发权限缓存加载
4. **游客清理**: 确保定时任务正常运行
5. **日志审计**: 开启操作日志记录

---

## 📝 已知限制

1. ⏳ AdminUserController的CRUD逻辑为占位实现
2. ⏳ 前端权限控制尚未实现
3. ⏳ 缺少管理员管理页面
4. ⏳ 权限矩阵配置页面待开发
5. ⏳ 审计日志分析功能待完善

---

**当前进度**: 60% ✅  
**下一步**: 完成Phase 4管理模块API  
**预计完工**: 2天内

---

**文档更新时间**: 2026-06-22 18:00:00  
**最新Commit**: f993fc1
