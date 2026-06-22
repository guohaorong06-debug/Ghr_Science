% 论文数据分析脚本
% 用于加载和分析实验结果

%% 1. 加载模型对比结果
clear; clc;

fprintf('===========================================\n');
fprintf('论文数据分析 - 模型对比\n');
fprintf('===========================================\n\n');

% 读取CSV结果
results_file = '../outputs/tables/model_comparison.csv';

if exist(results_file, 'file')
    % 读取数据
    data = readtable(results_file);
    fprintf('[SUCCESS] 成功加载实验结果\n\n');

    % 显示数据
    disp(data);

    %% 2. 提取指标
    model_names = data.Var1;  % 第一列是模型名称
    mae = data.MAE;
    rmse = data.RMSE;
    crps = data.CRPS;

    %% 3. 生成对比图表
    figure('Position', [100, 100, 1200, 400]);

    % 子图1: MAE对比
    subplot(1, 3, 1);
    bar(mae);
    set(gca, 'XTickLabel', model_names, 'XTickLabelRotation', 45);
    ylabel('MAE', 'FontSize', 12, 'FontWeight', 'bold');
    title('(a) Mean Absolute Error', 'FontSize', 12, 'FontWeight', 'bold');
    grid on;

    % 子图2: RMSE对比
    subplot(1, 3, 2);
    bar(rmse);
    set(gca, 'XTickLabel', model_names, 'XTickLabelRotation', 45);
    ylabel('RMSE', 'FontSize', 12, 'FontWeight', 'bold');
    title('(b) Root Mean Square Error', 'FontSize', 12, 'FontWeight', 'bold');
    grid on;

    % 子图3: CRPS对比
    subplot(1, 3, 3);
    bar(crps);
    set(gca, 'XTickLabel', model_names, 'XTickLabelRotation', 45);
    ylabel('CRPS', 'FontSize', 12, 'FontWeight', 'bold');
    title('(c) CRPS', 'FontSize', 12, 'FontWeight', 'bold');
    grid on;

    % 保存图表
    output_file = '../outputs/figures/matlab_model_comparison.png';
    saveas(gcf, output_file);
    fprintf('[SUCCESS] 图表已保存: %s\n', output_file);

    %% 4. 统计分析
    fprintf('\n统计分析:\n');
    fprintf('------------------------------------------\n');

    % 找出最佳模型
    [min_mae, idx_mae] = min(mae);
    [min_rmse, idx_rmse] = min(rmse);
    [min_crps, idx_crps] = min(crps);

    % 获取模型名称
    model_names = data.Var1;

    fprintf('最佳MAE: %s (%.4f)\n', model_names{idx_mae}, min_mae);
    fprintf('最佳RMSE: %s (%.4f)\n', model_names{idx_rmse}, min_rmse);
    fprintf('最佳CRPS: %s (%.4f)\n', model_names{idx_crps}, min_crps);

    %% 5. 计算改进百分比
    fprintf('\n改进分析 (相比Proposed):\n');
    fprintf('------------------------------------------\n');

    % 假设Proposed是最后一个
    proposed_idx = length(mae);
    proposed_mae = mae(proposed_idx);

    for i = 1:length(mae)-1
        improvement = ((mae(i) - proposed_mae) / mae(i)) * 100;
        fprintf('%s: %.2f%%\n', model_names{i}, improvement);
    end

else
    fprintf('[ERROR] 未找到结果文件: %s\n', results_file);
    fprintf('[INFO] 请先运行 Python 训练脚本生成结果\n');
end

fprintf('\n===========================================\n');
fprintf('分析完成\n');
fprintf('===========================================\n');
