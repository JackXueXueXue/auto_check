#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简单的运行方式 - 直接运行这个文件即可
在 VSCode 中点击右上角的运行按钮 ▶️ 即可
"""

from fetch_tongbu_commits import fetch_tongbu_commits
import json


def main():
    """
    简单运行示例
    直接在 VSCode 中运行这个文件即可，不需要传任何参数
    """
    
    print('=' * 80)
    print('开始获取 Tongbu.Tui.Nms.Inner 项目的最新提交...')
    print('=' * 80)
    print()
    
    # ===== 在这里修改参数 =====
    branch = 'dev'          # 分支名称：dev, master, 等
    per_page = 20           # 获取数量：10, 20, 50, 100 等
    save_to_file = True     # 是否保存到文件：True 或 False
    output_filename = 'commits_output.json'  # 输出文件名
    # ==========================
    
    print(f'配置信息:')
    print(f'  - 分支: {branch}')
    print(f'  - 获取数量: {per_page}')
    print(f'  - 保存到文件: {save_to_file}')
    if save_to_file:
        print(f'  - 文件名: {output_filename}')
    print()
    
    # 获取提交
    result = fetch_tongbu_commits(branch=branch, per_page=per_page)
    
    # 检查结果
    if result['success']:
        print(f'\n✅ 成功获取 {result["count"]} 条提交记录！\n')
        
        # 输出 JSON 格式
        print('=' * 80)
        print('JSON 格式输出:')
        print('=' * 80)
        json_output = json.dumps(result, indent=2, ensure_ascii=False)
        print(json_output)
        print()
        
        # 显示每条提交的摘要
        print('=' * 80)
        print('提交摘要:')
        print('=' * 80)
        for idx, commit in enumerate(result['commits'], 1):
            print(f"\n[{idx}] {commit.get('title', 'N/A')}")
            print(f"    作者: {commit.get('author_name', 'N/A')}")
            print(f"    时间: {commit.get('authored_date', 'N/A')}")
            print(f"    ID:   {commit.get('short_id', 'N/A')}")
            print(f"    链接: {commit.get('web_url', 'N/A')}")
        
        # 保存到文件
        if save_to_file:
            try:
                with open(output_filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f'\n💾 结果已保存到文件: {output_filename}')
            except Exception as e:
                print(f'\n❌ 保存文件失败: {str(e)}')
        
        print('\n' + '=' * 80)
        print('✅ 完成！')
        print('=' * 80)
        
    else:
        print(f'\n❌ 获取失败！')
        print(f'错误信息: {result["error"]}\n')
        print('请检查:')
        print('  1. 网络是否可以访问 http://git.server.tongbu.com/')
        print('  2. Access Token 是否有效')
        print('  3. 项目 ID (508) 是否正确')
        print('  4. 分支名称是否存在')


if __name__ == '__main__':
    # 提示信息
    print('\n' + '🚀 ' * 40)
    print()
    print('     Tongbu.Tui.Nms.Inner 项目提交获取工具')
    print()
    print('   如需修改参数，请编辑本文件第 17-20 行的配置')
    print()
    print('🚀 ' * 40 + '\n')
    
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n用户中断执行')
    except Exception as e:
        print(f'\n\n❌ 发生错误: {str(e)}')
        import traceback
        traceback.print_exc()
    
    print('\n按任意键退出...')
    input()

