package com.logistics.controller;

import com.logistics.service.ForecastService;
import com.logistics.utils.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 预测控制器
 *
 * 使用TorchScript模型进行需求预测
 */
@Slf4j
@RestController
@RequestMapping("/api/forecast")
@RequiredArgsConstructor
@Tag(name = "需求预测", description = "基于深度学习的需求预测API")
public class ForecastController {

    private final ForecastService forecastService;

    @PostMapping("/predict")
    @Operation(summary = "预测需求", description = "输入14天历史数据，预测未来7天需求")
    public Result<ForecastResponse> predict(@RequestBody PredictRequest request) {
        try {
            // 验证输入
            if (request.getHistoryData() == null ||
                request.getHistoryData().length != 14 ||
                request.getHistoryData()[0].length != 60) {
                return Result.error("输入数据格式错误，需要 [14, 60]");
            }

            // 执行预测
            String modelType = request.getModelType() != null ? request.getModelType() : "gru";
            float[][] forecast = forecastService.predict(request.getHistoryData(), modelType);

            // 构建响应
            ForecastResponse response = new ForecastResponse();
            response.setForecast(forecast);
            response.setModelType(modelType);
            response.setDays(7);
            response.setSites(60);

            return Result.ok(response);

        } catch (Exception e) {
            log.error("预测失败", e);
            return Result.error("预测失败: " + e.getMessage());
        }
    }

    @GetMapping("/predict-all")
    @Operation(summary = "批量预测所有网点", description = "自动获取历史数据并预测所有网点")
    public Result<Map<String, Object>> predictAll(
            @RequestParam(required = false) String startDate) {
        try {
            LocalDate date = startDate != null ?
                LocalDate.parse(startDate) : LocalDate.now();

            Map<Long, List<Float>> predictions = forecastService.predictAllSites(date);

            Map<String, Object> response = new HashMap<>();
            response.put("predictions", predictions);
            response.put("startDate", date.toString());
            response.put("forecastDays", 7);
            response.put("totalSites", predictions.size());

            return Result.ok(response);

        } catch (Exception e) {
            log.error("批量预测失败", e);
            return Result.error("批量预测失败: " + e.getMessage());
        }
    }

    @GetMapping("/models")
    @Operation(summary = "获取可用模型列表")
    public Result<List<String>> getAvailableModels() {
        return Result.ok(List.of("lstm", "gru", "transformer"));
    }

    /**
     * 预测请求
     */
    @Data
    public static class PredictRequest {
        private float[][] historyData;  // [14, 60]
        private String modelType;       // lstm/gru/transformer
    }

    /**
     * 预测响应
     */
    @Data
    public static class ForecastResponse {
        private float[][] forecast;  // [7, 60]
        private String modelType;
        private Integer days;
        private Integer sites;
    }
}
