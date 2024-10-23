import os
import sys
import qianfan

current_dir = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录（假设 bash_tools 和 safe_execute.py 在同一目录下）
project_root = os.path.abspath(os.path.join(current_dir, '..'))

# 将项目根目录添加到 sys.path
sys.path.insert(0, project_root)
os.environ["QIANFAN_AK"] = "your ak"
os.environ["QIANFAN_SK"] = "your sk"





def create_prompt(pairs, command):
    # 开头的请求描述，说明优化需求
    prevs = (
        f"请对以下 bash 指令进行优化：\n\n"
        f"{command}\n\n"
        f"目标是确保在用户权限不足的情况下指令能够正确执行。"
        f"以下是命令中涉及的文件路径及其对应的权限越界问题：\n"
    )

    # 添加每个 Pair 对象中越界的文件路径和权限状态
    for pair in pairs:
        out_of_bounds_details = ", ".join(pair.out_of_bounds_permissions.description())
        prevs += (
            f"- 文件路径：{pair.file_path}\n"
            f"  越界状态：{out_of_bounds_details}\n"
        )

    # 提示优化后的输出要求
    prevs += (
        "\n请根据上述信息对命令进行修改，以使其在权限不足的情况下正常运行，(注意，越界状态除非超级用户外不要通过sudo改进）"
        "先直接返回优化后的 bash 指令（不要前缀修饰语）再返回具体的优化建议。"
    )

    return prevs


def call_llm(pairs, command, temperature=0):
    prompt=create_prompt(pairs,command)
    chat_comp = qianfan.ChatCompletion()
    # 创建一个 completion，并得到回答
    resp = chat_comp.do(model="your model", messages=[{
        "role": "user",
        "content": f"{prompt}"
    }])
    # 返回回答文本内容
    return resp["body"]["result"]

def call_llm_test(model="ERNIE-4.0-8K-Latest"):

    chat_comp = qianfan.ChatCompletion()
    # 创建一个 completion，并得到回答
    resp = chat_comp.do(model="your model", messages=[{
        "role": "user",
        "content": "你好"
    }])
    # 返回回答文本内容

    print(resp["body"]["result"])

    return resp["body"]

if __name__ == "__main__":
    call_llm_test()
