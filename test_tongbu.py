#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试 Tongbu 项目提交获取
"""

from fetch_tongbu_commits import fetch_tongbu_commits
import json


def test_dev_branch():
    """测试获取 dev 分支的提交"""
    print('\n' + '=' * 80)
    print('测试 1: 获取 dev 分支最新 5 条提交')
    print('=' * 80)
    
    result = fetch_tongbu_commits(branch='dev', per_page=5)
    
    if result['success']:
        print(f'\n✅ 测试成功！获取了 {result["count"]} 条提交')
        
        # 显示第一条提交的详细信息
        if result['commits']:
            first_commit = result['commits'][0]
            print('\n第一条提交详情:')
            print(json.dumps(first_commit, indent=2, ensure_ascii=False))
        
        return True
    else:
        print(f'\n❌ 测试失败: {result["error"]}')
        return False


def test_master_branch():
    """测试获取 master 分支的提交"""
    print('\n' + '=' * 80)
    print('测试 2: 获取 master 分支最新 3 条提交')
    print('=' * 80)
    
    result = fetch_tongbu_commits(branch='master', per_page=3)
    
    if result['success']:
        print(f'\n✅ 测试成功！获取了 {result["count"]} 条提交')
        
        # 显示所有提交的标题
        print('\n提交列表:')
        for idx, commit in enumerate(result['commits'], 1):
            print(f"  {idx}. {commit.get('title', 'N/A')} - {commit.get('author_name', 'N/A')}")
        
        return True
    else:
        print(f'\n❌ 测试失败: {result["error"]}')
        print('   (可能 master 分支不存在，这是正常的)')
        return False


def test_json_structure():
    """测试返回的 JSON 结构是否正确"""
    print('\n' + '=' * 80)
    print('测试 3: 验证返回数据结构')
    print('=' * 80)
    
    result = fetch_tongbu_commits(branch='dev', per_page=1)
    
    # 检查必需的字段
    required_fields = ['success', 'commits', 'count', 'error']
    missing_fields = [field for field in required_fields if field not in result]
    
    if missing_fields:
        print(f'\n❌ 缺少必需字段: {missing_fields}')
        return False
    
    print('\n✅ 数据结构验证通过！')
    print(f'   - success: {type(result["success"]).__name__}')
    print(f'   - commits: {type(result["commits"]).__name__} (长度: {len(result["commits"])})')
    print(f'   - count: {type(result["count"]).__name__}')
    print(f'   - error: {type(result["error"]).__name__ if result["error"] else "None"}')
    
    # 如果有提交数据，检查提交字段
    if result['success'] and result['commits']:
        commit = result['commits'][0]
        commit_fields = ['id', 'short_id', 'title', 'message', 'author_name', 
                        'author_email', 'authored_date', 'web_url']
        
        print('\n   提交数据包含的字段:')
        for field in commit_fields:
            has_field = field in commit
            status = '✓' if has_field else '✗'
            print(f'   {status} {field}')
    
    return True


def run_all_tests():
    """运行所有测试"""
    print('\n')
    print('*' * 80)
    print('*' + ' ' * 78 + '*')
    print('*' + '  开始测试 Tongbu.Tui.Nms.Inner 项目提交获取功能'.center(76) + '*')
    print('*' + ' ' * 78 + '*')
    print('*' * 80)
    
    tests = [
        ('Dev 分支测试', test_dev_branch),
        ('Master 分支测试', test_master_branch),
        ('数据结构测试', test_json_structure),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f'\n❌ {test_name} 发生异常: {str(e)}')
            results.append((test_name, False))
    
    # 输出测试总结
    print('\n' + '=' * 80)
    print('测试总结')
    print('=' * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = '✅ 通过' if result else '❌ 失败'
        print(f'{status}  {test_name}')
    
    print('\n' + '-' * 80)
    print(f'总计: {passed}/{total} 个测试通过')
    print('=' * 80 + '\n')
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    
    if success:
        print('🎉 所有测试通过！可以正常使用了。\n')
        print('使用方法:')
        print('  python fetch_tongbu_commits.py')
        print('  python fetch_tongbu_commits.py --branch dev --per-page 20')
        print('  python fetch_tongbu_commits.py --output commits.json')
    else:
        print('⚠️  部分测试失败，请检查配置和网络连接。\n')
    
    exit(0 if success else 1)

