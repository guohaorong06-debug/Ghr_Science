package com.logistics.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.logistics.entity.LogisticsSite;
import com.logistics.mapper.LogisticsSiteMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 网点服务
 */
@Service
@RequiredArgsConstructor
public class LogisticsSiteService {

    private final LogisticsSiteMapper siteMapper;

    /**
     * 分页查询
     */
    public Page<LogisticsSite> page(int current, int size, String keyword) {
        Page<LogisticsSite> page = new Page<>(current, size);
        LambdaQueryWrapper<LogisticsSite> wrapper = new LambdaQueryWrapper<>();
        if (keyword != null && !keyword.isEmpty()) {
            wrapper.like(LogisticsSite::getName, keyword)
                   .or().eq(LogisticsSite::getGridId, keyword);
        }
        return siteMapper.selectPage(page, wrapper);
    }

    /**
     * 获取全部网点（地图用）
     */
    public List<LogisticsSite> listAll() {
        return siteMapper.selectList(null);
    }

    /**
     * 新增
     */
    public void add(LogisticsSite site) {
        validateCoordinates(site.getLongitude().doubleValue(), site.getLatitude().doubleValue());
        siteMapper.insert(site);
    }

    /**
     * 更新
     */
    public void update(LogisticsSite site) {
        if (site.getLongitude() != null && site.getLatitude() != null) {
            validateCoordinates(site.getLongitude().doubleValue(), site.getLatitude().doubleValue());
        }
        siteMapper.updateById(site);
    }

    /**
     * 删除
     */
    public void delete(Long id) {
        siteMapper.deleteById(id);
    }

    /**
     * 坐标验证
     */
    private void validateCoordinates(double lon, double lat) {
        if (lon < -180 || lon > 180 || lat < -90 || lat > 90) {
            throw new RuntimeException("坐标范围错误：经度[-180,180]，纬度[-90,90]");
        }
    }
}
