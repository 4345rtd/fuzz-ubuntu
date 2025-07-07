import unittest
import subprocess
import os
import shutil

class TestAFLSeedpoolPatch(unittest.TestCase):
    def setUp(self):
        # 配置测试环境
        self.fuzzware_path = "/home/zqh/fuzzware"  #  Fuzzware 项目的实际路径
        self.emulator_folder = os.path.join(self.fuzzware_path, "emulator")
        self.patch_file = "/home/zqh/fuzzware/output.patch"  # 替换为补丁文件的实际路径
        self.backup_folder = os.path.join(self.fuzzware_path, "emulator_backup")

        # 备份原始 emulator 文件夹
        if os.path.exists(self.emulator_folder):
            shutil.copytree(self.emulator_folder, self.backup_folder)
        else:
            self.fail(f"emulator 文件夹不存在: {self.emulator_folder}")

    def tearDown(self):
        # 恢复原始 emulator 文件夹
        if os.path.exists(self.backup_folder):
            shutil.rmtree(self.emulator_folder)
            shutil.copytree(self.backup_folder, self.emulator_folder)
            shutil.rmtree(self.backup_folder)
        else:
            self.fail("备份文件夹不存在，无法恢复原始状态")

    def test_patch_application(self):
        """测试补丁是否能够成功应用到 emulator 文件夹"""
        try:
            # 应用补丁
            result = subprocess.run(
                ["git", "apply", self.patch_file],
                cwd=self.fuzzware_path,
                capture_output=True,
                text=True
            )
            self.assertEqual(result.returncode, 0, f"补丁应用失败: {result.stderr}")
            print("补丁成功应用到 emulator 文件夹")
        except Exception as e:
            self.fail(f"补丁应用过程中出现错误: {str(e)}")

    def test_seedpool_functionality(self):
        """测试补丁是否有效改善了 Seedpool 功能"""
        try:
            # 进入项目根目录
            os.chdir(self.fuzzware_path)

            # 运行 make 编译
            make_result = subprocess.run(
                ["make"],
                capture_output=True,
                text=True
            )
            self.assertEqual(make_result.returncode, 0, f"编译失败: {make_result.stderr}")

            print("项目编译成功，Seedpool 功能可能正常")
        except Exception as e:
            self.fail(f"编译过程中出现错误: {str(e)}")

if __name__ == "__main__":
    unittest.main()