package com.logistics.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.logistics.entity.GuestSession;
import com.logistics.mapper.GuestSessionMapper;
import com.logistics.utils.JwtUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import javax.servlet.http.HttpServletRequest;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

/**
 * 游客服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class GuestService {

    private final GuestSessionMapper guestSessionMapper;
    private final RedisTemplate<String, Object> redisTemplate;
    private final JwtUtil jwtUtil;

    private static final long GUEST_SESSION_HOURS = 2;
    private static final String GUEST_CACHE_PREFIX = "guest:session:";
    private static final String GUEST_DATA_PREFIX = "guest:data:";

    /**
     * 创建游客会话
     */
    public Map<String, Object> createGuestSession(HttpServletRequest request) {
        // 生成游客ID
        String guestId = "guest_" + UUID.randomUUID().toString().replace("-", "");

        // 创建会话记录
        GuestSession session = new GuestSession();
        session.setGuestId(guestId);
        session.setIpAddress(getClientIp(request));
        session.setUserAgent(request.getHeader("User-Agent"));
        session.setLoginTime(LocalDateTime.now());
        session.setLastAccess(LocalDateTime.now());
        session.setExpireTime(LocalDateTime.now().plusHours(GUEST_SESSION_HOURS));

        Map<String, Object> sessionData = new HashMap<>();
        sessionData.put("loginTime", session.getLoginTime());
        sessionData.put("permissions", getGuestPermissions());

        session.setSessionData(toJson(sessionData));

        // 保存到数据库
        guestSessionMapper.insert(session);

        // 缓存到Redis
        String cacheKey = GUEST_CACHE_PREFIX + guestId;
        redisTemplate.opsForValue().set(cacheKey, sessionData, GUEST_SESSION_HOURS, TimeUnit.HOURS);

        // 生成JWT Token
        String token = jwtUtil.generateToken(guestId, "GUEST");

        Map<String, Object> result = new HashMap<>();
        result.put("guestId", guestId);
        result.put("token", token);
        result.put("expiresIn", GUEST_SESSION_HOURS * 3600);
        result.put("permissions", getGuestPermissions());

        log.info("游客会话创建成功: guestId={}, ip={}", guestId, session.getIpAddress());

        return result;
    }

    /**
     * 获取游客权限列表
     */
    private String[] getGuestPermissions() {
        return new String[]{
            "site:list",
            "site:view",
            "data:list",
            "data:preview",
            "forecast:list",
            "forecast:model:list",
            "alert:list"
        };
    }

    /**
     * 保存游客数据到缓存
     */
    public void saveGuestData(String guestId, String dataKey, Object data) {
        String key = GUEST_DATA_PREFIX + guestId + ":" + dataKey;
        redisTemplate.opsForValue().set(key, data, GUEST_SESSION_HOURS, TimeUnit.HOURS);
    }

    /**
     * 获取游客数据
     */
    public Object getGuestData(String guestId, String dataKey) {
        String key = GUEST_DATA_PREFIX + guestId + ":" + dataKey;
        return redisTemplate.opsForValue().get(key);
    }

    /**
     * 刷新游客会话
     */
    public void refreshGuestSession(String guestId) {
        // 更新数据库
        GuestSession session = guestSessionMapper.selectOne(
            new LambdaQueryWrapper<GuestSession>()
                .eq(GuestSession::getGuestId, guestId)
        );

        if (session != null) {
            session.setLastAccess(LocalDateTime.now());
            session.setExpireTime(LocalDateTime.now().plusHours(GUEST_SESSION_HOURS));
            guestSessionMapper.updateById(session);
        }

        // 刷新Redis过期时间
        String cacheKey = GUEST_CACHE_PREFIX + guestId;
        redisTemplate.expire(cacheKey, GUEST_SESSION_HOURS, TimeUnit.HOURS);
    }

    /**
     * 定时清理过期会话（每小时执行一次）
     */
    @Scheduled(cron = "0 0 * * * ?")
    public void cleanExpiredSessions() {
        int count = guestSessionMapper.deleteExpiredSessions(LocalDateTime.now());
        if (count > 0) {
            log.info("清理过期游客会话: {} 条", count);
        }
    }

    /**
     * 获取客户端IP
     */
    private String getClientIp(HttpServletRequest request) {
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("X-Real-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getRemoteAddr();
        }
        return ip;
    }

    /**
     * 简单的JSON序列化（生产环境建议使用Jackson）
     */
    private String toJson(Map<String, Object> map) {
        // TODO: 使用Jackson序列化
        return map.toString();
    }
}
