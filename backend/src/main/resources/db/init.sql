CREATE DATABASE IF NOT EXISTS logistics
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE logistics;

-- 用户表
CREATE TABLE IF NOT EXISTS sys_user (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL UNIQUE COMMENT '用户名',
    password    VARCHAR(255) NOT NULL COMMENT 'BCrypt加密密码',
    real_name   VARCHAR(50)  COMMENT '真实姓名',
    role        VARCHAR(20)  NOT NULL DEFAULT 'OPERATOR' COMMENT '角色: ADMIN/OPERATOR',
    phone       VARCHAR(20)  COMMENT '手机号',
    email       VARCHAR(100) COMMENT '邮箱',
    enabled     TINYINT(1)   NOT NULL DEFAULT 1 COMMENT '启用状态',
    create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted     TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '逻辑删除',
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统用户';

-- 物流网点表
CREATE TABLE IF NOT EXISTS logistics_site (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL COMMENT '网点名称',
    longitude    DECIMAL(10,6) NOT NULL COMMENT '经度',
    latitude     DECIMAL(10,6) NOT NULL COMMENT '纬度',
    grid_id      INT          COMMENT '网格编号(0-59)',
    capacity     INT          NOT NULL DEFAULT 1000 COMMENT '日最大处理件数',
    description  VARCHAR(500) COMMENT '备注',
    create_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted      TINYINT(1)   NOT NULL DEFAULT 0,
    INDEX idx_grid_id (grid_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='物流网点';

-- 历史需求数据表
CREATE TABLE IF NOT EXISTS demand_record (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    site_id     BIGINT       NOT NULL COMMENT '网点ID',
    record_date DATE         NOT NULL COMMENT '日期',
    volume      INT          NOT NULL COMMENT '包裹量',
    is_holiday  TINYINT(1)   DEFAULT 0 COMMENT '是否节假日',
    weather     VARCHAR(50)  COMMENT '天气(晴/雨/雪等)',
    temperature DECIMAL(5,2) COMMENT '温度(℃)',
    precipitation DECIMAL(5,2) COMMENT '降水量(mm)',
    wind_speed  DECIMAL(5,2) COMMENT '风速(km/h)',
    create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_site_date (site_id, record_date),
    INDEX idx_date (record_date),
    FOREIGN KEY (site_id) REFERENCES logistics_site(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='历史需求记录';

-- 预测结果表
CREATE TABLE IF NOT EXISTS forecast_result (
    id             BIGINT AUTO_INCREMENT PRIMARY KEY,
    site_id        BIGINT       NOT NULL COMMENT '网点ID',
    forecast_date  DATE         NOT NULL COMMENT '预测日期',
    model_version  VARCHAR(20)  NOT NULL COMMENT '模型版本',
    median         INT          NOT NULL COMMENT '预测中位数',
    p10            INT          COMMENT '10%分位数',
    p90            INT          COMMENT '90%分位数',
    condition_json VARCHAR(500) COMMENT '条件输入(天气/促销等JSON)',
    create_time    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_forecast (site_id, forecast_date, model_version),
    INDEX idx_site_forecast (site_id, forecast_date),
    FOREIGN KEY (site_id) REFERENCES logistics_site(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预测结果';

-- 预警记录表
CREATE TABLE IF NOT EXISTS alert_record (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    site_id         BIGINT       NOT NULL COMMENT '网点ID',
    forecast_id     BIGINT       NOT NULL COMMENT '关联预测ID',
    alert_date      DATE         NOT NULL COMMENT '预警日期',
    alert_level     VARCHAR(20)  NOT NULL COMMENT '预警级别: RED/YELLOW/GREEN',
    overflow_ratio  DECIMAL(5,2) COMMENT '超出比例(%)',
    extra_capacity  INT          COMMENT '建议额外运力',
    is_read         TINYINT(1)   DEFAULT 0 COMMENT '是否已读',
    create_time     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_alert_date (alert_date),
    INDEX idx_site_alert (site_id, alert_date),
    FOREIGN KEY (site_id) REFERENCES logistics_site(id),
    FOREIGN KEY (forecast_id) REFERENCES forecast_result(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预警记录';

-- 模型版本表
CREATE TABLE IF NOT EXISTS model_version (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    version      VARCHAR(20)  NOT NULL UNIQUE COMMENT '版本号',
    file_path    VARCHAR(255) NOT NULL COMMENT '模型文件路径',
    file_size    BIGINT       COMMENT '文件大小(字节)',
    is_active    TINYINT(1)   DEFAULT 0 COMMENT '是否活跃',
    metrics_json VARCHAR(1000) COMMENT '评估指标JSON',
    description  VARCHAR(500) COMMENT '版本说明',
    create_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模型版本';

-- 空间依赖关系表（GNNExplainer预计算结果）
CREATE TABLE IF NOT EXISTS spatial_dependency (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    source_site_id BIGINT   NOT NULL COMMENT '上游网点ID',
    target_site_id BIGINT   NOT NULL COMMENT '下游网点ID',
    weight      DECIMAL(8,6) NOT NULL COMMENT '依赖权重',
    scenario    VARCHAR(100) COMMENT '场景描述',
    create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_dependency (source_site_id, target_site_id, scenario),
    FOREIGN KEY (source_site_id) REFERENCES logistics_site(id),
    FOREIGN KEY (target_site_id) REFERENCES logistics_site(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='空间依赖关系';

-- 审计日志表
CREATE TABLE IF NOT EXISTS audit_log (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT       COMMENT '操作用户ID',
    action      VARCHAR(100) NOT NULL COMMENT '操作类型',
    target      VARCHAR(100) COMMENT '操作对象',
    detail      VARCHAR(1000) COMMENT '操作详情',
    ip          VARCHAR(50)  COMMENT 'IP地址',
    create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_time (user_id, create_time),
    INDEX idx_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审计日志';

-- 插入默认管理员 (密码: admin123，BCrypt加密)
INSERT INTO sys_user (username, password, real_name, role, email)
VALUES ('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5Eh', '系统管理员', 'ADMIN', 'admin@logistics.com')
ON DUPLICATE KEY UPDATE username=username;
