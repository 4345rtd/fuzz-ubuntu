# /all_test.py
from auto_fuzzware_pipeline import FuzzwarePatchManager
from harm_test import harness_test
import argparse
import logging
import os
from logging.handlers import RotatingFileHandler
import threading

def setup_log(log_level=logging.INFO, log_file=None, log_format=None):
    """
    配置日志记录器。

    :param log_level: 日志级别，默认为 INFO
    :param log_file: 日志文件路径，如果为 None 则仅输出到控制台
    :param log_format: 日志格式，默认为 '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    """
    # 创建一个 logger
    logger = logging.getLogger()
    logger.setLevel(log_level)  # 设置全局日志级别

    # 创建日志格式
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)

    # 添加控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 如果提供了日志文件路径，则添加文件 handler
    if log_file:
        # 确保日志文件所在的目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # 使用 RotatingFileHandler 实现日志文件按大小分割
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 每个日志文件最大为 10MB
            backupCount=5,              # 保留 5 个备份
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # 避免日志被多次记录（防止重复添加 handler）
    logger.propagate = False

    return logger

def start_process(args):
    is_test = False

    if args.all_test:
        log.info(f"==========start all test==========")
        is_test =True
        # 使用 FuzzwareManager 执行所有测试
        patch_manager = FuzzwarePatchManager()
        t1 = threading.Thread(target=patch_manager.compare_performance, args=())
        # patch_manager.compare_performance()
        t2 = threading.Thread(target=harness_test, args=())

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        log.info("\n测试完成！查看报告：")
        log.info(f" - 详细日志: {patch_manager.workspace / 'log'}")
        log.info(f" - 性能对比: {patch_manager.workspace / 'reports/comparison.json'}")

    if args.test_patch:
        log.info(f"==========start test patch==========")
        is_test = True
        # 使用 FuzzwarePatchManager 测试补丁
        patch_manager = FuzzwarePatchManager()
        patch_manager.compare_performance()

        log.info("\n测试完成！查看报告：")
        log.info(f" - 详细日志: {patch_manager.workspace / 'log'}")
        log.info(f" - 性能对比: {patch_manager.workspace / 'reports/comparison.json'}")

    if args.test_harness_svd:
        log.info(f"==========start test harness svd==========")
        is_test = True
        # 使用 FuzzwareManager 测试 harness svd
        harness_test()

    if is_test == False:
        log.info(f"{args}")
        log.warning(f"Please select what you want to test")
        log.warning(f"Or enter -h for more information")
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="start test")
    parser.add_argument("--all_test", type=bool, default=False, help="Whether all tests are performed")
    parser.add_argument("--test_patch", type=bool, default=False, help="test patch")
    parser.add_argument("--directories", type=str, default="", help="")
    parser.add_argument("--test_harness_svd", type=bool, default=False, help="test harness svd")
    parser.add_argument("--svd_test_file", type=str, default="", help="work file path")
    parser.add_argument("--is_log", type=bool, default=False, help="log or not")
    parser.add_argument("--log_out_file", type=str, default="", help="file directory for outputting logs")

    args = parser.parse_args()
    if args.is_log:
        # 设置日志
        log = setup_log(
            log_level=logging.DEBUG,
            log_file=args.log_out_file,
            log_format='%(asctime)s - %(levelname)s - %(message)s'
        )
    else:
        log = logging.getLogger(__name__)


    start_process(args)


