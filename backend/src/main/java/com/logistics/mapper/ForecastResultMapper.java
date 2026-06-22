package com.logistics.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.logistics.entity.ForecastResult;
import org.apache.ibatis.annotations.Mapper;

/**
 * 预测结果Mapper
 */
@Mapper
public interface ForecastResultMapper extends BaseMapper<ForecastResult> {
}
