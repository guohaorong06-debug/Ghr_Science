package com.logistics.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.logistics.entity.SysPermission;
import com.logistics.mapper.SysPermissionMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 权限管理服务
 */
@Service
@RequiredArgsConstructor
public class PermissionService {

    private final SysPermissionMapper permissionMapper;

    /**
     * 获取所有权限
     */
    @Cacheable(value = "permissions:all")
    public List<SysPermission> listAllPermissions() {
        return permissionMapper.selectList(
            new LambdaQueryWrapper<SysPermission>()
                .orderByAsc(SysPermission::getSortOrder)
        );
    }

    /**
     * 获取权限树
     */
    @Cacheable(value = "permissions:tree")
    public List<SysPermission> getPermissionTree() {
        List<SysPermission> all = listAllPermissions();

        // 构建树形结构（简化版，实际需要递归）
        return all.stream()
            .filter(p -> p.getParentId() == null || p.getParentId() == 0)
            .collect(Collectors.toList());
    }

    /**
     * 创建权限
     */
    @Transactional
    @CacheEvict(value = {"permissions:all", "permissions:tree"}, allEntries = true)
    public Long createPermission(SysPermission permission) {
        permissionMapper.insert(permission);
        return permission.getId();
    }

    /**
     * 更新权限
     */
    @Transactional
    @CacheEvict(value = {"permissions:all", "permissions:tree"}, allEntries = true)
    public void updatePermission(SysPermission permission) {
        permissionMapper.updateById(permission);
    }

    /**
     * 删除权限
     */
    @Transactional
    @CacheEvict(value = {"permissions:all", "permissions:tree", "role:permissions"}, allEntries = true)
    public void deletePermission(Long id) {
        // 检查是否有子权限
        Long childCount = permissionMapper.selectCount(
            new LambdaQueryWrapper<SysPermission>().eq(SysPermission::getParentId, id)
        );

        if (childCount > 0) {
            throw new RuntimeException("该权限下还有子权限，无法删除");
        }

        permissionMapper.deleteById(id);
    }
}
