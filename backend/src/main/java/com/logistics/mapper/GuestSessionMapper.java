package com.logistics.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.logistics.entity.GuestSession;
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Mapper;

import java.time.LocalDateTime;

/**
 * 游客会话Mapper
 */
@Mapper
public interface GuestSessionMapper extends BaseMapper<GuestSession> {

    /**
     * 清理过期会话
     */
    @Delete("DELETE FROM guest_session WHERE expire_time < #{now}")
    int deleteExpiredSessions(LocalDateTime now);
}
