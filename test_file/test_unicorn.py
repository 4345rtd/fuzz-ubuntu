import threading
import logging
import subprocess

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Fuzzware实例管理类
class FuzzwareManager:
    def __init__(self, fuzzware_command):
        self.fuzzware_command = fuzzware_command

    def run_instance(self):
        try:
            # 构造命令行参数
            command = self.fuzzware_command
            logging.info(f"Running Fuzzware with command: {' '.join(command)}")

            # 执行命令
            result = subprocess.run(command, capture_output=True, text=True)

            # 记录输出
            logging.info(f"Fuzzware output :\n{result.stdout}")
            if result.stderr:
                logging.error(f"Fuzzware error :\n{result.stderr}")

            return True
        except Exception as e:
            logging.error(f"Fuzzware execution failed : {e}")
            return False



# 主函数
def main():
    # 配置
    FUZZWARE_COMMAND = ["fuzzware", "pipeline", "--run-for", "00:05:00"]

    FuzzwareManager(FUZZWARE_COMMAND).run_instance()
    
    logging.info("All threads finished")

if __name__ == "__main__":
    main()
