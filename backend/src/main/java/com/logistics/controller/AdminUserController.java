package com.logistics.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.logistics.annotation.RequirePermission;
import com.logistics.entity.SysUser;
import com.logistics.service.AdminUserService;
import com.logistics.utils.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 管理员 - 用户管理（完整实现）
 */
@RestController
@RequestMapping("/api/admin/user")
@RequiredArgsConstructor
@Tag(name = "管理员 - 用户管理")
public class AdminUserController {

    private final AdminUserService adminUserService;

    @GetMapping("/list")
    @Operation(summary = "用户列表")
    @RequirePermission("admin:user:list")
    public Result<Page<SysUser>> list(
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size) {

        Page<SysUser> result = adminUserService.listUsers(page, size, keyword);

        // 移除密码字段
        result.getRecords().forEach(user -> user.setPassword(null));

        return Result.ok(result);
    }

    @PostMapping
    @Operation(summary = "创建用户")
    @RequirePermission("admin:user:add")
    public Result<Long> create(@RequestBody SysUser user) {
        Long userId = adminUserService.createUser(user);
        return Result.ok(userId);
    }

    @PutMapping
    @Operation(summary = "编辑用户")
    @RequirePermission("admin:user:edit")
    public Result<String> update(@RequestBody SysUser user) {
        adminUserService.updateUser(user);
        return Result.ok("用户更新成功");
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除用户")
    @RequirePermission("admin:user:delete")
    public Result<String> delete(@PathVariable Long id) {
        adminUserService.deleteUser(id);
        return Result.ok("用户删除成功");
    }

    @PutMapping("/{id}/status")
    @Operation(summary = "启用/禁用用户")
    @RequirePermission("admin:user:disable")
    public Result<String> toggleStatus(@PathVariable Long id, @RequestParam Integer status) {
        adminUserService.toggleUserStatus(id, status);
        return Result.ok("用户状态更新成功");
    }

    @PutMapping("/{id}/roles")
    @Operation(summary = "分配角色")
    @RequirePermission("admin:user:role")
    public Result<String> assignRoles(@PathVariable Long id, @RequestBody List<Long> roleIds) {
        adminUserService.assignRoles(id, roleIds);
        return Result.ok("角色分配成功");
    }

    @PostMapping("/{id}/reset-password")
    @Operation(summary = "重置密码")
    @RequirePermission("admin:user:reset")
    public Result<Map<String, String>> resetPassword(@PathVariable Long id) {
        String newPassword = adminUserService.resetPassword(id);
        return Result.ok(Map.of("newPassword", newPassword));
    }

    @GetMapping("/stats")
    @Operation(summary = "用户统计")
    @RequirePermission("admin:user:list")
    public Result<Map<String, Object>> stats() {
        Map<String, Object> stats = adminUserService.getUserStats();
        return Result.ok(stats);
    }
}
