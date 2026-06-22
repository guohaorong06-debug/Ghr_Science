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
        cn.hutool.core.text.csv.CsvData csvData = reader.read(new InputStreamReader(file.getInputStream(), StandardCharsets.UTF_8));

        List<DemandRecord> preview = new ArrayList<>();
        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyy-MM-dd");

        // 跳过表头，取前100行
        int rowCount = csvData.getRowCount();
        for (int i = 1; i < Math.min(rowCount, 101); i++) {
            cn.hutool.core.text.csv.CsvRow csvRow = csvData.getRow(i);
            if (csvRow.size() < 3) continue;

            DemandRecord record = new DemandRecord();
            record.setSiteId(Long.parseLong(csvRow.get(0)));
            record.setRecordDate(LocalDate.parse(csvRow.get(1), fmt));
            record.setVolume(Integer.parseInt(csvRow.get(2)));

            if (csvRow.size() > 3) record.setIsHoliday("1".equals(csvRow.get(3)) || "true".equalsIgnoreCase(csvRow.get(3)));
            if (csvRow.size() > 4) record.setWeather(csvRow.get(4));
            if (csvRow.size() > 5 && !csvRow.get(5).isEmpty()) record.setTemperature(new BigDecimal(csvRow.get(5)));
            if (csvRow.size() > 6 && !csvRow.get(6).isEmpty()) record.setPrecipitation(new BigDecimal(csvRow.get(6)));
            if (csvRow.size() > 7 && !csvRow.get(7).isEmpty()) record.setWindSpeed(new BigDecimal(csvRow.get(7)));

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
