# bash_authority_tool
一个针对bash指令的静态分析器，拟用于解析大模型生成bash中涉及到的权限越界问题

## **bashlint**
拟仿照github上已有的bashlex项目(项目链接：https://github.com/idank/bashlex.git）
用其核心代码作为bash静态分析器，并在原有代码基础上增加了一些创新。增加了部分bash语法。并在data_tools中增加了对语法树的解析部分。

## **bash_tools**
包括运行函数以及大模型修复函数以及权限表和异常处理的封装类。需要运行时：
```
python3 safe_execute.py
```

## **nlp_tool**
帮助静态分析器解析bash指令的一些工具类

## **tool**
里面包含了一个优化过后的htmlTestRunner,用于多测试用例可视化测试报告生成


## **tool**
里面包含了一个优化过后的htmlTestRunner,用于多测试用例可视化测试报告生成



## **test_bash**
自动化测试脚本
```
python3 test_bash.py
```

## **test_command**
测试用例
