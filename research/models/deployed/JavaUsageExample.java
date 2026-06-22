
// Java后端调用TorchScript模型示例

import ai.djl.Model;
import ai.djl.inference.Predictor;
import ai.djl.ndarray.NDArray;
import ai.djl.ndarray.NDList;
import ai.djl.ndarray.NDManager;
import ai.djl.translate.Batchifier;
import ai.djl.translate.Translator;
import ai.djl.translate.TranslatorContext;

public class LogisticsForecastService {

    private Model model;
    private Predictor<float[][], float[][]> predictor;

    public void loadModel(String modelPath) throws Exception {
        model = Model.newInstance("lstm_model");
        model.load(Paths.get(modelPath));

        predictor = model.newPredictor(new ForecastTranslator());
    }

    public float[][] predict(float[][] historyData) throws Exception {
        // historyData: [14, 60] - 14天历史，60个网格
        return predictor.predict(historyData);
    }

    static class ForecastTranslator implements Translator<float[][], float[][]> {

        @Override
        public NDList processInput(TranslatorContext ctx, float[][] input) {
            NDManager manager = ctx.getNDManager();
            // 转换为 [1, 14, 60] 张量
            NDArray array = manager.create(input).expandDims(0);
            return new NDList(array);
        }

        @Override
        public float[][] processOutput(TranslatorContext ctx, NDList list) {
            // 输出 [1, 7, 60] -> [7, 60]
            NDArray output = list.singletonOrThrow();
            return output.squeeze(0).toFloatArray();
        }

        @Override
        public Batchifier getBatchifier() {
            return Batchifier.STACK;
        }
    }
}

// 使用示例
public class Main {
    public static void main(String[] args) throws Exception {
        LogisticsForecastService service = new LogisticsForecastService();
        service.loadModel("models/deployed/lstm_torchscript.pt");

        // 14天历史数据
        float[][] historyData = new float[14][60];
        // ... 填充数据 ...

        // 预测未来7天
        float[][] forecast = service.predict(historyData);
        // forecast: [7, 60] - 7天预测，60个网格
    }
}
