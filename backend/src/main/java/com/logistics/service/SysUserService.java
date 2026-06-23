package com.logistics.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.logistics.entity.SysPermission;
import com.logistics.entity.SysRole;
import com.logistics.entity.SysUser;
import com.logistics.mapper.SysPermissionMapper;
import com.logistics.mapper.SysRoleMapper;
import com.logistics.mapper.SysUserMapper;
import com.logistics.utils.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 用户服务（复用优先、无冗余）
 */
@Service
@RequiredArgsConstructor
public class SysUserService {

    private final SysUserMapper userMapper;
    private final SysRoleMapper roleMapper;
    private final SysPermissionMapper permissionMapper;
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

        // 获取用户角色和权限
        List<SysRole> roles = roleMapper.selectRolesByUserId(user.getId());
        List<String> roleCodes = roles.stream()
                .map(SysRole::getRoleCode)
                .collect(Collectors.toList());

        List<String> permissionCodes = roles.stream()
                .flatMap(role -> permissionMapper.selectPermissionsByRoleId(role.getId()).stream())
                .map(SysPermission::getPermissionCode)
                .distinct()
                .collect(Collectors.toList());

        String token = jwtUtil.generateToken(user.getUsername(), user.getRole());
        return buildUserInfo(user, token, roleCodes, permissionCodes);
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

        // 获取用户角色和权限
        List<SysRole> roles = roleMapper.selectRolesByUserId(user.getId());
        List<String> roleCodes = roles.stream()
                .map(SysRole::getRoleCode)
                .collect(Collectors.toList());

        List<String> permissionCodes = roles.stream()
                .flatMap(role -> permissionMapper.selectPermissionsByRoleId(role.getId()).stream())
                .map(SysPermission::getPermissionCode)
                .distinct()
                .collect(Collectors.toList());

        return buildUserInfo(user, null, roleCodes, permissionCodes);
    }

    private Map<String, Object> buildUserInfo(SysUser user, String token, List<String> roles, List<String> permissions) {
        Map<String, Object> result = new HashMap<>();
        result.put("id", user.getId());
        result.put("username", user.getUsername());
        result.put("realName", user.getRealName());
        result.put("role", user.getRole());
        result.put("roles", roles);
        result.put("permissions", permissions);
        result.put("email", user.getEmail());
        result.put("phone", user.getPhone());
        if (token != null) {
            result.put("token", token);
        }
        return result;
    }
}
