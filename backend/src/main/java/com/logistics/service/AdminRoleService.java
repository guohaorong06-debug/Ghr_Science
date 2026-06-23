package com.logistics.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.logistics.entity.SysPermission;
import com.logistics.entity.SysRole;
import com.logistics.mapper.SysPermissionMapper;
import com.logistics.mapper.SysRoleMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 角色管理服务
 */
@Service
@RequiredArgsConstructor
public class AdminRoleService {

    private final SysRoleMapper roleMapper;
    private final SysPermissionMapper permissionMapper;

    /**
     * 获取所有角色
     */
    @Cacheable(value = "admin:roles")
    public List<SysRole> listRoles() {
        return roleMapper.selectList(
            new LambdaQueryWrapper<SysRole>()
                .orderByAsc(SysRole::getSortOrder)
        );
    }

    /**
     * 创建角色
     */
    @Transactional
    @CacheEvict(value = {"admin:roles", "role:permissions"}, allEntries = true)
    public Long createRole(SysRole role) {
        roleMapper.insert(role);
        return role.getId();
    }

    /**
     * 更新角色
     */
    @Transactional
    @CacheEvict(value = {"admin:roles", "role:permissions"}, allEntries = true)
    public void updateRole(SysRole role) {
        roleMapper.updateById(role);
    }

    /**
     * 删除角色
     */
    @Transactional
    @CacheEvict(value = {"admin:roles", "role:permissions", "user:roles"}, allEntries = true)
    public void deleteRole(Long roleId) {
        // 检查是否为系统内置角色
        SysRole role = roleMapper.selectById(roleId);
        if (role != null && role.getIsSystem() == 1) {
            throw new RuntimeException("系统内置角色不可删除");
        }

        // 检查是否有用户使用该角色
        Integer userCount = roleMapper.countUsersByRoleId(roleId);
        if (userCount > 0) {
            throw new RuntimeException("该角色下还有 " + userCount + " 个用户，无法删除");
        }

        // 删除角色
        roleMapper.deleteById(roleId);
    }

    /**
     * 配置角色权限
     */
    @Transactional
    @CacheEvict(value = {"role:permissions", "user:permissions"}, allEntries = true)
    public void configurePermissions(Long roleId, List<Long> permissionIds) {
        // 删除旧权限
        roleMapper.deleteRolePermissions(roleId);

        // 添加新权限
        if (permissionIds != null && !permissionIds.isEmpty()) {
            roleMapper.batchInsertPermissions(roleId, permissionIds);
        }
    }

    /**
     * 获取角色的权限列表
     */
    @Cacheable(value = "role:permissions", key = "#roleId")
    public List<SysPermission> getRolePermissions(Long roleId) {
        return permissionMapper.selectPermissionsByRoleId(roleId);
    }

    /**
     * 获取角色的权限ID列表
     */
    @Cacheable(value = "role:permission-ids", key = "#roleId")
    public List<Long> getRolePermissionIds(Long roleId) {
        return permissionMapper.selectPermissionsByRoleId(roleId)
                .stream()
                .map(SysPermission::getId)
                .collect(Collectors.toList());
    }

    /**
     * 分配角色权限（别名方法）
     */
    @Transactional
    @CacheEvict(value = {"role:permissions", "role:permission-ids", "user:permissions"}, allEntries = true)
    public void assignPermissions(Long roleId, List<Long> permissionIds) {
        configurePermissions(roleId, permissionIds);
    }

    /**
     * 获取角色的用户列表
     */
    public List<Map<String, Object>> getRoleUsers(Long roleId) {
        return roleMapper.selectUsersByRoleId(roleId);
    }

    /**
     * 角色统计
     */
    public Map<String, Object> getRoleStats() {
        Long totalRoles = roleMapper.selectCount(null);
        Long systemRoles = roleMapper.selectCount(
            new LambdaQueryWrapper<SysRole>().eq(SysRole::getIsSystem, 1)
        );
        Long customRoles = totalRoles - systemRoles;

        return Map.of(
            "total", totalRoles,
            "system", systemRoles,
            "custom", customRoles
        );
    }
}
