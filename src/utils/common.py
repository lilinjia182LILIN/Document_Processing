import re
import hashlib
import requests
import numpy as np


# SHA-1 哈希
def hash_id(name):
    return hashlib.sha1(name.encode()).hexdigest()


def extract_dates(text):
    # pattern = r'(\d{4})年(\d{1,2})月'
    pattern = r'(.{4})年(.{1,2})月'  ## 二0一三年二月，正则
    matches = re.findall(pattern, text)   # 在text里找到符合模式（pattern）的字符串
    # 列式推导式，格式化year和month，format按顺序转入{}
    return ['{}年{}月'.format(year, month) for year, month in matches]


# 测试代码
if __name__ == "__main__":
    # 测试哈希函数
    print("哈希测试:", hash_id("张三"))

    # 测试日期提取
    test_text = "该项目于二〇二三年二月启动，预计二〇二四年十二月完成"
    dates = extract_dates(test_text)
    print("提取的日期:", dates)