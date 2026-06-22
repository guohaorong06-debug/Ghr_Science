package com.logistics.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 预测结果实体
 */
@Data
@TableName("forecast_result")
public class ForecastResult {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long siteId;

    private LocalDate forecastDate;

    private String modelVersion;

    private Integer median;

    private Integer p10;

    private Integer p90;

    private String conditionJson;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
