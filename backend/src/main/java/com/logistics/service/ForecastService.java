package com.logistics.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.logistics.entity.AlertRecord;
import com.logistics.entity.ForecastResult;
import com.logistics.entity.LogisticsSite;
import com.logistics.mapper.AlertRecordMapper;
import com.logistics.mapper.ForecastResultMapper;
import com.logistics.mapper.LogisticsSiteMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.*;

/**
 * 预测服务（阶段3：占位实现，随机数模拟）
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ForecastService {

    private final ForecastResultMapper forecastMapper;
    private final AlertRecordMapper alertMapper;
    private final LogisticsSiteMapper siteMapper;

    /**
     * 执行预测（占位实现：生成随机预测值）
     * TODO: 阶段6替换为真实DJL模型推理
     */
    @Transactional(rollbackFor = Exception.class)
    public List<ForecastResult> predict(Long siteId, LocalDate startDate, Map<String, Object> conditions) {
        LogisticsSite site = siteMapper.selectById(siteId);
        if (site == null) {
            throw new RuntimeException("网点不存在");
        }

        String modelVersion = "v1.0.0-placeholder";
        List<ForecastResult> results = new ArrayList<>();
        Random random = new Random();

        // 模拟预测未来7天
        for (int i = 0; i < 7; i++) {
            LocalDate forecastDate = startDate.plusDays(i);

            // 随机生成预测值（基于网点处理能力波动）
            int baseVolume = site.getCapacity();
            int median = baseVolume + random.nextInt(200) - 100;
            int p10 = median - 50 - random.nextInt(50);
            int p90 = median + 50 + random.nextInt(50);

            ForecastResult forecast = new ForecastResult();
            forecast.setSiteId(siteId);
            forecast.setForecastDate(forecastDate);
            forecast.setModelVersion(modelVersion);
            forecast.setMedian(median);
            forecast.setP10(p10);
            forecast.setP90(p90);
            forecast.setConditionJson(conditions != null ? conditions.toString() : null);

            // 删除旧预测结果
            forecastMapper.delete(new LambdaQueryWrapper<ForecastResult>()
                    .eq(ForecastResult::getSiteId, siteId)
                    .eq(ForecastResult::getForecastDate, forecastDate)
                    .eq(ForecastResult::getModelVersion, modelVersion));

            forecastMapper.insert(forecast);
            results.add(forecast);

            // 生成预警
            generateAlert(forecast, site);
        }

        log.info("网点{}预测完成，生成{}条结果", siteId, results.size());
        return results;
    }

    /**
     * 生成预警
     */
    private void generateAlert(ForecastResult forecast, LogisticsSite site) {
        int predicted = forecast.getP90(); // 用90%分位数评估风险
        int capacity = site.getCapacity();

        if (predicted <= capacity) {
            return; // 无需预警
        }

        // 计算超出比例
        BigDecimal ratio = BigDecimal.valueOf(predicted - capacity)
                .divide(BigDecimal.valueOf(capacity), 4, RoundingMode.HALF_UP)
                .multiply(BigDecimal.valueOf(100));

        // 判断预警级别
        String level;
        if (ratio.compareTo(BigDecimal.valueOf(30)) > 0) {
            level = "RED";
        } else if (ratio.compareTo(BigDecimal.valueOf(10)) > 0) {
            level = "YELLOW";
        } else {
            level = "GREEN";
        }

        // 计算建议额外运力
        int extraCapacity = predicted - capacity;

        AlertRecord alert = new AlertRecord();
        alert.setSiteId(forecast.getSiteId());
        alert.setForecastId(forecast.getId());
        alert.setAlertDate(forecast.getForecastDate());
        alert.setAlertLevel(level);
        alert.setOverflowRatio(ratio);
        alert.setExtraCapacity(extraCapacity);
        alert.setIsRead(false);

        alertMapper.insert(alert);
    }

    /**
     * 查询预测结果
     */
    public List<ForecastResult> getResults(Long siteId, LocalDate startDate, LocalDate endDate) {
        LambdaQueryWrapper<ForecastResult> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ForecastResult::getSiteId, siteId);
        if (startDate != null) wrapper.ge(ForecastResult::getForecastDate, startDate);
        if (endDate != null) wrapper.le(ForecastResult::getForecastDate, endDate);
        wrapper.orderByAsc(ForecastResult::getForecastDate);
        return forecastMapper.selectList(wrapper);
    }

    /**
     * 查询预警列表
     */
    public List<Map<String, Object>> getAlerts(Long siteId, String level, Boolean isRead) {
        LambdaQueryWrapper<AlertRecord> wrapper = new LambdaQueryWrapper<>();
        if (siteId != null) wrapper.eq(AlertRecord::getSiteId, siteId);
        if (level != null) wrapper.eq(AlertRecord::getAlertLevel, level);
        if (isRead != null) wrapper.eq(AlertRecord::getIsRead, isRead);
        wrapper.orderByDesc(AlertRecord::getAlertDate);

        List<AlertRecord> alerts = alertMapper.selectList(wrapper);
        List<Map<String, Object>> result = new ArrayList<>();

        for (AlertRecord alert : alerts) {
            Map<String, Object> map = new HashMap<>();
            map.put("alert", alert);

            // 关联网点信息
            LogisticsSite site = siteMapper.selectById(alert.getSiteId());
            map.put("siteName", site != null ? site.getName() : "未知");

            result.add(map);
        }

        return result;
    }

    /**
     * 标记预警已读
     */
    public void markAlertRead(Long alertId) {
        AlertRecord alert = alertMapper.selectById(alertId);
        if (alert != null) {
            alert.setIsRead(true);
            alertMapper.updateById(alert);
        }
    }
}
