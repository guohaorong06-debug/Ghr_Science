"""
绘制训练曲线和Loss分析
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文显示
plt.rcParams['axes.unicode_minus'] = False

def plot_model_comparison():
    """绘制模型对比柱状图"""
    # 读取所有结果
    results = {}
    baseline_dir = Path("../experiments/baseline")

    models = ['lstm', 'gru', 'transformer', 'arima', 'prophet']
    for model in models:
        result_file = baseline_dir / model / "result.json"
        if result_file.exists():
            with open(result_file) as f:
                data = json.load(f)
                results[model.upper()] = data['metrics']

    # Proposed模型
    proposed_file = Path("../experiments/proposed/result.json")
    if proposed_file.exists():
        with open(proposed_file) as f:
            data = json.load(f)
            results['Proposed'] = data['metrics']

    # 绘图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    models_list = list(results.keys())
    mae_values = [results[m]['MAE'] for m in models_list]
    rmse_values = [results[m]['RMSE'] for m in models_list]

    # MAE对比
    colors = ['#3498db' if m != 'Proposed' else '#e74c3c' for m in models_list]
    ax1.bar(models_list, mae_values, color=colors, alpha=0.7)
    ax1.set_ylabel('MAE', fontsize=12)
    ax1.set_title('Model Comparison - MAE', fontsize=14, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # RMSE对比
    ax2.bar(models_list, rmse_values, color=colors, alpha=0.7)
    ax2.set_ylabel('RMSE', fontsize=12)
    ax2.set_title('Model Comparison - RMSE', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    # 保存
    output_dir = Path("../outputs/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / "model_comparison.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "model_comparison.pdf", bbox_inches='tight')
    print(f"[SUCCESS] 保存模型对比图: {output_dir / 'model_comparison.png'}")
    plt.close()


def plot_ablation_study():
    """绘制消融实验结果"""
    # 读取消融实验结果
    ablation_dir = Path("../experiments/ablation")

    results = {
        'Proposed (Full)': None,
        'w/o GraphVAE': None,
        'w/o NormalizingFlow': None
    }

    # Proposed完整模型
    proposed_file = Path("../experiments/proposed/result.json")
    if proposed_file.exists():
        with open(proposed_file) as f:
            results['Proposed (Full)'] = json.load(f)['metrics']['MAE']

    # 无GraphVAE
    no_gvae_file = ablation_dir / "without_graphvae.json"
    if no_gvae_file.exists():
        with open(no_gvae_file) as f:
            results['w/o GraphVAE'] = json.load(f)['metrics']['MAE']

    # 过滤None
    results = {k: v for k, v in results.items() if v is not None}

    if len(results) > 1:
        fig, ax = plt.subplots(figsize=(8, 6))

        models = list(results.keys())
        mae_values = list(results.values())

        colors = ['#27ae60' if 'Full' in m else '#95a5a6' for m in models]
        bars = ax.barh(models, mae_values, color=colors, alpha=0.7)

        ax.set_xlabel('MAE (Lower is Better)', fontsize=12)
        ax.set_title('Ablation Study - Component Contribution', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        # 添加数值标签
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   f'{width:.4f}', ha='left', va='center', fontsize=10)

        plt.tight_layout()

        output_dir = Path("../outputs/figures")
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_dir / "ablation_study.png", dpi=300, bbox_inches='tight')
        plt.savefig(output_dir / "ablation_study.pdf", bbox_inches='tight')
        print(f"[SUCCESS] 保存消融实验图: {output_dir / 'ablation_study.png'}")
        plt.close()


def main():
    print("=" * 60)
    print("绘制训练曲线和分析图")
    print("=" * 60)

    print("\n1. 绘制模型对比图...")
    plot_model_comparison()

    print("\n2. 绘制消融实验图...")
    plot_ablation_study()

    print("\n[SUCCESS] 所有图表生成完成！")
    print("输出目录: research/outputs/figures/")


if __name__ == "__main__":
    main()
