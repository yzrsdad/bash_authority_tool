from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import re
import subprocess
import warnings

import sys
import os

# 获取当前脚本文件的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录（假设 bash_tools 和 safe_execute.py 在同一目录下）
project_root = os.path.abspath(os.path.join(current_dir, '..'))

# 将项目根目录添加到 sys.path
sys.path.insert(0, project_root)
from bash_tools import authority_table
from multiprocessing import Process, Pipe
from bash_tools.llm.llm_repair import call_llm
from bash_tools.permission_status import PermissionStatus
from bashlint import data_tools
from bash_tools.common_exception import common_exceptions
from bash_tools.exception_handler import ExceptionHandler

if sys.version_info > (3, 0):
    pass


class Pair:
    def __init__(self, file_path: str, out_of_bounds_permissions: PermissionStatus):
        self.file_path = file_path
        self.out_of_bounds_permissions = out_of_bounds_permissions


def check_rwe(info, details):
    if details.get('read', False) and not info.get('read', False):
        return PermissionStatus.READ_OUT_OF_BOUNDS
    if details.get('write', False) and not info.get('write', False):
        return PermissionStatus.WRITE_OUT_OF_BOUNDS
    if details.get('execute', False) and not info.get('execute', False):
        return PermissionStatus.EXECUTE_OUT_OF_BOUNDS

    return PermissionStatus.NO_OUT_OF_BOUNDS


def check_authority(argument, details, table, superuser_global):
    if superuser_global:
        if details['is_dangerous']:
            warnings.warn(f"This operation maybe dangerous for {argument}", UserWarning)
            return PermissionStatus.NO_OUT_OF_BOUNDS
        return PermissionStatus.NO_OUT_OF_BOUNDS
    if argument not in table:
        return PermissionStatus.NOT_OWNER
    else:
        info = table.get(argument)
        if details['superuser']:
            if info.get("superuser"):
                if details['is_dangerous']:
                    warnings.warn(f"This operation maybe dangerous for {argument}", UserWarning)
                    return PermissionStatus.NO_OUT_OF_BOUNDS
                return PermissionStatus.NO_OUT_OF_BOUNDS
            else:
                return PermissionStatus.NOT_SUPERUSER
        else:
            if info.get("superuser"):
                if details['is_dangerous']:
                    warnings.warn(f"This operation maybe dangerous for {argument}", UserWarning)
                    return PermissionStatus.NO_OUT_OF_BOUNDS
                return PermissionStatus.NO_OUT_OF_BOUNDS
            if details['own']:
                if info.get('own'):
                    return check_rwe(info, details)  # 这里应该返回 check_rwe 的结果
                else:
                    return PermissionStatus.NOT_OWNER
            else:
                return check_rwe(info, details)  # 这里也应该返回 check_rwe 的结果


def check_read(arguments, table):
    for argument in arguments:
        info = table.get(argument)
        if not info:
            return False
        if not info.get('read'):
            return False
    return True


def safe_execute(user_name, command):
    exception_handler = ExceptionHandler()

    try:
        cmds = command.split("|")
        split_cmds = []
        for command in cmds:
            # 使用正则表达式按 $() 结构分割
            parts = re.split(r'(\$\([^\)]+\))', command)
            split_cmds.append(parts)

        # 创建权限表
        table = authority_table.AuthorityTable()

        # 遍历每个子命令并进行解析处理
        for sub_cmd in split_cmds:
            for part in sub_cmd:
                part = part.strip()
                if part:
                    ast = data_tools.bash_parser(part)
                    data_tools.reset_globals()
                    data_tools.extract_parameters_from_tree(ast, table)

        file_path = os.path.abspath(os.path.join(project_root, f"{user_name}.json"))
        # 打开 user_name.json 文件并读取其内容
        if os.path.exists(file_path):
            with open(file_path, 'r') as json_file:
                user_data = json.load(json_file)
        else:
            raise common_exceptions.UserNotFoundException(user_name)

        user_table = authority_table.AuthorityTable()
        user_table.load_from_json(user_data)
        superuser_global = user_data.get("superuser", False)
        flag = True
        arguments = []
        pairs = []
        for argument, details in table.table.items():  # 注意这里用 .table
            argument = argument.strip()  # 移除开头和结尾的空格或换行符
            absolute_argument = os.path.abspath(argument)
            flag1 = check_authority(absolute_argument, details, user_table.table, superuser_global)  # 同样用 .table
            if not flag1.value:
                flag = False
                pair = Pair(argument, flag1)
                pairs.append(pair)
                arguments.append(absolute_argument)

        if not flag:
            if_read = check_read(arguments, user_table.table)
            parent_conn, child_conn = Pipe()
            process = Process(target=call_llm_in_new_process, args=(child_conn, pairs, command))
            process.start()
            process.join()  # 等待子进程结束
            message = parent_conn.recv()

            if if_read:
                raise common_exceptions.PermissionDeniedException(user_name, command, arguments, message)
            else:
                raise common_exceptions.PermissionDeniedException(user_name, command, None, message)
            # 注意：这行代码实际上永远不会被执行
        else:
            return arguments

    except Exception as e:
        # 捕获并处理异常，同时返回 table
        exception_handler.handle_exception(e, False)



def run_command(command):
    proc = subprocess.Popen(command, shell=True)
    proc.wait()


def call_llm_in_new_process(conn, pairs, command):
    """
    在新进程中调用 call_llm，并将结果通过管道发送回主进程。
    """
    try:
        message = call_llm(pairs, command)
        conn.send(message)  # 发送结果给主进程
    except Exception as e:
        conn.send(f"Error occurred while calling LLM: {str(e)}")  # 发送错误信息
    finally:
        conn.close()


if __name__ == "__main__":
    user_name = "user"
    command = input("command:")
    safe_execute(user_name, command)
