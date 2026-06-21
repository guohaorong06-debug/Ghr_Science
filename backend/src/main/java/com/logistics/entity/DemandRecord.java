package com.logistics.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 历史需求记录实体
 */
@Data
@TableName("demand_record")
public class DemandRecord {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long siteId;

    private LocalDate recordDate;

    private Integer volume;

    private Boolean isHoliday;

    private String weather;

    private BigDecimal temperature;

    private BigDecimal precipitation;

    private BigDecimal windSpeed;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
