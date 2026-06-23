-- ============================================
-- 智能物流决策系统 - 完整数据库索引
-- ============================================

-- 1. sys_user 索引
CREATE INDEX idx_sys_user_username ON sys_user(username);
CREATE INDEX idx_sys_user_email ON sys_user(email);
CREATE INDEX idx_sys_user_status ON sys_user(enabled);
CREATE INDEX idx_sys_user_create_time ON sys_user(create_time);

-- 2. sys_role 索引
CREATE INDEX idx_sys_role_code ON sys_role(code);
CREATE INDEX idx_sys_role_status ON sys_role(status);

-- 3. sys_permission 索引
CREATE INDEX idx_sys_permission_code ON sys_permission(code);
CREATE INDEX idx_sys_permission_parent ON sys_permission(parent_id);
CREATE INDEX idx_sys_permission_type ON sys_permission(type);

-- 4. sys_user_role 索引
CREATE INDEX idx_user_role_user ON sys_user_role(user_id);
CREATE INDEX idx_user_role_role ON sys_user_role(role_id);
CREATE UNIQUE INDEX uk_user_role ON sys_user_role(user_id, role_id);

-- 5. sys_role_permission 索引
CREATE INDEX idx_role_permission_role ON sys_role_permission(role_id);
CREATE INDEX idx_role_permission_perm ON sys_role_permission(permission_id);
CREATE UNIQUE INDEX uk_role_permission ON sys_role_permission(role_id, permission_id);

-- 6. logistics_site 索引
CREATE INDEX idx_site_code ON logistics_site(site_code);
CREATE INDEX idx_site_status ON logistics_site(status);
CREATE INDEX idx_site_location ON logistics_site(latitude, longitude);

-- 7. demand_record 索引
CREATE INDEX idx_demand_site ON demand_record(site_id);
CREATE INDEX idx_demand_date ON demand_record(date);
CREATE INDEX idx_demand_site_date ON demand_record(site_id, date);

-- 8. forecast_result 索引
CREATE INDEX idx_forecast_site ON forecast_result(site_id);
CREATE INDEX idx_forecast_date ON forecast_result(forecast_date);
CREATE INDEX idx_forecast_model ON forecast_result(model_version);
CREATE INDEX idx_forecast_time ON forecast_result(created_at);

-- 9. model_version 索引
CREATE INDEX idx_model_status ON model_version(status);
CREATE INDEX idx_model_type ON model_version(model_type);
CREATE INDEX idx_model_create_time ON model_version(created_at);

-- 10. alert_record 索引
CREATE INDEX idx_alert_site ON alert_record(site_id);
CREATE INDEX idx_alert_date ON alert_record(alert_date);
CREATE INDEX idx_alert_level ON alert_record(alert_level);
CREATE INDEX idx_alert_status ON alert_record(is_handled);

-- 复合索引优化
CREATE INDEX idx_demand_site_date_comp ON demand_record(site_id, date DESC);
CREATE INDEX idx_forecast_site_date_comp ON forecast_result(site_id, forecast_date DESC);
CREATE INDEX idx_alert_site_date_level ON alert_record(site_id, alert_date, alert_level);

COMMIT;
