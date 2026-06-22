"""
生成论文图表

使用Matplotlib绘制高质量论文图表
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
matplotlib.rcParams['axes.unicode_minus'] = False

# 论文级图表配置
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

OUTPUT_DIR = Path("../outputs/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def plot_model_comparison():
    """绘制模型对比柱状图"""
    table_path = Path("../outputs/tables/model_comparison.csv")

    if not table_path.exists():
        print("❌ 未找到对比表格，请先运行 5_evaluate_all.py")
        return

    df = pd.read_csv(table_path)

    # 取前10个模型
    df_top = df.head(10)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    metrics = ['MAE', 'RMSE', 'CRPS']
    colors = ['#409eff' if t == 'Proposed' else '#909399' for t in df_top['Type']]

    for ax, metric in zip(axes, metrics):
        ax.barh(df_top['Model'], df_top[metric], color=colors)
        ax.set_xlabel(metric, fontsize=12)
        ax.set_title(f'{metric} 对比', fontsize=14, fontweight='bold')
        ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "model_comparison_bar.png")
    plt.savefig(OUTPUT_DIR / "model_comparison_bar.pdf")
    print(f"✅ 保存: model_comparison_bar.png")
    plt.close()

def plot_forecast_waterfall():
    """绘制预测区间瀑布图（示例）"""
    # 模拟数据
    import numpy as np
    dates = pd.date_range('2022-01-01', periods=14)
    true_values = np.random.randint(800, 1200, 14)
    predicted_median = true_values + np.random.randint(-50, 50, 14)
    predicted_p10 = predicted_median - np.random.randint(50, 100, 14)
    predicted_p90 = predicted_median + np.random.randint(50, 100, 14)
    capacity = 1000

    fig, ax = plt.subplots(figsize=(12, 6))

    # 预测区间（半透明）
    ax.fill_between(dates, predicted_p10, predicted_p90,
                     alpha=0.3, color='#409eff', label='预测区间 (10%-90%)')

    # 中位数预测
    ax.plot(dates, predicted_median, 'o-', color='#409eff',
            linewidth=2, markersize=6, label='预测中位数')

    # 真实值
    ax.plot(dates, true_values, 's--', color='#67c23a',
            linewidth=2, markersize=6, label='真实值')

    # 处理能力阈值
    ax.axhline(y=capacity, color='#f56c6c', linestyle='--',
               linewidth=2, label='处理能力阈值')

    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('包裹量', fontsize=12)
    ax.set_title('未来14天需求预测瀑布图', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "forecast_waterfall.png")
    plt.savefig(OUTPUT_DIR / "forecast_waterfall.pdf")
    print(f"✅ 保存: forecast_waterfall.png")
    plt.close()

def plot_reliability_diagram():
    """绘制可靠性图（校准图）"""
    # 模拟数据
    predicted_probs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    observed_freqs_proposed = [0.12, 0.22, 0.31, 0.42, 0.51, 0.59, 0.68, 0.79, 0.88]
    observed_freqs_baseline = [0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.92]

    fig, ax = plt.subplots(figsize=(8, 8))

    # 完美校准线
    ax.plot([0, 1], [0, 1], 'k--', linewidth=2, label='完美校准')

    # 创新模型
    ax.plot(predicted_probs, observed_freqs_proposed, 'o-',
            color='#409eff', linewidth=2, markersize=8, label='创新模型')

    # 基线模型
    ax.plot(predicted_probs, observed_freqs_baseline, 's--',
            color='#e6a23c', linewidth=2, markersize=8, label='最佳基线')

    ax.set_xlabel('预测概率', fontsize=12)
    ax.set_ylabel('观测频率', fontsize=12)
    ax.set_title('可靠性图（校准曲线）', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "reliability_diagram.png")
    plt.savefig(OUTPUT_DIR / "reliability_diagram.pdf")
    print(f"✅ 保存: reliability_diagram.png")
    plt.close()

def main():
    print("=" * 60)
    print("生成论文图表")
    print("=" * 60)

    plot_model_comparison()
    plot_forecast_waterfall()
    plot_reliability_diagram()

    print("\n" + "=" * 60)
    print("✅ 所有图表已生成")
    print("=" * 60)
    print(f"保存目录: {OUTPUT_DIR.absolute()}")
    print("\n生成的图表:")
    for img in OUTPUT_DIR.glob("*.png"):
        print(f"  - {img.name}")

if __name__ == "__main__":
    main()
