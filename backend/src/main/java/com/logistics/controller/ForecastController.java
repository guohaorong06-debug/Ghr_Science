package com.logistics.controller;

import com.logistics.entity.ForecastResult;
import com.logistics.service.ForecastService;
import com.logistics.utils.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * 预测服务控制器
 */
@RestController
@RequestMapping("/api/forecast")
@RequiredArgsConstructor
@Tag(name = "预测服务")
public class ForecastController {

    private final ForecastService forecastService;

    @PostMapping("/predict")
    @Operation(summary = "执行预测")
    public Result<List<ForecastResult>> predict(@RequestBody PredictRequest req) {
        return Result.ok(forecastService.predict(req.getSiteId(), req.getStartDate(), req.getConditions()));
    }

    @GetMapping("/results")
    @Operation(summary = "查询预测结果")
    public Result<List<ForecastResult>> getResults(
            @RequestParam Long siteId,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd") LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd") LocalDate endDate) {
        return Result.ok(forecastService.getResults(siteId, startDate, endDate));
    }

    @GetMapping("/alerts")
    @Operation(summary = "查询预警列表")
    public Result<List<Map<String, Object>>> getAlerts(
            @RequestParam(required = false) Long siteId,
            @RequestParam(required = false) String level,
            @RequestParam(required = false) Boolean isRead) {
        return Result.ok(forecastService.getAlerts(siteId, level, isRead));
    }

    @PutMapping("/alerts/{id}/read")
    @Operation(summary = "标记预警已读")
    public Result<Void> markRead(@PathVariable Long id) {
        forecastService.markAlertRead(id);
        return Result.ok();
    }

    @Data
    static class PredictRequest {
        private Long siteId;
        private LocalDate startDate;
        private Map<String, Object> conditions;
    }
}
