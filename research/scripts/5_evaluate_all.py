"""
统一评估脚本：对比所有模型结果

读取 experiments/ 中的所有实验结果，生成对比表格
"""

import json
from pathlib import Path
import pandas as pd

def load_baseline_results():
    """加载所有基线模型结果"""
    baseline_dir = Path("../experiments/baseline")
    results_file = baseline_dir / "results.json"

    if results_file.exists():
        with open(results_file) as f:
            data = json.load(f)
            return data.get('results', [])
    return []

def load_proposed_result():
    """加载创新模型结果"""
    proposed_file = Path("../experiments/proposed/result.json")

    if proposed_file.exists():
        with open(proposed_file) as f:
            return json.load(f)
    return None

def calculate_improvements(proposed, baseline_results):
    """计算相对改进"""
    # 找到最好的基线模型
    best_baseline = min(baseline_results, key=lambda x: x['metrics']['CRPS'])

    improvements = {}
    for metric in ['MAE', 'RMSE', 'CRPS']:
        baseline_val = best_baseline['metrics'][metric]
        proposed_val = proposed['metrics'][metric]
        improvement = ((baseline_val - proposed_val) / baseline_val) * 100
        improvements[metric] = {
            'baseline_value': baseline_val,
            'proposed_value': proposed_val,
            'improvement_percent': round(improvement, 2)
        }

    return improvements, best_baseline['model']

def main():
    print("=" * 80)
    print("模型评估与对比")
    print("=" * 80)

    # 加载结果
    baseline_results = load_baseline_results()
    proposed_result = load_proposed_result()

    if not baseline_results:
        print("❌ 未找到基线模型结果，请先运行 3_train_baseline.py")
        return

    print(f"\n基线模型: {len(baseline_results)} 个")

    # 创建对比表格
    comparison_data = []

    for result in baseline_results:
        comparison_data.append({
            'Model': result['model'],
            'MAE': result['metrics']['MAE'],
            'RMSE': result['metrics']['RMSE'],
            'CRPS': result['metrics']['CRPS'],
            'PICP_90': result['metrics']['PICP_90'],
            'MPIW_90': result['metrics']['MPIW_90'],
            'Type': 'Baseline'
        })

    if proposed_result:
        comparison_data.append({
            'Model': 'ProposedModel',
            'MAE': proposed_result['metrics']['MAE'],
            'RMSE': proposed_result['metrics']['RMSE'],
            'CRPS': proposed_result['metrics']['CRPS'],
            'PICP_90': proposed_result['metrics']['PICP_90'],
            'MPIW_90': proposed_result['metrics']['MPIW_90'],
            'Type': 'Proposed'
        })

    df = pd.DataFrame(comparison_data)

    # 按CRPS排序
    df = df.sort_values('CRPS')

    # 保存CSV
    output_dir = Path("../outputs/tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "model_comparison.csv"
    df.to_csv(csv_path, index=False)

    # 显示结果
    print("\n" + "=" * 80)
    print("模型对比表 (按CRPS排序)")
    print("=" * 80)
    print(df.to_string(index=False))

    # 计算改进
    if proposed_result:
        improvements, best_baseline_name = calculate_improvements(proposed_result, baseline_results)

        print("\n" + "=" * 80)
        print(f"相对最佳基线模型 ({best_baseline_name}) 的改进")
        print("=" * 80)

        for metric, values in improvements.items():
            print(f"\n{metric}:")
            print(f"  基线值: {values['baseline_value']:.2f}")
            print(f"  提出值: {values['proposed_value']:.2f}")
            print(f"  改进: {values['improvement_percent']:.2f}%")

        # 保存改进结果
        with open(output_dir / "improvements.json", "w") as f:
            json.dump({
                'best_baseline': best_baseline_name,
                'improvements': improvements,
                'timestamp': pd.Timestamp.now().isoformat()
            }, f, indent=2)

    # 生成LaTeX表格
    latex_path = output_dir / "model_comparison.tex"
    with open(latex_path, "w") as f:
        f.write("\\begin{table}[htbp]\n")
        f.write("\\centering\n")
        f.write("\\caption{模型性能对比}\n")
        f.write("\\label{tab:model_comparison}\n")
        f.write("\\begin{tabular}{lrrrrr}\n")
        f.write("\\hline\n")
        f.write("Model & MAE & RMSE & CRPS & PICP\\textsubscript{90} & MPIW\\textsubscript{90} \\\\\n")
        f.write("\\hline\n")

        for _, row in df.iterrows():
            model_name = row['Model'].replace('_', '\\_')
            if row['Type'] == 'Proposed':
                f.write(f"\\textbf{{{model_name}}} & ")
            else:
                f.write(f"{model_name} & ")

            f.write(f"{row['MAE']:.2f} & {row['RMSE']:.2f} & {row['CRPS']:.2f} & ")
            f.write(f"{row['PICP_90']:.3f} & {row['MPIW_90']:.2f} \\\\\n")

        f.write("\\hline\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")

    print("\n" + "=" * 80)
    print("✅ 评估完成")
    print("=" * 80)
    print(f"CSV表格: {csv_path}")
    print(f"LaTeX表格: {latex_path}")
    if proposed_result:
        print(f"改进统计: {output_dir / 'improvements.json'}")

if __name__ == "__main__":
    main()
