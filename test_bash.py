import unittest
import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))

# 将项目根目录添加到 sys.path
sys.path.insert(0, project_root)
from bash_tools import safe_execute, authority_table, common_exception
from bash_tools.common_exception import common_exceptions
from bash_tools.safe_execute import safe_execute
from tool.HTMLTestRunner_PY3.HTMLTestRunner_PY3 import HTMLTestRunner


def load_test_cases():
    # 获取 JSON 文件的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.abspath(os.path.join(current_dir, 'test_command.json'))

    # 读取并解析 JSON 文件
    with open(file_path, 'r') as file:
        test_cases = json.load(file)

    return test_cases


class TestSafeExecuteAuthorityTable(unittest.TestCase):

    @classmethod
    def generate_test_function(cls, user_name, command, expected_arguments):
        def test_function(self):
            # 初始化返回的 arguments 列表
            generated_arguments = []

            # 调用 safe_execute 并捕获异常
            try:
                generated_arguments = safe_execute(user_name, command)
            except common_exceptions.PermissionDeniedException as e:
                generated_arguments = e.args[2]  # 从异常中获取被拒绝的 arguments 列表
            except common_exceptions.UserNotFoundException:
                self.skipTest(f"User {user_name} not found, skipping test.")

            # 比较生成的 arguments 列表和预期的 arguments 列表是否相同
            self.assertEqual(
                expected_arguments,
                generated_arguments,
                f"Generated arguments do not match the expected arguments for command: {command}"
            )

        return test_function


# 动态添加测试方法
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 测试报告相关配置
    report_title = 'Bash用例执行报告'
    desc = '用于展示bash权限测试的测试用例'
    report_folder = os.path.join(current_dir, 'reports')
    report_file = 'BashTestReport.html'

    # 确保报告文件夹存在，不存在则创建
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)

    report_path = os.path.join(report_folder, report_file)

    # 创建测试套件
    testsuite = unittest.TestSuite()

    # 加载测试用例
    test_cases = load_test_cases()
    for i, case in enumerate(test_cases):
        user_name = case.get("user_name")
        command = case.get("command")
        expected_arguments = case.get("expected_arguments")

        # 生成测试函数
        test_func = TestSafeExecuteAuthorityTable.generate_test_function(user_name, command, expected_arguments)

        # 动态为测试类添加测试方法
        setattr(TestSafeExecuteAuthorityTable, f"test_case_{i + 1}", test_func)

        testsuite.addTest(TestSafeExecuteAuthorityTable(f"test_case_{i + 1}"))

    # 生成测试报告
    with open(report_path, 'wb') as report:
        runner = HTMLTestRunner(stream=report, title=report_title, description=desc)
        runner.run(testsuite)
