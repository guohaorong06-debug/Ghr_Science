package com.logistics.controller;

import com.logistics.annotation.RequirePermission;
import com.logistics.entity.SysUser;
import com.logistics.service.SysUserService;
import com.logistics.utils.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 管理员 - 用户管理
 */
@RestController
@RequestMapping("/api/admin/user")
@RequiredArgsConstructor
@Tag(name = "管理员 - 用户管理")
public class AdminUserController {

    private final SysUserService userService;

    @GetMapping("/list")
    @Operation(summary = "用户列表")
    @RequirePermission("admin:user:list")
    public Result<List<SysUser>> list(
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size) {
        // TODO: 实现分页查询
        return Result.ok(List.of());
    }

    @PostMapping
    @Operation(summary = "创建用户")
    @RequirePermission("admin:user:add")
    public Result<String> create(@RequestBody SysUser user) {
        // TODO: 实现用户创建
        return Result.ok("用户创建成功");
    }

    @PutMapping
    @Operation(summary = "编辑用户")
    @RequirePermission("admin:user:edit")
    public Result<String> update(@RequestBody SysUser user) {
        // TODO: 实现用户更新
        return Result.ok("用户更新成功");
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除用户")
    @RequirePermission("admin:user:delete")
    public Result<String> delete(@PathVariable Long id) {
        // TODO: 实现用户删除
        return Result.ok("用户删除成功");
    }

    @PutMapping("/{id}/status")
    @Operation(summary = "启用/禁用用户")
    @RequirePermission("admin:user:disable")
    public Result<String> toggleStatus(@PathVariable Long id, @RequestParam Integer status) {
        // TODO: 实现状态切换
        return Result.ok("用户状态更新成功");
    }

    @PutMapping("/{id}/roles")
    @Operation(summary = "分配角色")
    @RequirePermission("admin:user:role")
    public Result<String> assignRoles(@PathVariable Long id, @RequestBody List<Long> roleIds) {
        // TODO: 实现角色分配
        return Result.ok("角色分配成功");
    }

    @PostMapping("/{id}/reset-password")
    @Operation(summary = "重置密码")
    @RequirePermission("admin:user:reset")
    public Result<String> resetPassword(@PathVariable Long id) {
        // TODO: 实现密码重置
        return Result.ok("密码重置成功，新密码已发送");
    }

    @GetMapping("/stats")
    @Operation(summary = "用户统计")
    @RequirePermission("admin:user:list")
    public Result<Map<String, Object>> stats() {
        // TODO: 实现用户统计
        return Result.ok(Map.of(
                "total", 100,
                "active", 85,
                "disabled", 15
        ));
    }
}
