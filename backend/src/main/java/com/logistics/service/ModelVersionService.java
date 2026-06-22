package com.logistics.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.logistics.entity.ModelVersion;
import com.logistics.mapper.ModelVersionMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

/**
 * 模型版本服务
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ModelVersionService {

    private final ModelVersionMapper modelMapper;
    private static final String MODEL_DIR = "./models/";

    /**
     * 查询所有版本
     */
    public List<ModelVersion> listAll() {
        return modelMapper.selectList(new LambdaQueryWrapper<ModelVersion>().orderByDesc(ModelVersion::getCreateTime));
    }

    /**
     * 获取活跃模型
     */
    public ModelVersion getActiveModel() {
        return modelMapper.selectOne(new LambdaQueryWrapper<ModelVersion>().eq(ModelVersion::getIsActive, true));
    }

    /**
     * 上传模型文件
     */
    @Transactional(rollbackFor = Exception.class)
    public ModelVersion uploadModel(MultipartFile file, String version, String description, String metricsJson) throws IOException {
        // 检查版本号唯一性
        if (modelMapper.exists(new LambdaQueryWrapper<ModelVersion>().eq(ModelVersion::getVersion, version))) {
            throw new RuntimeException("版本号已存在");
        }

        // 创建目录
        File dir = new File(MODEL_DIR);
        if (!dir.exists()) {
            dir.mkdirs();
        }

        // 保存文件
        String fileName = version + ".pt";
        Path filePath = Paths.get(MODEL_DIR, fileName);
        Files.write(filePath, file.getBytes());

        // 入库
        ModelVersion model = new ModelVersion();
        model.setVersion(version);
        model.setFilePath(filePath.toString());
        model.setFileSize(file.getSize());
        model.setIsActive(false);
        model.setMetricsJson(metricsJson);
        model.setDescription(description);

        modelMapper.insert(model);
        log.info("模型上传成功：{}", version);
        return model;
    }

    /**
     * 激活模型
     */
    @Transactional(rollbackFor = Exception.class)
    public void activateModel(Long id) {
        // 取消所有活跃状态
        List<ModelVersion> activeModels = modelMapper.selectList(new LambdaQueryWrapper<ModelVersion>().eq(ModelVersion::getIsActive, true));
        for (ModelVersion model : activeModels) {
            model.setIsActive(false);
            modelMapper.updateById(model);
        }

        // 激活指定模型
        ModelVersion target = modelMapper.selectById(id);
        if (target == null) {
            throw new RuntimeException("模型不存在");
        }
        target.setIsActive(true);
        modelMapper.updateById(target);

        log.info("模型{}已激活", target.getVersion());
    }

    /**
     * 删除模型
     */
    @Transactional(rollbackFor = Exception.class)
    public void deleteModel(Long id) {
        ModelVersion model = modelMapper.selectById(id);
        if (model == null) {
            throw new RuntimeException("模型不存在");
        }

        if (model.getIsActive()) {
            throw new RuntimeException("不能删除活跃模型");
        }

        // 删除文件
        try {
            Files.deleteIfExists(Paths.get(model.getFilePath()));
        } catch (IOException e) {
            log.error("删除模型文件失败", e);
        }

        // 删除记录
        modelMapper.deleteById(id);
        log.info("模型{}已删除", model.getVersion());
    }
}
