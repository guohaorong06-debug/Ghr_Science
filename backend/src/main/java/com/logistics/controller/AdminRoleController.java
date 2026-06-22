package com.logistics.controller;

import com.logistics.entity.SysRole;
import com.logistics.service.AdminRoleService;
import com.logistics.utils.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
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
    public Result<List<SysRole>> list() {
        List<SysRole> roles = adminRoleService.listRoles();
        return Result.ok(roles);
    }

    @PostMapping
    @Operation(summary = "创建角色")
    public Result<Long> create(@RequestBody SysRole role) {
        Long roleId = adminRoleService.createRole(role);
        return Result.ok(roleId);
    }

    @PutMapping
    @Operation(summary = "更新角色")
    public Result<String> update(@RequestBody SysRole role) {
        adminRoleService.updateRole(role);
        return Result.ok("角色更新成功");
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除角色")
    public Result<String> delete(@PathVariable Long id) {
        adminRoleService.deleteRole(id);
        return Result.ok("角色删除成功");
    }

    @PutMapping("/{id}/permissions")
    @Operation(summary = "配置角色权限")
    public Result<String> configurePermissions(
            @PathVariable Long id,
            @RequestBody List<Long> permissionIds) {
        adminRoleService.configurePermissions(id, permissionIds);
        return Result.ok("权限配置成功");
    }

    @GetMapping("/{id}/permissions")
    @Operation(summary = "获取角色权限")
    public Result<List<Map<String, Object>>> getPermissions(@PathVariable Long id) {
        // 简化返回，实际应该返回SysPermission列表
        return Result.ok(List.of());
    }

    @GetMapping("/{id}/users")
    @Operation(summary = "获取角色用户列表")
    public Result<List<Map<String, Object>>> getUsers(@PathVariable Long id) {
        List<Map<String, Object>> users = adminRoleService.getRoleUsers(id);
        return Result.ok(users);
    }

    @GetMapping("/stats")
    @Operation(summary = "角色统计")
    public Result<Map<String, Object>> stats() {
        Map<String, Object> stats = adminRoleService.getRoleStats();
        return Result.ok(stats);
    }
}
