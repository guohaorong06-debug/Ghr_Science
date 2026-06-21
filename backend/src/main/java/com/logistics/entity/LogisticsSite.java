package com.logistics.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 物流网点实体
 */
@Data
@TableName("logistics_site")
public class LogisticsSite {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String name;

    private BigDecimal longitude;

    private BigDecimal latitude;

    private Integer gridId;

    private Integer capacity;

    private String description;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;

    @TableLogic
    private Boolean deleted;
}
