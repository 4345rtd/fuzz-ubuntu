import multiprocessing
import logging
import subprocess
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Fuzzware实例管理类
class FuzzwareManager:
    def __init__(self, fuzzware_command, directory):
        self.fuzzware_command = fuzzware_command
        self.directory = directory

    def run_instance(self):
        try:
            # 切换到指定目录
            os.chdir(self.directory)
            logging.info(f"Changed directory to: {self.directory}")

            # 构造命令行参数
            command = self.fuzzware_command
            logging.info(f"Running Fuzzware with command: {' '.join(command)}")

            # 使用subprocess.Popen启动命令
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # 获取输出和错误信息
            stdout, stderr = process.communicate()

            # 记录输出
            logging.info(f"Fuzzware output in {self.directory}:\n{stdout}")
            if stderr:
                logging.error(f"Fuzzware error in {self.directory}:\n{stderr}")

            return True
        except Exception as e:
            logging.error(f"Fuzzware execution failed in {self.directory}: {e}")
            return False


# 主函数
def main():
    # 定义三个目录
    directories = [
        "/home/zqh/Desktop/test1"
    ]

    # 配置Fuzzware命令
    FUZZWARE_COMMAND = ["fuzzware", "pipeline", "--run-for", "00:05:00"]

    # 创建进程列表
    processes = []

    # 为每个目录创建一个进程
    for directory in directories:
        manager = FuzzwareManager(FUZZWARE_COMMAND, directory)
        process = multiprocessing.Process(target=manager.run_instance)
        processes.append(process)
        process.start()
        logging.info(f"Process for directory {directory} started")

    # 等待所有进程完成
    for process in processes:
        process.join()

    logging.info("All processes finished")


if __name__ == "__main__":
    main()