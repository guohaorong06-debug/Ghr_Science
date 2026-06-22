package com.logistics.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.logistics.entity.SysPermission;
import com.logistics.entity.SysRole;
import com.logistics.mapper.SysPermissionMapper;
import com.logistics.mapper.SysRoleMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 权限服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class PermissionService {

    private final SysPermissionMapper permissionMapper;
    private final SysRoleMapper roleMapper;

    /**
     * 获取用户的所有角色
     */
    @Cacheable(value = "user:roles", key = "#userId")
    public List<SysRole> getUserRoles(Long userId) {
        return roleMapper.selectRolesByUserId(userId);
    }

    /**
     * 获取用户的所有权限
     */
    @Cacheable(value = "user:permissions", key = "#userId")
    public List<SysPermission> getUserPermissions(Long userId) {
        return permissionMapper.selectPermissionsByUserId(userId);
    }

    /**
     * 获取用户的权限编码集合
     */
    @Cacheable(value = "user:permission:codes", key = "#userId")
    public Set<String> getUserPermissionCodes(Long userId) {
        List<String> codes = permissionMapper.selectPermissionCodesByUserId(userId);
        return codes.stream().collect(Collectors.toSet());
    }

    /**
     * 检查用户是否拥有指定权限
     */
    public boolean hasPermission(Long userId, String permissionCode) {
        Set<String> userPermissions = getUserPermissionCodes(userId);
        return userPermissions.contains(permissionCode);
    }

    /**
     * 检查用户是否拥有任意一个权限（OR）
     */
    public boolean hasAnyPermission(Long userId, String... permissionCodes) {
        Set<String> userPermissions = getUserPermissionCodes(userId);
        for (String code : permissionCodes) {
            if (userPermissions.contains(code)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 检查用户是否拥有所有权限（AND）
     */
    public boolean hasAllPermissions(Long userId, String... permissionCodes) {
        Set<String> userPermissions = getUserPermissionCodes(userId);
        for (String code : permissionCodes) {
            if (!userPermissions.contains(code)) {
                return false;
            }
        }
        return true;
    }

    /**
     * 检查用户是否拥有指定角色
     */
    @Cacheable(value = "user:has:role", key = "#userId + ':' + #roleCode")
    public boolean hasRole(Long userId, String roleCode) {
        List<SysRole> roles = getUserRoles(userId);
        return roles.stream().anyMatch(r -> r.getRoleCode().equals(roleCode));
    }

    /**
     * 检查用户是否是管理员
     */
    public boolean isAdmin(Long userId) {
        return hasRole(userId, "ADMIN");
    }

    /**
     * 检查用户是否是游客
     */
    public boolean isGuest(Long userId) {
        return hasRole(userId, "GUEST");
    }

    /**
     * 获取角色的所有权限
     */
    @Cacheable(value = "role:permissions", key = "#roleId")
    public List<SysPermission> getRolePermissions(Long roleId) {
        return permissionMapper.selectPermissionsByRoleId(roleId);
    }

    /**
     * 查询所有权限（树形结构）
     */
    public List<SysPermission> getAllPermissions() {
        return permissionMapper.selectList(
            new LambdaQueryWrapper<SysPermission>()
                .orderByAsc(SysPermission::getSortOrder)
        );
    }

    /**
     * 查询所有角色
     */
    public List<SysRole> getAllRoles() {
        return roleMapper.selectList(
            new LambdaQueryWrapper<SysRole>()
                .eq(SysRole::getStatus, 1)
                .orderByAsc(SysRole::getSortOrder)
        );
    }
}
