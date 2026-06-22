-- =============================================
-- 三层权限系统数据库升级脚本
-- 版本: v2.0
-- 日期: 2026-06-22
-- =============================================

-- 1. 角色表
CREATE TABLE IF NOT EXISTS sys_role (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    role_code   VARCHAR(50) NOT NULL UNIQUE COMMENT '角色编码: GUEST/USER/ADMIN',
    role_name   VARCHAR(100) NOT NULL COMMENT '角色名称',
    description VARCHAR(500) COMMENT '角色描述',
    sort_order  INT DEFAULT 0 COMMENT '排序',
    status      TINYINT(1) DEFAULT 1 COMMENT '状态: 1启用 0禁用',
    is_system   TINYINT(1) DEFAULT 0 COMMENT '系统内置角色（不可删除）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted     TINYINT(1) DEFAULT 0,
    INDEX idx_code (role_code),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- 2. 权限表
CREATE TABLE IF NOT EXISTS sys_permission (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    permission_code VARCHAR(100) NOT NULL UNIQUE COMMENT '权限编码: system:user:add',
    permission_name VARCHAR(100) NOT NULL COMMENT '权限名称',
    module          VARCHAR(50) COMMENT '所属模块',
    resource_type   VARCHAR(20) COMMENT '资源类型: menu/button/api',
    api_path        VARCHAR(200) COMMENT 'API路径',
    api_method      VARCHAR(10) COMMENT 'HTTP方法',
    parent_id       BIGINT DEFAULT 0 COMMENT '父权限ID',
    sort_order      INT DEFAULT 0,
    create_time     DATETIME DEFAULT CURRENT_TIMESTAMP,
    deleted         TINYINT(1) DEFAULT 0,
    INDEX idx_module (module),
    INDEX idx_code (permission_code),
    INDEX idx_parent (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='权限表';

-- 3. 角色权限关联表
CREATE TABLE IF NOT EXISTS sys_role_permission (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    role_id       BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    create_time   DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_role_permission (role_id, permission_id),
    INDEX idx_role (role_id),
    INDEX idx_permission (permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色权限关联表';

-- 4. 用户角色关联表
CREATE TABLE IF NOT EXISTS sys_user_role (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT NOT NULL,
    role_id     BIGINT NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_role (user_id, role_id),
    INDEX idx_user (user_id),
    INDEX idx_role (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户角色关联表';

-- 5. 游客会话表
CREATE TABLE IF NOT EXISTS guest_session (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    guest_id    VARCHAR(100) NOT NULL UNIQUE COMMENT '游客唯一标识',
    session_data TEXT COMMENT '会话数据JSON',
    ip_address  VARCHAR(50) COMMENT 'IP地址',
    user_agent  VARCHAR(500) COMMENT '浏览器UA',
    login_time  DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_access DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expire_time DATETIME COMMENT '过期时间',
    INDEX idx_guest (guest_id),
    INDEX idx_expire (expire_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='游客会话表';

-- =============================================
-- 初始化基础数据
-- =============================================

-- 1. 插入三个系统角色
INSERT INTO sys_role (role_code, role_name, description, sort_order, is_system) VALUES
('GUEST', '游客', '临时访客，只读权限，数据存储在缓存', 3, 1),
('USER', '普通用户', '注册用户，可使用基础功能', 2, 1),
('ADMIN', '管理员', '系统管理员，拥有完整权限', 1, 1)
ON DUPLICATE KEY UPDATE role_name=role_name;

-- 2. 插入权限数据（按模块组织）
INSERT INTO sys_permission (permission_code, permission_name, module, resource_type, api_path, api_method, parent_id) VALUES
-- 认证模块
('auth:guest:login', '游客登录', 'auth', 'api', '/api/auth/guest/login', 'POST', 0),
('auth:user:register', '用户注册', 'auth', 'api', '/api/auth/register', 'POST', 0),
('auth:user:login', '用户登录', 'auth', 'api', '/api/auth/login', 'POST', 0),

-- 网点管理模块
('site:list', '查看网点列表', 'site', 'api', '/api/site/list', 'GET', 0),
('site:view', '查看网点详情', 'site', 'api', '/api/site/{id}', 'GET', 0),
('site:add', '新增网点', 'site', 'api', '/api/site', 'POST', 0),
('site:edit', '编辑网点', 'site', 'api', '/api/site', 'PUT', 0),
('site:delete', '删除网点', 'site', 'api', '/api/site/{id}', 'DELETE', 0),

-- 数据管理模块
('data:list', '查看历史数据', 'data', 'api', '/api/data/records', 'GET', 0),
('data:preview', '预览CSV', 'data', 'api', '/api/data/preview', 'POST', 0),
('data:import', '导入数据', 'data', 'api', '/api/data/import', 'POST', 0),
('data:export', '导出数据', 'data', 'api', '/api/data/export', 'GET', 0),
('data:delete', '批量删除数据', 'data', 'api', '/api/data/batch-delete', 'DELETE', 0),

-- 预测模块
('forecast:list', '查看预测结果', 'forecast', 'api', '/api/forecast/results', 'GET', 0),
('forecast:predict', '触发预测', 'forecast', 'api', '/api/forecast/predict', 'POST', 0),
('forecast:model:list', '查看模型版本', 'forecast', 'api', '/api/model/list', 'GET', 0),
('forecast:model:switch', '切换模型版本', 'forecast', 'api', '/api/model/{id}/activate', 'PUT', 0),

-- 预警模块
('alert:list', '查看预警记录', 'alert', 'api', '/api/forecast/alerts', 'GET', 0),
('alert:read', '标记已读', 'alert', 'api', '/api/forecast/alerts/{id}/read', 'PUT', 0),

-- 用户管理模块（管理员专属）
('admin:user:list', '查看用户列表', 'admin', 'api', '/api/admin/user/list', 'GET', 0),
('admin:user:add', '创建用户', 'admin', 'api', '/api/admin/user', 'POST', 0),
('admin:user:edit', '编辑用户', 'admin', 'api', '/api/admin/user', 'PUT', 0),
('admin:user:delete', '删除用户', 'admin', 'api', '/api/admin/user/{id}', 'DELETE', 0),
('admin:user:disable', '禁用/启用用户', 'admin', 'api', '/api/admin/user/{id}/status', 'PUT', 0),
('admin:user:role', '分配角色', 'admin', 'api', '/api/admin/user/{id}/roles', 'PUT', 0),
('admin:user:reset', '重置密码', 'admin', 'api', '/api/admin/user/{id}/reset-password', 'POST', 0),

-- 角色管理模块
('admin:role:list', '查看角色列表', 'admin', 'api', '/api/admin/role/list', 'GET', 0),
('admin:role:add', '创建角色', 'admin', 'api', '/api/admin/role', 'POST', 0),
('admin:role:edit', '编辑角色', 'admin', 'api', '/api/admin/role', 'PUT', 0),
('admin:role:delete', '删除角色', 'admin', 'api', '/api/admin/role/{id}', 'DELETE', 0),
('admin:role:permission', '配置权限', 'admin', 'api', '/api/admin/role/{id}/permissions', 'PUT', 0),

-- 审计日志模块
('admin:audit:list', '查看审计日志', 'admin', 'api', '/api/admin/audit/list', 'GET', 0),
('admin:audit:detail', '日志详情', 'admin', 'api', '/api/admin/audit/{id}', 'GET', 0),
('admin:audit:stats', '日志统计', 'admin', 'api', '/api/admin/audit/stats', 'GET', 0),

-- 系统监控模块
('admin:monitor:online', '在线用户', 'admin', 'api', '/api/admin/monitor/online-users', 'GET', 0),
('admin:monitor:stats', '系统统计', 'admin', 'api', '/api/admin/monitor/stats', 'GET', 0),
('admin:monitor:metrics', '性能指标', 'admin', 'api', '/api/admin/monitor/metrics', 'GET', 0),

-- 数据管理模块
('admin:data:backup', '数据备份', 'admin', 'api', '/api/admin/data/backup', 'POST', 0),
('admin:data:clean', '数据清理', 'admin', 'api', '/api/admin/data/clean', 'DELETE', 0),
('admin:data:export', '导出全量数据', 'admin', 'api', '/api/admin/data/export', 'GET', 0)
ON DUPLICATE KEY UPDATE permission_name=permission_name;

-- 3. 配置角色权限关联
-- GUEST角色权限（只读）
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT r.id, p.id FROM sys_role r, sys_permission p
WHERE r.role_code = 'GUEST' AND p.permission_code IN (
    'auth:guest:login',
    'auth:user:register',
    'site:list',
    'site:view',
    'data:list',
    'data:preview',
    'forecast:list',
    'forecast:model:list',
    'alert:list'
)
ON DUPLICATE KEY UPDATE role_id=role_id;

-- USER角色权限（基础操作）
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT r.id, p.id FROM sys_role r, sys_permission p
WHERE r.role_code = 'USER' AND p.permission_code IN (
    'auth:user:login',
    'site:list',
    'site:view',
    'site:add',
    'site:edit',
    'data:list',
    'data:preview',
    'data:import',
    'data:export',
    'forecast:list',
    'forecast:predict',
    'forecast:model:list',
    'alert:list',
    'alert:read'
)
ON DUPLICATE KEY UPDATE role_id=role_id;

-- ADMIN角色权限（全部权限）
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT r.id, p.id FROM sys_role r, sys_permission p
WHERE r.role_code = 'ADMIN'
ON DUPLICATE KEY UPDATE role_id=role_id;

-- 4. 数据迁移：将现有用户的role字段迁移到sys_user_role表
INSERT INTO sys_user_role (user_id, role_id)
SELECT u.id, r.id FROM sys_user u, sys_role r
WHERE u.role = r.role_code
ON DUPLICATE KEY UPDATE user_id=user_id;

-- 5. 增强audit_log表（添加更多字段）
ALTER TABLE audit_log
    ADD COLUMN IF NOT EXISTS request_params VARCHAR(2000) COMMENT '请求参数' AFTER detail,
    ADD COLUMN IF NOT EXISTS response_status INT COMMENT '响应状态码' AFTER request_params,
    ADD COLUMN IF NOT EXISTS execution_time INT COMMENT '执行时间(ms)' AFTER response_status,
    ADD INDEX idx_user_time (user_id, create_time),
    ADD INDEX idx_action (action);

-- =============================================
-- 完成提示
-- =============================================
SELECT '三层权限系统数据库升级完成！' AS message;
SELECT CONCAT('角色数量: ', COUNT(*)) AS result FROM sys_role;
SELECT CONCAT('权限数量: ', COUNT(*)) AS result FROM sys_permission;
SELECT CONCAT('角色权限关联: ', COUNT(*)) AS result FROM sys_role_permission;
