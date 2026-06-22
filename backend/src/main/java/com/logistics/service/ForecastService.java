package com.logistics.service;

import ai.djl.inference.Predictor;
import com.logistics.entity.Site;
import com.logistics.mapper.SiteMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.*;

/**
 * 预测服务
 *
 * 使用TorchScript模型进行需求预测
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ForecastService {

    private final ModelLoaderService modelLoaderService;
    private final SiteMapper siteMapper;

    /**
     * 预测未来7天需求
     *
     * @param historyData 历史14天数据 [14, 60]
     * @param modelType 模型类型: lstm/gru/transformer
     * @return 预测7天数据 [7, 60]
     */
    public float[][] predict(float[][] historyData, String modelType) {
        try {
            log.info("开始预测，模型类型: {}", modelType);

            // 验证输入
            if (historyData == null || historyData.length != 14 || historyData[0].length != 60) {
                throw new IllegalArgumentException("输入数据格式错误，需要 [14, 60]");
            }

            // 选择模型
            Predictor<float[][], float[][]> predictor = getPredictor(modelType);

            // 执行预测
            long startTime = System.currentTimeMillis();
            float[][] forecast = predictor.predict(historyData);
            long elapsed = System.currentTimeMillis() - startTime;

            log.info("预测完成，耗时: {}ms, 输出形状: [{}, {}]",
                     elapsed, forecast.length, forecast[0].length);

            return forecast;

        } catch (Exception e) {
            log.error("预测失败", e);
            throw new RuntimeException("预测失败: " + e.getMessage(), e);
        }
    }

    /**
     * 智能预测（自动选择最佳模型）
     *
     * 默认使用GRU模型（速度和精度平衡）
     */
    public float[][] predictSmart(float[][] historyData) {
        return predict(historyData, "gru");
    }

    /**
     * 批量预测所有网点
     *
     * @param startDate 预测起始日期
     * @return 预测结果Map<网点ID, 7天预测值>
     */
    public Map<Long, List<Float>> predictAllSites(LocalDate startDate) {
        try {
            // 1. 获取所有网点
            List<Site> sites = siteMapper.selectList(null);

            // 2. 构建历史数据 [14, 60]
            float[][] historyData = buildHistoryData(sites, startDate);

            // 3. 执行预测
            float[][] forecast = predictSmart(historyData);

            // 4. 转换结果
            Map<Long, List<Float>> result = new HashMap<>();
            for (int i = 0; i < Math.min(sites.size(), 60); i++) {
                Site site = sites.get(i);
                List<Float> predictions = new ArrayList<>();
                for (int day = 0; day < 7; day++) {
                    predictions.add(forecast[day][i]);
                }
                result.put(site.getId(), predictions);
            }

            return result;

        } catch (Exception e) {
            log.error("批量预测失败", e);
            throw new RuntimeException("批量预测失败: " + e.getMessage(), e);
        }
    }

    /**
     * 获取预测器
     */
    private Predictor<float[][], float[][]> getPredictor(String modelType) {
        return switch (modelType.toLowerCase()) {
            case "lstm" -> modelLoaderService.getLSTMPredictor();
            case "gru" -> modelLoaderService.getGRUPredictor();
            case "transformer" -> modelLoaderService.getTransformerPredictor();
            default -> throw new IllegalArgumentException("未知模型类型: " + modelType);
        };
    }

    /**
     * 构建历史数据
     *
     * TODO: 从数据库读取真实历史数据
     * 当前返回模拟数据
     */
    private float[][] buildHistoryData(List<Site> sites, LocalDate startDate) {
        float[][] data = new float[14][60];

        // 模拟历史数据
        Random random = new Random();
        for (int day = 0; day < 14; day++) {
            for (int site = 0; site < Math.min(sites.size(), 60); site++) {
                data[day][site] = random.nextFloat() * 100;
            }
        }

        return data;
    }
}
