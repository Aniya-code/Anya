# log.py
import logging
import os
from datetime import datetime
import configparser

config = configparser.ConfigParser()
config.read('src/match/config.ini')
LOG_DIR = config.get('OUTPUT', 'LOG_DIR')

# 创建日志文件夹
def create_log_dir(log_file):
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

# 获取当前时间
def get_cur_datetime():
    return datetime.now().strftime('%Y%m%d_%H%M%S')  # 格式：20241211_153000

# 日志设置函数
def setup_logger(log_level=logging.INFO, logger_name='default', log_prefix='log'):
    date_time_str = get_cur_datetime()
    log_file = os.path.join(LOG_DIR, f'{log_prefix}_{logger_name}_{date_time_str}.log')
    create_log_dir(log_file)

    # 创建日志器
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    if not logger.handlers:
        # 创建日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        # 创建文件日志处理器
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        # 控制台日志处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # 添加处理器到日志器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# 接口函数：记录匹配日志
def log_match(msg):
    match_logger = setup_logger(log_level=logging.INFO, logger_name='match', log_prefix='log')
    match_logger.info(msg)

# 接口函数：记录错误日志
def log_error(msg):
    error_logger = setup_logger(log_level=logging.ERROR, logger_name='error', log_prefix='log')
    error_logger.error(msg)
