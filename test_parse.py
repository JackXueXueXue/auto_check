# -*- coding: utf-8 -*-
import json
from typing import List

def main(data1: List[dict], data2: List[dict]) -> List[str]:
    """
    从两个数据数组中提取 Text 字段中以 "#" 开头的标题行，并汇总去重后的结果。

    参数：
    data1: 第一个 Array[Object] 格式的列表
    data2: 第二个 Array[Object] 格式的列表

    返回：
    list: 包含所有不重复的提取标题的列表。
    """
    KnowledgeList = []
    
    # 处理第一个数据数组
    for item in data1:
        text = item.get("Text", "")
        if not text:
            continue
            
        # 按行分割文本并查找第一个以 "#" 开头的行
        for line in text.splitlines():
            if line.strip().startswith("#"):
                KnowledgeList.append(line.strip())
                break  # 只提取第一行以 "#" 开头的文本
    
    # 处理第二个数据数组
    for item in data2:
        text = item.get("Text", "")
        if not text:
            continue
            
        # 按行分割文本并查找第一个以 "#" 开头的行
        for line in text.splitlines():
            if line.strip().startswith("#"):
                KnowledgeList.append(line.strip())
                break  # 只提取第一行以 "#" 开头的文本
    
    # 去重并返回结果
    return list(dict.fromkeys(KnowledgeList))  # 使用字典的键来保持顺序并去重

# 测试代码
if __name__ == "__main__":
    # 测试数据1
    test_data1 = [
        {
            "BlockId": "0195c72a-b36e-59de-b1f1-8c325a504c91",
            "Text": "# FlashGet Kids Connector\n\nFlashGet Kids Connector 如果包括这个三个单词(不区分大小写的)，请保留原文，不翻译。\n",
            "Score": 0.8292092,
            "Token": 43
        }
    ]
    
    # 测试数据2（包含一个重复的标题）
    test_data2 = [
        {
            "BlockId": "0195c72a-b36e-59de-b1f1-8c325a504c9a",
            "Text": "# FlashGet Cast\n\nFlashGet Cast 如果包括这两个单词(不区分大小写的)，请保留原文，不翻译。\n",
            "Score": 0.7955847,
            "Token": 40
        },
        {
            "BlockId": "duplicate-entry",
            "Text": "# FlashGet Kids Connector\n\n重复的标题\n",
            "Score": 0.8,
            "Token": 30
        }
    ]
    
    # 运行测试
    titles = main(test_data1, test_data2)
    print("提取的标题:", titles)