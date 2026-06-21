package com.logistics.service;

import cn.hutool.core.text.csv.CsvReader;
import cn.hutool.core.text.csv.CsvUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.logistics.entity.DemandRecord;
import com.logistics.mapper.DemandRecordMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStreamReader;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

/**
 * 需求记录服务
 */
@Service
@RequiredArgsConstructor
public class DemandRecordService {

    private final DemandRecordMapper recordMapper;

    /**
     * 解析CSV预览（返回前100行）
     */
    public List<DemandRecord> previewCsv(MultipartFile file) throws Exception {
        CsvReader reader = CsvUtil.getReader();
        List<String[]> rows = reader.read(new InputStreamReader(file.getInputStream(), StandardCharsets.UTF_8));

        List<DemandRecord> preview = new ArrayList<>();
        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyy-MM-dd");

        // 跳过表头，取前100行
        for (int i = 1; i < Math.min(rows.size(), 101); i++) {
            String[] row = rows.get(i);
            if (row.length < 3) continue;

            DemandRecord record = new DemandRecord();
            record.setSiteId(Long.parseLong(row[0]));
            record.setRecordDate(LocalDate.parse(row[1], fmt));
            record.setVolume(Integer.parseInt(row[2]));

            if (row.length > 3) record.setIsHoliday("1".equals(row[3]) || "true".equalsIgnoreCase(row[3]));
            if (row.length > 4) record.setWeather(row[4]);
            if (row.length > 5 && !row[5].isEmpty()) record.setTemperature(new BigDecimal(row[5]));
            if (row.length > 6 && !row[6].isEmpty()) record.setPrecipitation(new BigDecimal(row[6]));
            if (row.length > 7 && !row[7].isEmpty()) record.setWindSpeed(new BigDecimal(row[7]));

            preview.add(record);
        }
        return preview;
    }

    /**
     * 批量导入（覆盖已存在的日期数据）
     */
    @Transactional(rollbackFor = Exception.class)
    public int importCsv(MultipartFile file) throws Exception {
        List<DemandRecord> records = previewCsv(file);

        // 批量插入（MyBatis Plus 自动处理冲突）
        for (DemandRecord record : records) {
            // 删除已存在的记录
            recordMapper.delete(new LambdaQueryWrapper<DemandRecord>()
                    .eq(DemandRecord::getSiteId, record.getSiteId())
                    .eq(DemandRecord::getRecordDate, record.getRecordDate()));
            recordMapper.insert(record);
        }
        return records.size();
    }

    /**
     * 分页查询
     */
    public Page<DemandRecord> page(int current, int size, Long siteId, LocalDate startDate, LocalDate endDate) {
        Page<DemandRecord> page = new Page<>(current, size);
        LambdaQueryWrapper<DemandRecord> wrapper = new LambdaQueryWrapper<>();

        if (siteId != null) wrapper.eq(DemandRecord::getSiteId, siteId);
        if (startDate != null) wrapper.ge(DemandRecord::getRecordDate, startDate);
        if (endDate != null) wrapper.le(DemandRecord::getRecordDate, endDate);

        wrapper.orderByDesc(DemandRecord::getRecordDate);
        return recordMapper.selectPage(page, wrapper);
    }
}
