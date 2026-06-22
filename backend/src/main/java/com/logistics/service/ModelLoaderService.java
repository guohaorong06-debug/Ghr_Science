package com.logistics.service;

import ai.djl.MalformedModelException;
import ai.djl.Model;
import ai.djl.inference.Predictor;
import ai.djl.ndarray.NDArray;
import ai.djl.ndarray.NDList;
import ai.djl.ndarray.NDManager;
import ai.djl.translate.Batchifier;
import ai.djl.translate.Translator;
import ai.djl.translate.TranslatorContext;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import jakarta.annotation.PostConstruct;
import java.io.IOException;
import java.nio.file.Paths;

/**
 * 模型加载服务
 *
 * 加载TorchScript模型用于预测
 */
@Slf4j
@Service
public class ModelLoaderService {

    private Model lstmModel;
    private Model gruModel;
    private Model transformerModel;

    private Predictor<float[][], float[][]> lstmPredictor;
    private Predictor<float[][], float[][]> gruPredictor;
    private Predictor<float[][], float[][]> transformerPredictor;

    @PostConstruct
    public void init() {
        try {
            log.info("开始加载TorchScript模型...");

            // 加载LSTM模型
            lstmModel = Model.newInstance("lstm");
            lstmModel.load(Paths.get("models/lstm_torchscript.pt"));
            lstmPredictor = lstmModel.newPredictor(new ForecastTranslator());
            log.info("✅ LSTM模型加载成功");

            // 加载GRU模型
            gruModel = Model.newInstance("gru");
            gruModel.load(Paths.get("models/gru_torchscript.pt"));
            gruPredictor = gruModel.newPredictor(new ForecastTranslator());
            log.info("✅ GRU模型加载成功");

            // 加载Transformer模型
            transformerModel = Model.newInstance("transformer");
            transformerModel.load(Paths.get("models/transformer_torchscript.pt"));
            transformerPredictor = transformerModel.newPredictor(new ForecastTranslator());
            log.info("✅ Transformer模型加载成功");

            log.info("所有模型加载完成！");

        } catch (MalformedModelException | IOException e) {
            log.error("模型加载失败", e);
            throw new RuntimeException("模型加载失败: " + e.getMessage(), e);
        }
    }

    public Predictor<float[][], float[][]> getLSTMPredictor() {
        return lstmPredictor;
    }

    public Predictor<float[][], float[][]> getGRUPredictor() {
        return gruPredictor;
    }

    public Predictor<float[][], float[][]> getTransformerPredictor() {
        return transformerPredictor;
    }

    /**
     * 预测Translator
     *
     * 将输入数据转换为NDArray，将输出NDArray转换为float数组
     */
    static class ForecastTranslator implements Translator<float[][], float[][]> {

        @Override
        public NDList processInput(TranslatorContext ctx, float[][] input) {
            NDManager manager = ctx.getNDManager();

            // input: [14, 60] -> [1, 14, 60]
            NDArray array = manager.create(input).expandDims(0);

            return new NDList(array);
        }

        @Override
        public float[][] processOutput(TranslatorContext ctx, NDList list) {
            NDArray output = list.singletonOrThrow();

            // output: [1, 7, 60] -> [7, 60]
            output = output.squeeze(0);

            // 转换为二维数组
            long[] shape = output.getShape().getShape();
            int rows = (int) shape[0];
            int cols = (int) shape[1];

            float[][] result = new float[rows][cols];
            float[] flatArray = output.toFloatArray();

            for (int i = 0; i < rows; i++) {
                System.arraycopy(flatArray, i * cols, result[i], 0, cols);
            }

            return result;
        }

        @Override
        public Batchifier getBatchifier() {
            return Batchifier.STACK;
        }
    }
}
