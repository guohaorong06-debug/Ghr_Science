"""
一键启动所有模型训练脚本（修复版）

优化：
- 修复编码问题
- 实时显示训练进度
- 不使用emoji特殊字符
"""

import subprocess
import time
from pathlib import Path
from datetime import datetime
import json
import sys

# 所有训练脚本列表
TRAINING_SCRIPTS = [
    ("LSTM", "train_lstm_real.py", "10-20分钟"),
    ("GRU", "train_gru_real.py", "10-20分钟"),
    ("Transformer", "train_transformer_real.py", "15-25分钟"),
    ("Proposed (GraphVAE+Flow)", "train_proposed_real.py", "30-60分钟"),
]

def run_training(model_name, script_name):
    """运行单个训练脚本 - 实时显示输出"""
    print("\n" + "=" * 70)
    print(f"开始训练: {model_name}")
    print(f"脚本: {script_name}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

    start_time = time.time()

    try:
        # 实时显示输出
        process = subprocess.Popen(
            ["python", "-u", script_name],  # -u 参数确保实时输出
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore',
            bufsize=1,
            universal_newlines=True
        )

        # 实时读取并打印输出
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                sys.stdout.flush()

        # 等待进程完成
        return_code = process.wait()

        # 读取剩余错误输出
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"\n[WARNING] 有警告信息:\n{stderr_output}")

        elapsed_time = time.time() - start_time
        minutes = elapsed_time / 60

        if return_code == 0:
            print(f"\n[SUCCESS] {model_name} 训练成功！耗时: {minutes:.1f}分钟")
            return True, elapsed_time
        else:
            print(f"\n[ERROR] {model_name} 训练失败！返回码: {return_code}")
            return False, elapsed_time

    except KeyboardInterrupt:
        print(f"\n\n[INTERRUPTED] 用户中断训练！")
        process.kill()
        raise
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n[ERROR] {model_name} 训练出错: {e}")
        return False, elapsed_time


def main():
    print("=" * 70)
    print("       一键启动所有模型训练")
    print("=" * 70)

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
        print(f"\n{'='*70}")
        print(f"进度: [{i}/{len(TRAINING_SCRIPTS)}]")
        print(f"{'='*70}")

        try:
            success, elapsed = run_training(model_name, script_name)

            results.append({
                "model": model_name,
                "script": script_name,
                "success": success,
                "time_minutes": round(elapsed / 60, 2)
            })

            # 短暂休息
            if i < len(TRAINING_SCRIPTS):
                print("\n等待3秒后继续...")
                time.sleep(3)

        except KeyboardInterrupt:
            print("\n\n[INTERRUPTED] 训练被用户中断！")
            print(f"已完成 {i-1}/{len(TRAINING_SCRIPTS)} 个模型")
            break

    # 总结
    total_elapsed = time.time() - total_start_time
    total_minutes = total_elapsed / 60

    print("\n\n")
    print("=" * 70)
    print("       训练完成总结")
    print("=" * 70)

    print(f"\n总耗时: {total_minutes:.1f}分钟 ({total_minutes/60:.1f}小时)")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n训练结果:")
    print("-" * 70)

    success_count = 0
    for r in results:
        status = "[SUCCESS]" if r['success'] else "[FAILED]"
        print(f"{r['model']:<35} {status:<15} {r['time_minutes']:.1f}分钟")
        if r['success']:
            success_count += 1

    print("-" * 70)
    print(f"\n成功: {success_count}/{len(results)}")

    # 保存训练摘要
    summary = {
        "total_time_minutes": round(total_minutes, 2),
        "success_count": success_count,
        "total_models": len(results),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

    summary_path = Path("../experiments/training_summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n训练摘要已保存: {summary_path}")

    # 检查生成的模型文件
    print("\n生成的模型文件:")
    models_dir = Path("../models")
    models_dir.mkdir(exist_ok=True)
    model_files = list(models_dir.glob("*_best.pt"))
    if model_files:
        for mf in model_files:
            size_mb = mf.stat().st_size / 1024 / 1024
            print(f"  [OK] {mf.name} ({size_mb:.1f} MB)")
    else:
        print("  [WARNING] 未找到模型文件")

    print("\n[COMPLETE] 所有训练任务完成！")
    print("\n下一步:")
    print("  1. 查看结果: cat ../experiments/baseline/*/result.json")
    print("  2. 生成对比: python 5_evaluate_all.py")
    print("  3. 生成图表: python 6_generate_plots.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] 程序被用户中断")
        sys.exit(1)
