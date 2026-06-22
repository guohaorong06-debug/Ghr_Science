package com.logistics.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 游客会话实体
 */
@Data
@TableName("guest_session")
public class GuestSession {

    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 游客唯一标识
     */
    private String guestId;

    /**
     * 会话数据（JSON格式）
     */
    private String sessionData;

    /**
     * IP地址
     */
    private String ipAddress;

    /**
     * 浏览器UA
     */
    private String userAgent;

    /**
     * 登录时间
     */
    private LocalDateTime loginTime;

    /**
     * 最后访问时间
     */
    private LocalDateTime lastAccess;

    /**
     * 过期时间
     */
    private LocalDateTime expireTime;
}
