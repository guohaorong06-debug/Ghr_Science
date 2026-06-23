package com.logistics.controller;

import com.logistics.entity.SysRole;
import com.logistics.service.AdminRoleService;
import com.logistics.utils.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 管理员 - 角色管理
 */
@RestController
@RequestMapping("/api/admin/role")
@RequiredArgsConstructor
@Tag(name = "管理员 - 角色管理")
public class AdminRoleController {

    private final AdminRoleService adminRoleService;

    @GetMapping("/list")
    @Operation(summary = "角色列表")
    @PreAuthorize("hasRole('ADMIN')")
    public Result<List<SysRole>> list() {
        List<SysRole> roles = adminRoleService.listRoles();
        return Result.ok(roles);
    }

    @PostMapping
    @Operation(summary = "创建角色")
    @PreAuthorize("hasRole('ADMIN')")
    public Result<Long> create(@RequestBody SysRole role) {
        Long roleId = adminRoleService.createRole(role);
        return Result.ok(roleId);
    }

    @PutMapping
    @Operation(summary = "更新角色")
    @PreAuthorize("hasRole('ADMIN')")
    public Result<String> update(@RequestBody SysRole role) {
        adminRoleService.updateRole(role);
        return Result.ok("角色更新成功");
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除角色")
    @PreAuthorize("hasRole('ADMIN')")
    public Result<String> delete(@PathVariable Long id) {
        adminRoleService.deleteRole(id);
        return Result.ok("角色删除成功");
    }

    @GetMapping("/{id}/permissions")
    @Operation(summary = "获取角色权限列表")
    @PreAuthorize("hasRole('ADMIN')")
    public Result<List<Long>> getRolePermissions(@PathVariable Long id) {
        List<Long> permissionIds = adminRoleService.getRolePermissionIds(id);
        return Result.ok(permissionIds);
    }

    @PostMapping("/{id}/assign-permission")
    @Operation(summary = "分配角色权限")
    @PreAuthorize("hasRole('ADMIN')")
    public Result<String> assignPermissions(
            @PathVariable Long id,
            @RequestBody Map<String, List<Long>> body
    ) {
        List<Long> permissionIds = body.get("permissionIds");
        adminRoleService.assignPermissions(id, permissionIds);
        return Result.ok("权限分配成功");
    }

    @GetMapping("/{id}/users")
    @Operation(summary = "获取角色用户列表")
    @PreAuthorize("hasRole('ADMIN')")
    public Result<List<Map<String, Object>>> getRoleUsers(@PathVariable Long id) {
        List<Map<String, Object>> users = adminRoleService.getRoleUsers(id);
        return Result.ok(users);
    }
}
