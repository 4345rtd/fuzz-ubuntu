import os
import subprocess
import shutil
import time
import json
import re
from pathlib import Path

# 配置参数
FUZZWARE_REPO = "https://github.com/fuzzware-fuzzer/fuzzware"
PATCH_FILE = "afl-seedpool.patch"
TARGET_PROGRAM = "./test_file"  # 待测试的目标程序
INPUT_CORPUS = "test_file"  # 初始测试用例目录
FUZZ_TIME = 300  # 单次模糊测试时间（秒）
COVERAGE_TOOL = "gcov"  # 覆盖率工具


class FuzzwarePatchManager:
    def __init__(self, workspace="/home/zqh/fuzzware"):
        self.workspace = Path(workspace)
        self.emulator_dir = self.workspace / "emulator"
        self.setup_dirs()

    def setup_dirs(self):
        """创建必要目录"""
        self.workspace.mkdir(exist_ok=True)
        (self.workspace / "log").mkdir(exist_ok=True)
        (self.workspace / "reports").mkdir(exist_ok=True)
        (self.workspace / "baseline").mkdir(exist_ok=True)
        (self.workspace / "patched").mkdir(exist_ok=True)

    def clone_and_patch(self):
        """应用补丁"""
        os.chdir(self.workspace)

        # 检查未提交的更改
        if self.has_uncommitted_changes():
            print("代码库有未提交的更改，正在自动处理...")
            self.handle_uncommitted_changes()

        if not Path(PATCH_FILE).exists():
            raise FileNotFoundError(f"补丁文件 {PATCH_FILE} 未找到")

        try:
            # 检查补丁是否可以无冲突应用
            self.run_cmd(f"git apply --check {PATCH_FILE}", check=True)
            # 应用补丁
            self.run_cmd(f"git apply {PATCH_FILE}")
            print("[+] 补丁应用成功")
        except subprocess.CalledProcessError as e:
            print(f"[-] 补丁冲突: {e}")
            self.handle_patch_conflict()

    def has_uncommitted_changes(self):
        """检查是否有未提交的更改"""
        result = self.run_cmd("git status --porcelain")
        return result.stdout.strip() != ""

    def handle_uncommitted_changes(self):
        """处理未提交的更改"""
        choice = input("检测到未提交的更改，是否尝试自动暂存？(y/n): ")
        if choice.lower() == "y":
            try:
                # 暂存更改
                self.run_cmd("git stash")
                print("未提交的更改已暂存")
            except subprocess.CalledProcessError as e:
                print(f"自动暂存失败: {e}")
                print("请手动处理未提交的更改后重新运行脚本。")
                exit(1)
        else:
            print("请手动处理未提交的更改后重新运行脚本。")
            exit(1)

    def handle_patch_conflict(self):
        """处理补丁冲突"""
        choice = input("检测到补丁冲突，是否尝试自动合并？(y/n): ")
        if choice.lower() == "y":
            try:
                self.run_cmd(f"git apply --reject {PATCH_FILE}")
                print("补丁部分应用成功，但存在冲突。")
                print("请手动检查.rej文件并解决冲突后继续。")
                exit(1)
            except subprocess.CalledProcessError as e:
                print(f"自动合并失败: {e}")
                print("请手动解决冲突后重新运行脚本。")
                exit(1)
        else:
            print("请手动解决冲突后重新运行脚本。")
            exit(1)

    def compile_emulator(self):
        """编译仿真器组件"""
        os.chdir(self.emulator_dir)
        self.run_cmd("make clean")
        result = self.run_cmd("make -j4", save_log="compile.log")

        # 检查编译错误
        if "error:" in result.stderr:
            raise RuntimeError("编译失败，请检查compile.log")
        print("[+] 编译成功")

    def run_fuzzing(self, output_dir="output"):
        """运行模糊测试并收集指标"""
        output_path = self.workspace / output_dir
        target_dir = "/home/zqh/fuzzware/test_file"
        os.chdir(target_dir)
        cmd = f"fuzzware pipeline --run-for 00:05:00"  # 替换为实际的目标程序路径

        start_time = time.time()
        try:
            # 运行模糊测试（非阻塞）
            proc = subprocess.Popen(
                cmd.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            # 实时监控输出
            coverage_data = []
            while time.time() - start_time < FUZZ_TIME:
                line = proc.stdout.readline()
                if not line:
                    break
                print(line.strip())

                # 提取覆盖率信息（示例正则）
                if "cov:" in line:
                    cov = re.search(r"cov: (\d+\.\d+)%", line)
                    if cov:
                        coverage_data.append({
                            "time": time.time() - start_time,
                            "coverage": float(cov.group(1))
                        })

            # 生成报告
            report = {
                "executions": self.parse_afl_stats(output_path / "fuzzer_stats"),
                "coverage": coverage_data
            }
            report_dir = self.workspace / "reports"
            report_dir.mkdir(exist_ok=True)
            with open(report_dir / "fuzz_report.json", "w") as f:
                json.dump(report, f)

        except KeyboardInterrupt:
            proc.terminate()

    def compare_performance(self, baseline_dir="baseline"):
        """对比性能差异"""
        # 运行基准测试和应用补丁后的测试
        if not (self.workspace / baseline_dir).exists():
            print("[*] 运行基准测试...")
            self.run_fuzzing(output_dir=baseline_dir)

        print("[*] 运行补丁后测试...")
        self.run_fuzzing(output_dir="patched")

        # 生成对比报告
        self.generate_comparison_report(
            self.workspace / baseline_dir,
            self.workspace / "patched"
        )

    def parse_afl_stats(self, stats_path):
        """解析AFL统计文件"""
        stats = {}
        if stats_path.exists():
            with open(stats_path) as f:
                for line in f:
                    if ":" in line:
                        key, val = line.strip().split(":", 1)
                        stats[key.strip()] = val.strip()
        return stats

    def generate_comparison_report(self, base_dir, patched_dir):
        """生成性能对比报告"""
        # 解析统计数据
        base_stats = self.parse_afl_stats(base_dir / "fuzzer_stats")
        patch_stats = self.parse_afl_stats(patched_dir / "fuzzer_stats")

        # 计算关键指标差异
        metrics = [
            ("paths_total", "发现路径数"),
            ("unique_crashes", "独特Crash数"),
            ("execs_per_sec", "执行速度(次/秒)")
        ]

        report = {"metrics": []}
        for key, name in metrics:
            base_val = float(base_stats.get(key, 0))
            patch_val = float(patch_stats.get(key, 0))
            improvement = (patch_val - base_val) / base_val * 100 if base_val != 0 else 0

            report["metrics"].append({
                "name": name,
                "baseline": base_val,
                "patched": patch_val,
                "improvement": f"{improvement:.2f}%"
            })

        # 保存报告
        report_dir = self.workspace / "reports"
        report_dir.mkdir(exist_ok=True)
        with open(report_dir / "comparison.json", "w") as f:
            json.dump(report, f, indent=2)
        print("[+] 性能对比报告已生成")

    def run_cmd(self, cmd, check=False, save_log=None):
        """执行shell命令"""
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        if save_log:
            log_dir = self.workspace / "log"
            log_dir.mkdir(exist_ok=True)
            log_path = log_dir / save_log
            with open(log_path, "w") as f:
                f.write(f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd,
                output=result.stdout,
                stderr=result.stderr
            )
        return result


if __name__ == "__main__":
    manager = FuzzwarePatchManager()

    # Step 1: 应用补丁
    manager.clone_and_patch()

    # Step 2: 编译验证
    manager.compile_emulator()

    # Step 3: 性能对比测试
    manager.compare_performance()

    # Step 4: 生成最终报告
    print("\n测试完成！查看报告：")
    print(f" - 详细日志: {manager.workspace / 'log'}")
    print(f" - 性能对比: {manager.workspace / 'reports/comparison.json'}")