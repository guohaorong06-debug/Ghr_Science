package com.logistics.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.logistics.entity.SysUser;
import com.logistics.mapper.SysUserMapper;
import com.logistics.utils.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

/**
 * 用户服务（复用优先、无冗余）
 */
@Service
@RequiredArgsConstructor
public class SysUserService {

    private final SysUserMapper userMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    /**
     * 登录
     */
    public Map<String, Object> login(String username, String password) {
        SysUser user = userMapper.selectOne(
                new LambdaQueryWrapper<SysUser>()
                        .eq(SysUser::getUsername, username)
                        .eq(SysUser::getEnabled, true)
        );

        if (user == null || !passwordEncoder.matches(password, user.getPassword())) {
            throw new RuntimeException("用户名或密码错误");
        }

        String token = jwtUtil.generateToken(user.getUsername(), user.getRole());
        return buildUserInfo(user, token);
    }

    /**
     * 注册
     */
    public void register(SysUser user) {
        if (userMapper.exists(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, user.getUsername()))) {
            throw new RuntimeException("用户名已存在");
        }

        user.setPassword(passwordEncoder.encode(user.getPassword()));
        user.setRole("OPERATOR");
        user.setEnabled(true);
        userMapper.insert(user);
    }

    /**
     * 获取用户信息
     */
    public Map<String, Object> getUserInfo(String username) {
        SysUser user = userMapper.selectOne(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, username));
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        return buildUserInfo(user, null);
    }

    private Map<String, Object> buildUserInfo(SysUser user, String token) {
        Map<String, Object> result = new HashMap<>();
        result.put("id", user.getId());
        result.put("username", user.getUsername());
        result.put("realName", user.getRealName());
        result.put("role", user.getRole());
        result.put("email", user.getEmail());
        result.put("phone", user.getPhone());
        if (token != null) {
            result.put("token", token);
        }
        return result;
    }
}
