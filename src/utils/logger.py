import os
import sys
import logging
from datetime import datetime

def setup_logger(name, log_file=None):
    """通用日志设置函数"""
    logger = logging.getLogger(name)
    if not logger.handlers:  # 避免重复添加处理程序
        # 获取日志目录路径
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_dir = os.path.join(base_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 如果没有指定日志文件，使用模块名
        if log_file is None:
            log_file = f"{name.split('.')[-1]}.log"
        
        # 创建文件处理程序
        file_handler = logging.FileHandler(
            os.path.join(log_dir, log_file),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理程序
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理程序
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
    
    return logger 