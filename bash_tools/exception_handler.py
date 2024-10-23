import logging
from datetime import datetime
from bash_tools.common_exception import common_exceptions

import sys
import os

# 获取当前脚本文件的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录（假设 bash_tools 和 safe_execute.py 在同一目录下）
project_root = os.path.abspath(os.path.join(current_dir, '..'))

# 将项目根目录添加到 sys.path
sys.path.insert(0, project_root)


class ExceptionHandler:

    def __init__(self, log_file='command_log.txt'):
        # 初始化日志设置
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        # 将日志文件放在项目根目录下
        log_file = os.path.join(project_root, log_file)
        self.logger = logging.getLogger('exception_logger')
        self.logger.setLevel(logging.INFO)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        log_handler = logging.FileHandler(log_file)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.logger.addHandler(log_handler)

    def handle_exception(self, exception, exit_on_error):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 根据异常类型进行不同的处理和日志记录
        if isinstance(exception, common_exceptions.DangerousCommandException):
            self.logger.warning(
                f"{exception.user_name} dangerous command '{exception.command}' in arguments: {', '.join(exception.arguments)} at {current_time}")

        elif isinstance(exception, common_exceptions.UserNotFoundException):
            self.logger.warning(f"User '{exception.user_name}' not found at {current_time}")

        elif isinstance(exception, common_exceptions.PermissionDeniedException):
            self.logger.warning(
                f"Permission denied for user '{exception.user_name}' to execute '{exception.command}' at {current_time}")

        exception_name = type(exception).__name__
        exception_message = str(exception)

        # 输出异常名称和信息
        print(f"{exception_name}: {exception_message}")

        if exit_on_error:
            sys.exit(1)
