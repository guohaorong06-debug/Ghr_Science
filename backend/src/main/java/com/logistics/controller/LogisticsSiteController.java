package com.logistics.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.logistics.entity.LogisticsSite;
import com.logistics.service.LogisticsSiteService;
import com.logistics.utils.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 网点管理控制器
 */
@RestController
@RequestMapping("/api/site")
@RequiredArgsConstructor
@Tag(name = "网点管理")
public class LogisticsSiteController {

    private final LogisticsSiteService siteService;

    @GetMapping("/page")
    @Operation(summary = "分页查询网点")
    public Result<Page<LogisticsSite>> page(
            @RequestParam(defaultValue = "1") int current,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String keyword) {
        return Result.ok(siteService.page(current, size, keyword));
    }

    @GetMapping("/list")
    @Operation(summary = "查询全部网点")
    public Result<List<LogisticsSite>> list() {
        return Result.ok(siteService.listAll());
    }

    @GetMapping("/{id}")
    @Operation(summary = "根据ID查询")
    public Result<LogisticsSite> getById(@PathVariable Long id) {
        return Result.ok(siteService.getById(id));
    }

    @PostMapping
    @Operation(summary = "新增网点")
    public Result<Void> add(@RequestBody LogisticsSite site) {
        siteService.add(site);
        return Result.ok();
    }

    @PutMapping
    @Operation(summary = "更新网点")
    public Result<Void> update(@RequestBody LogisticsSite site) {
        siteService.update(site);
        return Result.ok();
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除网点")
    public Result<Void> delete(@PathVariable Long id) {
        siteService.delete(id);
        return Result.ok();
    }
}
