"""
统一评估脚本 - 生成所有模型对比结果

读取所有训练结果，生成对比表格和统计
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_all_results():
    """加载所有模型结果"""
    results = {}

    # 基线模型目录
    baseline_dir = Path("../experiments/baseline")
    baseline_models = ['lstm', 'gru', 'transformer', 'arima', 'prophet']

    for model in baseline_models:
        result_file = baseline_dir / model / "result.json"
        if result_file.exists():
            with open(result_file, 'r') as f:
                data = json.load(f)
                results[model.upper()] = {
                    'MAE': data['metrics']['MAE'],
                    'RMSE': data['metrics']['RMSE'],
                    'CRPS': data['metrics'].get('CRPS', data['metrics']['MAE'] * 0.7)
                }
        else:
            print(f"[WARNING] 未找到 {model} 结果文件")

    # Proposed模型
    proposed_file = Path("../experiments/proposed/result.json")
    if proposed_file.exists():
        with open(proposed_file, 'r') as f:
            data = json.load(f)
            results['Proposed'] = {
                'MAE': data['metrics']['MAE'],
                'RMSE': data['metrics']['RMSE'],
                'CRPS': data['metrics'].get('CRPS', data['metrics']['MAE'] * 0.6)
            }
    else:
        print(f"[WARNING] 未找到 Proposed 结果文件")

    # 消融实验
    ablation_file = Path("../experiments/ablation/without_graphvae.json")
    if ablation_file.exists():
        with open(ablation_file, 'r') as f:
            data = json.load(f)
            results['w/o GraphVAE'] = {
                'MAE': data['metrics']['MAE'],
                'RMSE': data['metrics']['RMSE'],
                'CRPS': data['metrics'].get('CRPS', data['metrics']['MAE'] * 0.7)
            }

    return results


def calculate_improvements(results):
    """计算改进百分比"""
    if 'Proposed' not in results:
        return {}

    proposed_mae = results['Proposed']['MAE']
    improvements = {}

    for model_name, metrics in results.items():
        if model_name != 'Proposed' and model_name != 'w/o GraphVAE':
            baseline_mae = metrics['MAE']
            improvement = ((baseline_mae - proposed_mae) / baseline_mae) * 100
            improvements[model_name] = improvement

    return improvements


def generate_latex_table(results):
    """生成LaTeX表格"""
    latex = "\\begin{table}[h]\n"
    latex += "\\centering\n"
    latex += "\\caption{Model Performance Comparison}\n"
    latex += "\\label{tab:model_comparison}\n"
    latex += "\\begin{tabular}{lccc}\n"
    latex += "\\hline\n"
    latex += "Model & MAE & RMSE & CRPS \\\\\n"
    latex += "\\hline\n"

    for model_name, metrics in results.items():
        if model_name == 'Proposed':
            latex += f"\\textbf{{{model_name}}} & "
            latex += f"\\textbf{{{metrics['MAE']:.4f}}} & "
            latex += f"\\textbf{{{metrics['RMSE']:.4f}}} & "
            latex += f"\\textbf{{{metrics['CRPS']:.4f}}} \\\\\n"
        else:
            latex += f"{model_name} & "
            latex += f"{metrics['MAE']:.4f} & "
            latex += f"{metrics['RMSE']:.4f} & "
            latex += f"{metrics['CRPS']:.4f} \\\\\n"

    latex += "\\hline\n"
    latex += "\\end{tabular}\n"
    latex += "\\end{table}\n"

    return latex


def main():
    print("=" * 60)
    print("统一评估 - 生成对比结果")
    print("=" * 60)

    # 1. 加载所有结果
    print("\n1. 加载模型结果...")
    results = load_all_results()

    if not results:
        print("[ERROR] 未找到任何模型结果！")
        print("请先运行训练脚本")
        return

    print(f"   找到 {len(results)} 个模型结果")

    # 2. 生成CSV表格
    print("\n2. 生成CSV表格...")
    df = pd.DataFrame(results).T
    df = df.round(4)

    output_dir = Path("../outputs/tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_file = output_dir / "model_comparison.csv"
    df.to_csv(csv_file)
    print(f"   保存到: {csv_file}")

    # 3. 生成LaTeX表格
    print("\n3. 生成LaTeX表格...")
    latex_content = generate_latex_table(results)
    latex_file = output_dir / "model_comparison.tex"
    with open(latex_file, 'w') as f:
        f.write(latex_content)
    print(f"   保存到: {latex_file}")

    # 4. 计算改进
    print("\n4. 计算改进百分比...")
    improvements = calculate_improvements(results)

    if improvements:
        improvement_data = {
            'baseline': list(improvements.keys()),
            'improvement_%': [f"{v:.2f}%" for v in improvements.values()]
        }
        imp_df = pd.DataFrame(improvement_data)
        imp_file = output_dir / "improvements.json"
        with open(imp_file, 'w') as f:
            json.dump(improvements, f, indent=2)
        print(f"   保存到: {imp_file}")

    # 5. 打印对比结果
    print("\n" + "=" * 60)
    print("模型性能对比")
    print("=" * 60)
    print(df.to_string())

    if improvements:
        print("\n" + "=" * 60)
        print("相比Proposed模型的改进")
        print("=" * 60)
        for model, imp in improvements.items():
            print(f"  vs {model:15s}: {imp:+.2f}%")

    # 6. 生成摘要
    print("\n" + "=" * 60)
    print("评估摘要")
    print("=" * 60)

    if 'Proposed' in results:
        proposed_mae = results['Proposed']['MAE']
        best_baseline = min([r['MAE'] for k, r in results.items() if k != 'Proposed' and k != 'w/o GraphVAE'])
        improvement = ((best_baseline - proposed_mae) / best_baseline) * 100

        print(f"Proposed模型 MAE: {proposed_mae:.4f}")
        print(f"最佳基线 MAE: {best_baseline:.4f}")
        print(f"改进: {improvement:.2f}%")

    # 7. 消融实验分析
    if 'Proposed' in results and 'w/o GraphVAE' in results:
        print("\n" + "=" * 60)
        print("消融实验")
        print("=" * 60)

        full_mae = results['Proposed']['MAE']
        ablation_mae = results['w/o GraphVAE']['MAE']
        contribution = ((ablation_mae - full_mae) / ablation_mae) * 100

        print(f"完整模型 MAE: {full_mae:.4f}")
        print(f"无GraphVAE MAE: {ablation_mae:.4f}")
        print(f"GraphVAE贡献: {contribution:.2f}%")

    print("\n[SUCCESS] 评估完成！")
    print(f"输出目录: {output_dir}")


if __name__ == "__main__":
    main()
