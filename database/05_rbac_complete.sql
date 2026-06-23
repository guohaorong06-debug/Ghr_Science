-- ============================================
-- 完善三层权限系统数据
-- ============================================

-- 1. 清理并重新插入角色数据
DELETE FROM sys_role WHERE id IN (1,2,3);
INSERT INTO sys_role (id, role_code, role_name, description, sort_order, status, is_system) VALUES
(1, 'GUEST', '游客', '只读权限，可查看公开信息', 3, 1, 1),
(2, 'OPERATOR', '运营员', '业务权限，可管理网点和数据', 2, 1, 1),
(3, 'ADMIN', '管理员', '完整权限，可管理用户和系统配置', 1, 1, 1);

-- 2. 清理并重新插入权限数据
DELETE FROM sys_permission;

-- 2.1 仪表盘模块
INSERT INTO sys_permission (permission_code, permission_name, module, resource_type, api_path, api_method, parent_id, sort_order) VALUES
('dashboard:view', '查看仪表盘', 'dashboard', 'menu', '/dashboard', 'GET', 0, 1);

-- 2.2 网点管理模块
INSERT INTO sys_permission (permission_code, permission_name, module, resource_type, api_path, api_method, parent_id, sort_order) VALUES
('site:view', '查看网点', 'site', 'menu', '/site', 'GET', 0, 2),
('site:list', '网点列表', 'site', 'api', '/api/logistics/site/list', 'GET', 0, 3),
('site:add', '添加网点', 'site', 'button', '/api/logistics/site', 'POST', 0, 4),
('site:edit', '编辑网点', 'site', 'button', '/api/logistics/site', 'PUT', 0, 5),
('site:delete', '删除网点', 'site', 'button', '/api/logistics/site/*', 'DELETE', 0, 6);

-- 2.3 数据导入模块
INSERT INTO sys_permission (permission_code, permission_name, module, resource_type, api_path, api_method, parent_id, sort_order) VALUES
('data:view', '查看数据导入', 'data', 'menu', '/data-import', 'GET', 0, 7),
('data:import', '导入数据', 'data', 'button', '/api/logistics/data/import', 'POST', 0, 8),
('data:export', '导出数据', 'data', 'button', '/api/logistics/data/export', 'GET', 0, 9);

-- 2.4 需求预测模块
INSERT INTO sys_permission (permission_code, permission_name, module, resource_type, api_path, api_method, parent_id, sort_order) VALUES
('forecast:view', '查看预测', 'forecast', 'menu', '/forecast', 'GET', 0, 10),
('forecast:predict', '执行预测', 'forecast', 'button', '/api/forecast/predict', 'POST', 0, 11),
('forecast:history', '查看历史预测', 'forecast', 'api', '/api/forecast/history', 'GET', 0, 12);

-- 2.5 模型管理模块
INSERT INTO sys_permission (permission_code, permission_name, module, resource_type, api_path, api_method, parent_id, sort_order) VALUES
('model:view', '查看模型', 'model', 'menu', '/model', 'GET', 0, 13),
('model:list', '模型列表', 'model', 'api', '/api/model/list', 'GET', 0, 14),
('model:switch', '切换模型', 'model', 'button', '/api/model/switch', 'POST', 0, 15);

-- 2.6 用户管理模块（仅管理员）
INSERT INTO sys_permission (permission_code, permission_name, module, resource_type, api_path, api_method, parent_id, sort_order) VALUES
('admin:user:view', '查看用户管理', 'admin', 'menu', '/admin/user', 'GET', 0, 16),
('admin:user:list', '用户列表', 'admin', 'api', '/api/admin/user/list', 'GET', 0, 17),
('admin:user:add', '添加用户', 'admin', 'button', '/api/admin/user', 'POST', 0, 18),
('admin:user:edit', '编辑用户', 'admin', 'button', '/api/admin/user', 'PUT', 0, 19),
('admin:user:delete', '删除用户', 'admin', 'button', '/api/admin/user/*', 'DELETE', 0, 20),
('admin:user:assign-role', '分配角色', 'admin', 'button', '/api/admin/user/assign-role', 'POST', 0, 21);

-- 2.7 角色管理模块（仅管理员）
INSERT INTO sys_permission (permission_code, permission_name, module, resource_type, api_path, api_method, parent_id, sort_order) VALUES
('admin:role:view', '查看角色管理', 'admin', 'menu', '/admin/role', 'GET', 0, 22),
('admin:role:list', '角色列表', 'admin', 'api', '/api/admin/role/list', 'GET', 0, 23),
('admin:role:add', '添加角色', 'admin', 'button', '/api/admin/role', 'POST', 0, 24),
('admin:role:edit', '编辑角色', 'admin', 'button', '/api/admin/role', 'PUT', 0, 25),
('admin:role:delete', '删除角色', 'admin', 'button', '/api/admin/role/*', 'DELETE', 0, 26),
('admin:role:assign-permission', '分配权限', 'admin', 'button', '/api/admin/role/assign-permission', 'POST', 0, 27);

-- 3. 清理并重新插入角色权限关联
DELETE FROM sys_role_permission;

-- 3.1 游客（GUEST）权限：只读
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT 1, id FROM sys_permission WHERE permission_code IN (
    'dashboard:view',
    'site:view', 'site:list',
    'forecast:view', 'forecast:history',
    'model:view', 'model:list'
);

-- 3.2 运营员（OPERATOR）权限：业务操作
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT 2, id FROM sys_permission WHERE permission_code IN (
    'dashboard:view',
    'site:view', 'site:list', 'site:add', 'site:edit', 'site:delete',
    'data:view', 'data:import', 'data:export',
    'forecast:view', 'forecast:predict', 'forecast:history',
    'model:view', 'model:list', 'model:switch'
);

-- 3.3 管理员（ADMIN）权限：所有权限
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT 3, id FROM sys_permission;

-- 4. 清理并重新插入测试用户
DELETE FROM sys_user WHERE username IN ('admin', 'operator', 'guest');
-- 密码都是 123456 (BCrypt加密后)
INSERT INTO sys_user (username, password, real_name, phone, email, status, enabled) VALUES
('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVKIUi', '系统管理员', '13800138000', 'admin@logistics.com', 1, 1),
('operator', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVKIUi', '运营人员', '13800138001', 'operator@logistics.com', 1, 1),
('guest', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVKIUi', '访客用户', '13800138002', 'guest@logistics.com', 1, 1);

-- 5. 清理并重新插入用户角色关联
DELETE FROM sys_user_role WHERE user_id IN (SELECT id FROM sys_user WHERE username IN ('admin', 'operator', 'guest'));
INSERT INTO sys_user_role (user_id, role_id)
VALUES
((SELECT id FROM sys_user WHERE username='admin'), 3),    -- 管理员
((SELECT id FROM sys_user WHERE username='operator'), 2), -- 运营员
((SELECT id FROM sys_user WHERE username='guest'), 1);    -- 游客

COMMIT;

-- 验证数据
SELECT '角色数据' AS category, role_code, role_name, description FROM sys_role WHERE deleted=0 ORDER BY sort_order;
SELECT '权限数据' AS category, COUNT(*) AS total FROM sys_permission WHERE deleted=0;
SELECT '游客权限数' AS category, COUNT(*) AS total FROM sys_role_permission WHERE role_id=1;
SELECT '运营员权限数' AS category, COUNT(*) AS total FROM sys_role_permission WHERE role_id=2;
SELECT '管理员权限数' AS category, COUNT(*) AS total FROM sys_role_permission WHERE role_id=3;
SELECT '用户角色关联' AS category, u.username, r.role_name FROM sys_user u JOIN sys_user_role ur ON u.id=ur.user_id JOIN sys_role r ON ur.role_id=r.id WHERE u.deleted=0;
