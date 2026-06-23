package com.logistics.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.logistics.entity.SysRole;
import com.logistics.entity.SysUser;
import com.logistics.entity.SysUserRole;
import com.logistics.mapper.SysRoleMapper;
import com.logistics.mapper.SysUserMapper;
import com.logistics.mapper.SysUserRoleMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 管理员-用户管理服务
 */
@Service
@RequiredArgsConstructor
public class AdminUserService {

    private final SysUserMapper userMapper;
    private final SysUserRoleMapper userRoleMapper;
    private final SysRoleMapper roleMapper;
    private final PasswordEncoder passwordEncoder;

    /**
     * 分页查询用户列表
     */
    public Page<SysUser> listUsers(Integer page, Integer size, String keyword) {
        Page<SysUser> pageParam = new Page<>(page, size);

        LambdaQueryWrapper<SysUser> wrapper = new LambdaQueryWrapper<>();
        if (keyword != null && !keyword.isEmpty()) {
            wrapper.like(SysUser::getUsername, keyword)
                   .or()
                   .like(SysUser::getEmail, keyword);
        }
        wrapper.orderByDesc(SysUser::getCreateTime);

        return userMapper.selectPage(pageParam, wrapper);
    }

    /**
     * 创建用户
     */
    @Transactional
    @CacheEvict(value = {"user:permissions", "user:roles"}, allEntries = true)
    public Long createUser(SysUser user) {
        // 加密密码
        user.setPassword(passwordEncoder.encode(user.getPassword()));

        // 插入用户
        userMapper.insert(user);

        return user.getId();
    }

    /**
     * 更新用户
     */
    @Transactional
    @CacheEvict(value = {"user:permissions", "user:roles"}, key = "#user.id")
    public void updateUser(SysUser user) {
        // 如果密码不为空，则加密
        if (user.getPassword() != null && !user.getPassword().isEmpty()) {
            user.setPassword(passwordEncoder.encode(user.getPassword()));
        } else {
            user.setPassword(null); // 不更新密码
        }

        userMapper.updateById(user);
    }

    /**
     * 删除用户（软删除）
     */
    @Transactional
    @CacheEvict(value = {"user:permissions", "user:roles"}, key = "#userId")
    public void deleteUser(Long userId) {
        // 软删除用户
        userMapper.deleteById(userId);

        // 删除用户角色关联
        userRoleMapper.deleteByUserId(userId);
    }

    /**
     * 启用/禁用用户
     */
    @Transactional
    public void toggleUserStatus(Long userId, Integer status) {
        SysUser user = new SysUser();
        user.setId(userId);
        user.setStatus(status);
        userMapper.updateById(user);
    }

    /**
     * 分配角色
     */
    @Transactional
    @CacheEvict(value = {"user:permissions", "user:roles"}, key = "#userId")
    public void assignRoles(Long userId, List<Long> roleIds) {
        // 删除旧的角色关联
        userRoleMapper.deleteByUserId(userId);

        // 创建新的角色关联
        if (roleIds != null && !roleIds.isEmpty()) {
            List<SysUserRole> userRoles = roleIds.stream()
                .map(roleId -> {
                    SysUserRole userRole = new SysUserRole();
                    userRole.setUserId(userId);
                    userRole.setRoleId(roleId);
                    return userRole;
                })
                .collect(Collectors.toList());

            userRoleMapper.batchInsert(userRoles);
        }
    }

    /**
     * 重置密码
     */
    @Transactional
    public String resetPassword(Long userId) {
        // 生成随机密码
        String newPassword = generateRandomPassword();

        // 加密并更新
        SysUser user = new SysUser();
        user.setId(userId);
        user.setPassword(passwordEncoder.encode(newPassword));
        userMapper.updateById(user);

        return newPassword;
    }

    /**
     * 用户统计
     */
    public java.util.Map<String, Object> getUserStats() {
        Long totalUsers = userMapper.selectCount(null);
        Long activeUsers = userMapper.selectCount(
            new LambdaQueryWrapper<SysUser>().eq(SysUser::getStatus, 1)
        );
        Long disabledUsers = userMapper.selectCount(
            new LambdaQueryWrapper<SysUser>().eq(SysUser::getStatus, 0)
        );

        return java.util.Map.of(
            "total", totalUsers,
            "active", activeUsers,
            "disabled", disabledUsers
        );
    }

    /**
     * 生成随机密码
     */
    private String generateRandomPassword() {
        String chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789";
        StringBuilder password = new StringBuilder();
        java.util.Random random = new java.util.Random();
        for (int i = 0; i < 8; i++) {
            password.append(chars.charAt(random.nextInt(chars.length())));
        }
        return password.toString();
    }
}
