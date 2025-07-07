import subprocess
import logging
import os

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fuzzware_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def harness_test():

    directory = "/home/zqh/Desktop/test1"
    logger.info(f"chang file path :{ directory }")

    os.chdir(directory)


    # 配置Fuzzware命令
    FUZZWARE_COMMAND = [
        "fuzzware_harness",
        "emulator",
    ]

    # 运行Fuzzware命令
    process = subprocess.Popen(FUZZWARE_COMMAND, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # 获取输出和错误信息
    stdout, stderr = process.communicate()

    # 记录输出
    logger.info("Fuzzware output:\n%s", stdout)
    if stderr:
        logger.error("Fuzzware error:\n%s", stderr)

if __name__ == '__main__':
    harness_test()