package com.logistics.controller;

import com.logistics.entity.SysPermission;
import com.logistics.service.PermissionService;
import com.logistics.utils.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 权限管理控制器
 */
@RestController
@RequestMapping("/api/admin/permission")
@RequiredArgsConstructor
@Tag(name = "管理员 - 权限管理")
public class PermissionController {

    private final PermissionService permissionService;

    @GetMapping("/list")
    @Operation(summary = "权限列表")
    public Result<List<SysPermission>> list() {
        List<SysPermission> permissions = permissionService.listAllPermissions();
        return Result.ok(permissions);
    }

    @GetMapping("/tree")
    @Operation(summary = "权限树")
    public Result<List<SysPermission>> tree() {
        List<SysPermission> tree = permissionService.getPermissionTree();
        return Result.ok(tree);
    }

    @PostMapping
    @Operation(summary = "创建权限")
    public Result<Long> create(@RequestBody SysPermission permission) {
        Long id = permissionService.createPermission(permission);
        return Result.ok(id);
    }

    @PutMapping
    @Operation(summary = "更新权限")
    public Result<String> update(@RequestBody SysPermission permission) {
        permissionService.updatePermission(permission);
        return Result.ok("权限更新成功");
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除权限")
    public Result<String> delete(@PathVariable Long id) {
        permissionService.deletePermission(id);
        return Result.ok("权限删除成功");
    }
}
