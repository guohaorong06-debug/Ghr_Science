package com.logistics.controller;

import com.logistics.entity.ModelVersion;
import com.logistics.service.ModelVersionService;
import com.logistics.utils.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

/**
 * 模型管理控制器
 */
@RestController
@RequestMapping("/api/model")
@RequiredArgsConstructor
@Tag(name = "模型管理")
public class ModelController {

    private final ModelVersionService modelService;

    @GetMapping("/list")
    @Operation(summary = "查询所有模型版本")
    public Result<List<ModelVersion>> list() {
        return Result.ok(modelService.listAll());
    }

    @GetMapping("/active")
    @Operation(summary = "获取活跃模型")
    public Result<ModelVersion> getActive() {
        return Result.ok(modelService.getActiveModel());
    }

    @PostMapping("/upload")
    @Operation(summary = "上传模型文件")
    public Result<ModelVersion> upload(
            @RequestParam("file") MultipartFile file,
            @RequestParam("version") String version,
            @RequestParam(required = false) String description,
            @RequestParam(required = false) String metricsJson) {
        try {
            return Result.ok(modelService.uploadModel(file, version, description, metricsJson));
        } catch (Exception e) {
            return Result.error("上传失败：" + e.getMessage());
        }
    }

    @PutMapping("/{id}/activate")
    @Operation(summary = "激活模型")
    public Result<String> activate(@PathVariable Long id) {
        modelService.activateModel(id);
        return Result.ok("模型已激活");
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除模型")
    public Result<String> delete(@PathVariable Long id) {
        modelService.deleteModel(id);
        return Result.ok("模型已删除");
    }
}
