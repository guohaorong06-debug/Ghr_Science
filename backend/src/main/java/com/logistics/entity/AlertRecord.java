package com.logistics.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 预警记录实体
 */
@Data
@TableName("alert_record")
public class AlertRecord {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long siteId;

    private Long forecastId;

    private LocalDate alertDate;

    private String alertLevel;

    private BigDecimal overflowRatio;

    private Integer extraCapacity;

    private Boolean isRead;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
