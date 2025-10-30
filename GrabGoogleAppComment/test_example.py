#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试示例 - 直接在代码中调用
现在会从 config.json 读取配置，不需要在这里硬编码参数
"""

from reviews_scraper import main

# 调用函数获取提交记录（所有参数都从config.json读取）
# 如果需要覆盖某些参数，可以传入，例如：
# result = main(per_page=5, ref_name='other-branch')
result = main()  # 完全从config.json读取

# 处理结果
if result['success']:
    print(f"\n成功获取 {result['count']} 条提交记录\n")
    print("="*80)
    
    for idx, commit in enumerate(result['commits'], 1):
        print(f"\n[提交 #{idx}]")
        print(f"  ID: {commit.get('short_id', 'N/A')}")
        print(f"  标题: {commit.get('title', 'N/A')}")
        print(f"  作者: {commit.get('author_name', 'N/A')}")
        print(f"  提交时间: {commit.get('authored_date', 'N/A')}")
        print(f"  链接: {commit.get('web_url', 'N/A')}")
        print("-"*80)
else:
    print(f"错误: {result['error']}")

