-- ============================================
-- 智能物流决策系统 - 测试数据
-- ============================================

-- 1. 插入测试角色
INSERT INTO sys_role (name, code, description, status, sort_order) VALUES
('管理员', 'ADMIN', '系统管理员，拥有所有权限', 1, 1),
('运营人员', 'OPERATOR', '运营人员，可查看和操作业务数据', 1, 2),
('访客', 'GUEST', '访客，只能查看数据', 1, 3);

-- 2. 插入测试权限
INSERT INTO sys_permission (name, code, type, parent_id, path, sort_order) VALUES
-- 一级菜单
('仪表盘', 'dashboard', 'MENU', NULL, '/dashboard', 1),
('网点管理', 'site', 'MENU', NULL, '/site', 2),
('数据导入', 'data', 'MENU', NULL, '/data-import', 3),
('需求预测', 'forecast', 'MENU', NULL, '/forecast', 4),
('模型管理', 'model', 'MENU', NULL, '/model', 5),
('权限管理', 'admin', 'MENU', NULL, '/admin', 6);

-- 二级权限（网点管理）
INSERT INTO sys_permission (name, code, type, parent_id, sort_order) VALUES
('查看网点', 'site:view', 'BUTTON', (SELECT id FROM sys_permission WHERE code = 'site' LIMIT 1), 1),
('创建网点', 'site:create', 'BUTTON', (SELECT id FROM sys_permission WHERE code = 'site' LIMIT 1), 2),
('编辑网点', 'site:edit', 'BUTTON', (SELECT id FROM sys_permission WHERE code = 'site' LIMIT 1), 3),
('删除网点', 'site:delete', 'BUTTON', (SELECT id FROM sys_permission WHERE code = 'site' LIMIT 1), 4);

-- 二级权限（预测管理）
INSERT INTO sys_permission (name, code, type, parent_id, sort_order) VALUES
('查看预测', 'forecast:view', 'BUTTON', (SELECT id FROM sys_permission WHERE code = 'forecast' LIMIT 1), 1),
('执行预测', 'forecast:execute', 'BUTTON', (SELECT id FROM sys_permission WHERE code = 'forecast' LIMIT 1), 2);

-- 二级权限（权限管理）
INSERT INTO sys_permission (name, code, type, parent_id, sort_order) VALUES
('用户管理', 'admin:user', 'BUTTON', (SELECT id FROM sys_permission WHERE code = 'admin' LIMIT 1), 1),
('角色管理', 'admin:role', 'BUTTON', (SELECT id FROM sys_permission WHERE code = 'admin' LIMIT 1), 2);

-- 3. 分配管理员所有权限
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT
    (SELECT id FROM sys_role WHERE code = 'ADMIN' LIMIT 1),
    id
FROM sys_permission;

-- 4. 分配运营人员部分权限
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT
    (SELECT id FROM sys_role WHERE code = 'OPERATOR' LIMIT 1),
    id
FROM sys_permission
WHERE code IN ('dashboard', 'site', 'site:view', 'site:create', 'site:edit',
               'data', 'forecast', 'forecast:view', 'forecast:execute', 'model');

-- 5. 分配访客只读权限
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT
    (SELECT id FROM sys_role WHERE code = 'GUEST' LIMIT 1),
    id
FROM sys_permission
WHERE code IN ('dashboard', 'site', 'site:view', 'forecast', 'forecast:view');

-- 6. 创建测试用户（密码：123456，BCrypt加密）
-- 注意：实际使用时需要用BCrypt加密密码
INSERT INTO sys_user (username, password, real_name, email, phone, role, enabled) VALUES
('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '系统管理员', 'admin@example.com', '13800138000', 'ADMIN', 1),
('operator', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '运营人员', 'operator@example.com', '13800138001', 'USER', 1),
('guest', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '访客用户', 'guest@example.com', '13800138002', 'GUEST', 1);

-- 7. 分配用户角色
INSERT INTO sys_user_role (user_id, role_id) VALUES
((SELECT id FROM sys_user WHERE username = 'admin' LIMIT 1), (SELECT id FROM sys_role WHERE code = 'ADMIN' LIMIT 1)),
((SELECT id FROM sys_user WHERE username = 'operator' LIMIT 1), (SELECT id FROM sys_role WHERE code = 'OPERATOR' LIMIT 1)),
((SELECT id FROM sys_user WHERE username = 'guest' LIMIT 1), (SELECT id FROM sys_role WHERE code = 'GUEST' LIMIT 1));

-- 8. 插入测试网点数据
INSERT INTO logistics_site (site_code, site_name, province, city, district, address, latitude, longitude, contact_person, contact_phone, status) VALUES
('BJ001', '北京朝阳网点', '北京市', '朝阳区', '朝阳区', '朝阳路123号', 39.9289, 116.4883, '张三', '13800001001', 'ACTIVE'),
('BJ002', '北京海淀网点', '北京市', '海淀区', '海淀区', '中关村大街45号', 39.9833, 116.3161, '李四', '13800001002', 'ACTIVE'),
('SH001', '上海浦东网点', '上海市', '浦东新区', '浦东新区', '世纪大道888号', 31.2397, 121.4999, '王五', '13800002001', 'ACTIVE'),
('SH002', '上海徐汇网点', '上海市', '徐汇区', '徐汇区', '漕河泾开发区', 31.1715, 121.4146, '赵六', '13800002002', 'ACTIVE'),
('GZ001', '广州天河网点', '广东省', '广州市', '天河区', '天河路208号', 23.1353, 113.3235, '孙七', '13800003001', 'ACTIVE');

-- 9. 插入测试模型版本
INSERT INTO model_version (model_type, version_name, description, model_path, performance_metrics, status) VALUES
('LSTM', 'v1.0.0', 'LSTM基线模型', '/models/lstm_v1.0.0.pt', '{"mae": 0.1033, "rmse": 0.2975, "crps": 0.0723}', 'ACTIVE'),
('GRU', 'v1.0.0', 'GRU基线模型', '/models/gru_v1.0.0.pt', '{"mae": 0.1024, "rmse": 0.2912, "crps": 0.0717}', 'ACTIVE'),
('TRANSFORMER', 'v1.0.0', 'Transformer基线模型', '/models/transformer_v1.0.0.pt', '{"mae": 0.0987, "rmse": 0.2845, "crps": 0.0691}', 'ACTIVE'),
('PROPOSED', 'v1.0.0', '提出模型（GraphVAE+Flow）', '/models/proposed_v1.0.0.pt', '{"mae": 0.0891, "rmse": 0.2654, "crps": 0.0535}', 'ACTIVE');

COMMIT;

-- 显示插入结果
SELECT '角色数据插入完成' AS message, COUNT(*) AS count FROM sys_role;
SELECT '权限数据插入完成' AS message, COUNT(*) AS count FROM sys_permission;
SELECT '用户数据插入完成' AS message, COUNT(*) AS count FROM sys_user;
SELECT '网点数据插入完成' AS message, COUNT(*) AS count FROM logistics_site;
SELECT '模型数据插入完成' AS message, COUNT(*) AS count FROM model_version;
