package com.logistics.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.logistics.entity.DemandRecord;
import com.logistics.service.DemandRecordService;
import com.logistics.utils.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDate;
import java.util.List;

/**
 * 数据导入控制器
 */
@RestController
@RequestMapping("/api/data")
@RequiredArgsConstructor
@Tag(name = "数据导入")
public class DataImportController {

    private final DemandRecordService recordService;

    @PostMapping("/preview")
    @Operation(summary = "预览CSV（前100行）")
    public Result<List<DemandRecord>> preview(@RequestParam("file") MultipartFile file) {
        try {
            return Result.ok(recordService.previewCsv(file));
        } catch (Exception e) {
            return Result.error("文件解析失败：" + e.getMessage());
        }
    }

    @PostMapping("/import")
    @Operation(summary = "导入CSV数据")
    public Result<String> importCsv(@RequestParam("file") MultipartFile file) {
        try {
            int count = recordService.importCsv(file);
            return Result.ok("成功导入 " + count + " 条记录");
        } catch (Exception e) {
            return Result.error("导入失败：" + e.getMessage());
        }
    }

    @GetMapping("/records")
    @Operation(summary = "查询历史记录")
    public Result<Page<DemandRecord>> page(
            @RequestParam(defaultValue = "1") int current,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) Long siteId,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd") LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd") LocalDate endDate) {
        return Result.ok(recordService.page(current, size, siteId, startDate, endDate));
    }
}
