"""
一键启动所有模型训练脚本

按顺序训练所有基线模型和创新模型
"""

import subprocess
import time
from pathlib import Path
from datetime import datetime
import json

# 所有训练脚本列表
TRAINING_SCRIPTS = [
    # 简单基线模型（快速）
    ("LSTM", "train_lstm_real.py", "10-20分钟"),
    ("GRU", "train_gru_real.py", "10-20分钟"),

    # 注意力机制模型（中等）
    ("Transformer", "train_transformer_real.py", "15-25分钟"),

    # 创新模型（复杂）
    ("Proposed (GraphVAE+Flow)", "train_proposed_real.py", "30-60分钟"),
]

def run_training(model_name, script_name):
    """运行单个训练脚本"""
    print("\n" + "=" * 70)
    print(f"开始训练: {model_name}")
    print(f"脚本: {script_name}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    start_time = time.time()

    try:
        # 运行训练脚本
        result = subprocess.run(
            ["python", script_name],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        # 打印输出
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)

        elapsed_time = time.time() - start_time
        minutes = elapsed_time / 60

        if result.returncode == 0:
            print(f"\n✅ {model_name} 训练成功！耗时: {minutes:.1f}分钟")
            return True, elapsed_time
        else:
            print(f"\n❌ {model_name} 训练失败！")
            return False, elapsed_time

    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ {model_name} 训练出错: {e}")
        return False, elapsed_time


def main():
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "        🚀 一键启动所有模型训练 🚀".center(76) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    print(f"\n训练计划:")
    print("-" * 70)
    for i, (name, script, duration) in enumerate(TRAINING_SCRIPTS, 1):
        print(f"{i}. {name:<30} {script:<30} 预计: {duration}")
    print("-" * 70)

    total_estimated = "约1.5-2.5小时"
    print(f"\n总预计时间: {total_estimated}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    input("\n按Enter键开始训练...")

    # 记录结果
    results = []
    total_start_time = time.time()

    # 逐个训练
    for i, (model_name, script_name, _) in enumerate(TRAINING_SCRIPTS, 1):
        print(f"\n进度: [{i}/{len(TRAINING_SCRIPTS)}]")
        success, elapsed = run_training(model_name, script_name)

        results.append({
            "model": model_name,
            "script": script_name,
            "success": success,
            "time_minutes": round(elapsed / 60, 2)
        })

        # 短暂休息
        if i < len(TRAINING_SCRIPTS):
            print("\n等待5秒后继续...")
            time.sleep(5)

    # 总结
    total_elapsed = time.time() - total_start_time
    total_minutes = total_elapsed / 60

    print("\n\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "        📊 训练完成总结 📊".center(76) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    print(f"\n总耗时: {total_minutes:.1f}分钟 ({total_minutes/60:.1f}小时)")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n训练结果:")
    print("-" * 70)

    success_count = 0
    for r in results:
        status = "✅ 成功" if r['success'] else "❌ 失败"
        print(f"{r['model']:<35} {status:<10} {r['time_minutes']:.1f}分钟")
        if r['success']:
            success_count += 1

    print("-" * 70)
    print(f"\n成功: {success_count}/{len(TRAINING_SCRIPTS)}")

    # 保存训练摘要
    summary = {
        "total_time_minutes": round(total_minutes, 2),
        "success_count": success_count,
        "total_models": len(TRAINING_SCRIPTS),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

    summary_path = Path("../experiments/training_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n训练摘要已保存: {summary_path}")

    # 检查生成的模型文件
    print("\n生成的模型文件:")
    models_dir = Path("../models")
    if models_dir.exists():
        model_files = list(models_dir.glob("*_best.pt"))
        for mf in model_files:
            size_mb = mf.stat().st_size / 1024 / 1024
            print(f"  ✅ {mf.name} ({size_mb:.1f} MB)")

    print("\n🎉 所有训练任务完成！")
    print("\n下一步:")
    print("  1. 查看结果: cat ../experiments/*/result.json")
    print("  2. 生成对比: python 5_evaluate_all.py")
    print("  3. 生成图表: python 6_generate_plots.py")


if __name__ == "__main__":
    main()
