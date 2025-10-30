#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git提交内容获取工具
支持GitLab和GitHub API来获取项目的最新提交信息
"""

import requests
import json
import time
import os
import re
from datetime import datetime


def get_commit_diff(api_base_url, project_id, commit_id, access_token, platform='gitlab', timeout=30):
    """
    获取单个提交的diff内容
    
    参数:
        api_base_url: API基础URL
        project_id: 项目ID
        commit_id: 提交ID（GitLab）或SHA（GitHub）
        access_token: API访问令牌
        platform: 平台类型
        timeout: 请求超时时间
    
    返回:
        字典结构:
        {
            'success': bool,
            'files': list,  # 文件改动列表
            'diff_text': str,  # 完整diff文本
            'error': str
        }
    """
    result = {
        'success': False,
        'files': [],
        'diff_text': '',
        'error': None
    }
    
    try:
        if platform == 'gitlab':
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            url = f'{api_base_url}/projects/{project_id}/repository/commits/{commit_id}/diff'
        else:  # GitHub
            headers = {
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            url = f'{api_base_url}/repos/{project_id}/commits/{commit_id}'
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        if platform == 'gitlab':
            # GitLab直接返回diff列表
            for diff_item in data:
                old_path = diff_item.get('old_path', '')
                new_path = diff_item.get('new_path', '')
                diff_content = diff_item.get('diff', '')
                
                # 判断改动类型
                change_type = 'modified'
                if diff_item.get('deleted_file'):
                    change_type = 'deleted'
                elif diff_item.get('new_file'):
                    change_type = 'added'
                elif diff_item.get('renamed_file'):
                    change_type = 'renamed'
                
                # 计算新增和删除的行数（排除diff头部的---和+++行）
                diff_lines = diff_content.split('\n') if diff_content else []
                additions = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
                deletions = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
                
                result['files'].append({
                    'old_path': old_path,
                    'new_path': new_path,
                    'change_type': change_type,  # added, deleted, modified, renamed
                    'diff': diff_content,
                    'additions': additions,
                    'deletions': deletions
                })
            
            # 生成完整diff文本
            diff_lines = []
            for file_info in result['files']:
                diff_lines.append(f"--- a/{file_info['old_path']}")
                diff_lines.append(f"+++ b/{file_info['new_path']}")
                diff_lines.append(file_info['diff'])
            result['diff_text'] = '\n'.join(diff_lines)
        else:  # GitHub
            # GitHub返回的commit对象中包含files字段
            files_data = data.get('files', [])
            for file_item in files_data:
                filename = file_item.get('filename', '')
                patch = file_item.get('patch', '')
                status = file_item.get('status', 'modified')
                
                result['files'].append({
                    'old_path': file_item.get('previous_filename', filename),
                    'new_path': filename,
                    'change_type': status,  # added, removed, modified, renamed
                    'diff': patch,
                    'additions': file_item.get('additions', 0),
                    'deletions': file_item.get('deletions', 0)
                })
            
            # 生成完整diff文本
            result['diff_text'] = '\n\n'.join([f['diff'] for f in result['files'] if f['diff']])
        
        result['success'] = True
        
    except requests.exceptions.RequestException as e:
        result['error'] = f'获取diff失败: {str(e)}'
    
    return result


def get_file_content_at_commit(api_base_url, project_id, commit_id, file_path, access_token, platform='gitlab', timeout=30):
    """
    获取文件在特定commit时的完整内容
    
    参数:
        api_base_url: API基础URL
        project_id: 项目ID
        commit_id: 提交ID（GitLab）或SHA（GitHub）
        file_path: 文件路径
        access_token: API访问令牌
        platform: 平台类型
        timeout: 请求超时时间
    
    返回:
        文件内容字符串，失败返回None
    """
    try:
        if platform == 'gitlab':
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            # 使用GitLab API获取文件内容
            url = f'{api_base_url}/projects/{project_id}/repository/files/{requests.utils.quote(file_path, safe="")}/raw'
            params = {'ref': commit_id}
        else:  # GitHub
            headers = {
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            url = f'{api_base_url}/repos/{project_id}/contents/{requests.utils.quote(file_path, safe="")}'
            params = {'ref': commit_id}
        
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        if response.status_code == 200:
            if platform == 'gitlab':
                return response.text
            else:  # GitHub
                import base64
                data = response.json()
                if data.get('content'):
                    return base64.b64decode(data['content']).decode('utf-8')
        return None
    except Exception:
        return None


def extract_changed_ranges_from_diff(diff_content):
    """
    从diff中提取改动的行号范围
    
    返回:
        list of tuples: [(old_start, old_end, new_start, new_end), ...]
    """
    ranges = []
    pattern = r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@'
    
    for match in re.finditer(pattern, diff_content):
        old_start = int(match.group(1))
        old_count = int(match.group(2) or 1)
        new_start = int(match.group(3))
        new_count = int(match.group(4) or 1)
        
        old_end = old_start + old_count - 1
        new_end = new_start + new_count - 1
        
        ranges.append((old_start, old_end, new_start, new_end))
    
    return ranges


def extract_function_context(code_lines, line_range, language='csharp'):
    """
    从代码中提取函数上下文
    
    参数:
        code_lines: 代码行列表
        line_range: 行号范围 (start, end)
        language: 编程语言类型
    
    返回:
        字典: {
            'function_code': str,  # 完整函数代码
            'function_signature': str,  # 函数签名
            'class_name': str,  # 类名
            'namespace': str  # 命名空间
        }
    """
    start_line, end_line = line_range[0], line_range[1]
    context = {
        'function_code': '',
        'function_signature': '',
        'class_name': '',
        'namespace': ''
    }
    
    if language == 'csharp':
        # 提取命名空间
        namespace_match = None
        for i, line in enumerate(code_lines):
            if re.match(r'^\s*namespace\s+', line):
                namespace_match = line.strip()
                break
        context['namespace'] = namespace_match or ''
        
        # 提取类和函数
        # 寻找包含改动行的函数
        function_start = -1
        class_start = -1
        class_name = ''
        
        # 向前查找函数开始和类定义
        current_brace_count = 0
        for i in range(start_line, -1, -1):
            if i >= len(code_lines):
                continue
            line = code_lines[i]
            
            # 计算当前的大括号层级
            current_brace_count += line.count('}') - line.count('{')
            
            # 查找类定义（在函数之外）
            if class_start == -1:
                class_match = re.search(r'\bclass\s+(\w+)', line)
                if class_match:
                    class_name = class_match.group(1)
                    class_start = i
            
            # 查找函数定义（方法签名）
            # C#方法签名模式: [修饰符] [返回类型] [方法名]([参数])
            method_pattern = r'\b(public|private|protected|internal|static)?\s*(static)?\s*(\w+)\s+(\w+)\s*\([^)]*\)'
            method_match = re.search(method_pattern, line)
            if method_match and '{' in line:
                # 找到了函数定义且在同一行开始函数体
                function_start = i
                context['function_signature'] = line.strip()
                break
            elif method_match:
                # 函数定义，但函数体在下一行
                # 检查下一行是否有 '{'
                if i + 1 < len(code_lines) and '{' in code_lines[i + 1]:
                    function_start = i
                    context['function_signature'] = line.strip()
                    break
        
        # 提取完整函数体
        if function_start >= 0:
            func_lines = []
            brace_count = 0
            in_brace = False
            
            for i in range(function_start, min(end_line + 100, len(code_lines))):
                if i >= len(code_lines):
                    break
                line = code_lines[i]
                
                # 检查是否到达下一个函数或类（通过检测注释、属性或新函数）
                if i > function_start and i > end_line:
                    # 如果遇到XML注释开头且大括号已闭合，说明到了下一个函数
                    if brace_count == 0 and line.strip().startswith('///'):
                        break
                    # 如果遇到属性标记且大括号已闭合
                    if brace_count == 0 and line.strip().startswith('['):
                        break
                
                func_lines.append(line)
                
                # 计算大括号
                brace_count += line.count('{') - line.count('}')
                
                if '{' in line:
                    in_brace = True
                
                # 如果大括号闭合且已经过了改动行
                if in_brace and brace_count == 0 and i >= end_line:
                    break
            
            # 保留换行符
            context['function_code'] = ''.join(func_lines)
            context['class_name'] = class_name
            context['function_start'] = function_start  # 保存函数开始的索引
        
        # 如果没找到完整的函数，至少提取改动周围的代码（前后各30行）
        if not context['function_code']:
            context_start = max(0, start_line - 30)
            context_end = min(len(code_lines), end_line + 30)
            context['function_code'] = ''.join(code_lines[context_start:context_end])
    
    return context


def format_for_ai_review(commit, api_base_url=None, project_id=None, access_token=None, platform='gitlab'):
    """
    将提交记录格式化为AI审核友好的格式，包含完整的代码上下文
    
    参数:
        commit: 提交记录字典
        api_base_url: API基础URL（用于获取文件完整内容）
        project_id: 项目ID（用于获取文件完整内容）
        access_token: API访问令牌（用于获取文件完整内容）
        platform: 平台类型
    
    返回:
        格式化的字符串，包含改动前后代码对比和完整上下文
    """
    if not commit.get('diff') or not commit.get('diff').get('success'):
        return None
    
    diff_info = commit['diff']
    output_lines = []
    commit_id = commit.get('id') or commit.get('sha')
    short_commit_id = commit.get('short_id') or commit.get('short_sha', '')
    
    # 提交基本信息
    output_lines.append("# 📋 代码提交审核报告")
    output_lines.append("")
    output_lines.append("## 📌 提交信息")
    output_lines.append("")
    output_lines.append(f"- **提交ID**: `{short_commit_id}`")
    output_lines.append(f"- **标题**: {commit.get('title', 'N/A')}")
    output_lines.append(f"- **作者**: {commit.get('author_name', 'N/A')}")
    output_lines.append(f"- **提交时间**: {commit.get('authored_date', 'N/A')}")
    if commit.get('message') and commit.get('message').strip() != commit.get('title', '').strip():
        commit_msg = commit.get('message', '').strip()
        if len(commit_msg) > 200:
            output_lines.append(f"- **提交说明**: {commit_msg[:200]}...")
        else:
            output_lines.append(f"- **提交说明**: {commit_msg}")
    output_lines.append("")
    
    # 改动统计
    files_count = len(diff_info.get('files', []))
    total_additions = sum(f.get('additions', 0) for f in diff_info.get('files', []))
    total_deletions = sum(f.get('deletions', 0) for f in diff_info.get('files', []))
    output_lines.append("## 📊 改动统计")
    output_lines.append("")
    output_lines.append(f"- **改动文件数**: {files_count} 个")
    output_lines.append(f"- **新增行数**: +{total_additions}")
    output_lines.append(f"- **删除行数**: -{total_deletions}")
    output_lines.append(f"- **净变化**: {total_additions - total_deletions:+d} 行")
    output_lines.append("")
    
    # 每个文件的改动详情（包含完整上下文）
    output_lines.append("## 🔍 代码改动详情")
    
    for file_info in diff_info.get('files', []):
        old_path = file_info.get('old_path', '')
        new_path = file_info.get('new_path', '')
        change_type = file_info.get('change_type', 'modified')
        diff_content = file_info.get('diff', '')
        
        # 文件标题
        change_type_names = {
            'added': '➕ 新增文件',
            'deleted': '🗑️ 删除文件',
            'modified': '✏️ 修改文件',
            'renamed': '📝 重命名文件'
        }
        output_lines.append("")
        output_lines.append("---")
        output_lines.append("")
        output_lines.append(f"### {change_type_names.get(change_type, '✏️ 修改')}: `{new_path or old_path}`")
        
        if old_path != new_path and change_type == 'renamed':
            output_lines.append(f"  原路径: {old_path}")
            output_lines.append(f"  新路径: {new_path}")
        
        # 尝试获取文件完整内容和函数上下文
        if diff_content and api_base_url and project_id and access_token and commit_id:
            try:
                # 获取改动后的文件内容
                new_file_content = get_file_content_at_commit(
                    api_base_url, project_id, commit_id, new_path or old_path,
                    access_token, platform
                )
                
                # 提取改动的行号范围
                changed_ranges = extract_changed_ranges_from_diff(diff_content)
                
                if new_file_content and changed_ranges:
                    new_code_lines = new_file_content.split('\n')
                    
                    # 为每个改动范围提取上下文
                    for range_idx, (_, _, new_start, new_end) in enumerate(changed_ranges):
                        # 确定代码语言类型（根据文件扩展名）
                        file_ext = (new_path or old_path).split('.')[-1].lower()
                        language_map = {
                            'cs': 'csharp', 'cpp': 'cpp', 'c': 'c',
                            'java': 'java', 'py': 'python', 'js': 'javascript',
                            'ts': 'typescript', 'go': 'go', 'rs': 'rust'
                        }
                        language = language_map.get(file_ext, 'unknown')
                        
                        # 提取函数上下文（从改动后的版本）
                        context = extract_function_context(
                            new_code_lines,
                            (new_start - 1, new_end - 1),  # 转换为0-based索引
                            language
                        )
                        
                        # 保存function_start用于后续计算相对位置
                        function_start_line = context.get('function_start', -1)
                        
                        if context.get('function_code'):
                            output_lines.append(f"\n#### 改动 #{range_idx + 1} 所在函数（改动后）：")
                            if context.get('namespace'):
                                output_lines.append(f"**命名空间**: `{context['namespace']}`")
                            if context.get('class_name'):
                                output_lines.append(f"**类名**: `{context['class_name']}`")
                            if context.get('function_signature'):
                                output_lines.append(f"**函数签名**: `{context['function_signature'].strip()}`")
                            
                            output_lines.append("")
                            
                            # 格式化函数代码
                            func_code = context['function_code']
                            
                            # 检查代码长度，如果太长则智能截取
                            func_lines_list = func_code.split('\n') if '\n' in func_code else [func_code]
                            total_lines = len(func_lines_list)
                            
                            # 如果函数超过80行，只显示改动附近的代码
                            if total_lines > 80:
                                # 找到改动行在函数中的相对位置
                                # function_start_line 是函数开始的0-based索引
                                # new_start - 1 是改动行的0-based索引
                                if function_start_line >= 0:
                                    change_line_relative = (new_start - 1) - function_start_line
                                else:
                                    change_line_relative = 0
                                # 显示改动前后各30行
                                display_start = max(0, change_line_relative - 30)
                                display_end = min(total_lines, change_line_relative + 30)
                                
                                output_lines.append("<details>")
                                output_lines.append("<summary>📝 展开查看完整函数代码（改动后）</summary>")
                                output_lines.append("")
                                output_lines.append("```csharp")
                                if display_start > 0:
                                    output_lines.append(f"... (省略前 {display_start} 行) ...\n")
                                output_lines.append('\n'.join(func_lines_list[display_start:display_end]))
                                if display_end < total_lines:
                                    output_lines.append(f"\n... (省略后 {total_lines - display_end} 行) ...")
                                output_lines.append("```")
                                output_lines.append("</details>")
                            else:
                                # 函数不长，完整显示
                                output_lines.append("<details>")
                                output_lines.append("<summary>📝 展开查看完整函数代码（改动后）</summary>")
                                output_lines.append("")
                                output_lines.append("```csharp")
                                output_lines.append(func_code.rstrip())
                                output_lines.append("```")
                                output_lines.append("</details>")
            except Exception:
                pass  # 如果获取文件内容失败，继续使用diff
        
        # 显示diff内容（标准unified diff格式）
        if diff_content:
            output_lines.append("")
            output_lines.append("#### 💡 代码差异（Diff）:")
            output_lines.append("")
            output_lines.append("```diff")
            output_lines.append(diff_content.rstrip())
            output_lines.append("```")
        elif change_type == 'deleted':
            output_lines.append("\n[文件已完全删除]")
        elif change_type == 'added':
            output_lines.append("\n[新文件已添加]")
        
        output_lines.append("")
    
    return "\n".join(output_lines)


def load_config(config_file='config.json'):
    """
    从配置文件加载配置
    
    参数:
        config_file: 配置文件路径，默认 'config.json'
    
    返回:
        配置字典，如果文件不存在或读取失败则返回默认配置
    """
    default_config = {
        'access_token': None,
        'project_id': None,
        'platform': 'gitlab',
        'base_url': 'http://git.server.tongbu.com/',
        'per_page': 10,
        'ref_name': None,
        'include_diff': True
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # 合并用户配置，只保留有效的键
                for key in default_config.keys():
                    if key in user_config:
                        default_config[key] = user_config[key]
        except Exception as e:
            print(f"警告: 读取配置文件失败 ({config_file}): {e}，使用默认值")
    
    return default_config


def main(access_token=None, project_id=None, platform=None, base_url=None, per_page=None, ref_name=None, include_diff=None, config_file='config.json'):
    """
    获取Git项目的最新提交内容
    
    参数:
        access_token: API访问令牌（如果为None，从配置文件读取）
        project_id: 项目ID（GitLab）或仓库路径（GitHub格式：owner/repo）（如果为None，从配置文件读取）
        platform: 平台类型，'gitlab' 或 'github'（如果为None，从配置文件读取）
        base_url: 自定义API基础URL（如果为None，从配置文件读取）
        per_page: 返回的提交数量（如果为None，从配置文件读取）
        ref_name: 分支或标签名称（如果为None，从配置文件读取）
        include_diff: 是否获取每个提交的改动内容（diff）（如果为None，从配置文件读取）
        config_file: 配置文件路径，默认 'config.json'
    
    返回:
        字典结构:
        {
            'success': bool,  # 是否成功获取
            'commits': list,  # 提交列表，每个提交包含diff信息
            'count': int,     # 提交数量
            'error': str      # 错误信息（如果有）
        }
    """
    # 加载配置文件
    config = load_config(config_file)
    
    # 如果参数为None，则从配置文件读取
    if access_token is None:
        access_token = config.get('access_token')
    if project_id is None:
        project_id = config.get('project_id')
    if platform is None:
        platform = config.get('platform', 'gitlab')
    if base_url is None:
        base_url = config.get('base_url')
    if per_page is None:
        per_page = config.get('per_page', 10)
    if ref_name is None:
        ref_name = config.get('ref_name')
    if include_diff is None:
        include_diff = config.get('include_diff', True)
    
    # 初始化返回字典，确保结构一致
    response = {
        'success': False,
        'commits': [],
        'count': 0,
        'error': None
    }
    
    try:
        # 参数验证
        if not access_token or not project_id:
            response['error'] = '缺少必需参数: access_token 和 project_id'
            return response
        
        platform = platform.lower()
        
        # 设置API基础URL
        # GitLab API需要 /api/v4 路径，所以需要拼接
        # base_url参数默认是 http://git.server.tongbu.com/，需要拼接 /api/v4
        if platform == 'github':
            # GitHub使用公共API
            api_base_url = 'https://api.github.com'
        elif base_url:
            # 如果base_url已经包含/api/v4，直接使用；否则自动拼接
            base_url = base_url.rstrip('/')
            if not base_url.endswith('/api/v4'):
                if base_url.endswith('/api'):
                    api_base_url = f'{base_url}/v4'
                else:
                    # 自动拼接 /api/v4（例如：http://git.server.tongbu.com -> http://git.server.tongbu.com/api/v4）
                    api_base_url = f'{base_url}/api/v4'
            else:
                api_base_url = base_url
        else:
            # 默认使用内部GitLab（如果base_url为空）
            api_base_url = 'http://git.server.tongbu.com/api/v4'
        
        # 设置请求头
        if platform == 'gitlab':
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
        else:  # GitHub
            headers = {
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
        
        # 构建API URL和参数
        if platform == 'gitlab':
            url = f'{api_base_url}/projects/{project_id}/repository/commits'
            params = {
                'per_page': per_page,
                'order_by': 'created_at',
                'sort': 'desc'
            }
            if ref_name:
                params['ref_name'] = ref_name
        else:  # GitHub
            url = f'{api_base_url}/repos/{project_id}/commits'
            params = {'per_page': per_page}
            if ref_name:
                params['sha'] = ref_name
        
        # 发起API请求
        api_response = requests.get(url, headers=headers, params=params, timeout=30)
        api_response.raise_for_status()
        
        commits_data = api_response.json()
        
        # 格式化提交数据
        formatted_commits = []
        
        if platform == 'gitlab':
            for commit_item in commits_data:
                commit_id = commit_item.get('id')
                commit_data = {
                    'id': commit_id,
                    'short_id': commit_item.get('short_id'),
                    'title': commit_item.get('title'),
                    'message': commit_item.get('message'),
                    'author_name': commit_item.get('author_name'),
                    'author_email': commit_item.get('author_email'),
                    'authored_date': commit_item.get('authored_date'),
                    'committer_name': commit_item.get('committer_name'),
                    'committer_email': commit_item.get('committer_email'),
                    'committed_date': commit_item.get('committed_date'),
                    'web_url': commit_item.get('web_url'),
                    'diff': None,
                    'files_changed': []
                }
                
                # 如果需要获取diff
                if include_diff:
                    diff_result = get_commit_diff(
                        api_base_url=api_base_url,
                        project_id=project_id,
                        commit_id=commit_id,
                        access_token=access_token,
                        platform=platform
                    )
                    
                    if diff_result['success']:
                        commit_data['diff'] = diff_result
                        commit_data['files_changed'] = diff_result['files']
                    else:
                        commit_data['diff'] = {'error': diff_result['error']}
                    
                    # 避免请求过快，稍微延迟
                    time.sleep(0.1)
                
                formatted_commits.append(commit_data)
        else:  # GitHub
            for commit_item in commits_data:
                commit_sha = commit_item.get('sha')
                commit_info = commit_item.get('commit', {})
                author_info = commit_info.get('author', {})
                committer_info = commit_info.get('committer', {})
                
                commit_data = {
                    'sha': commit_sha,
                    'short_sha': commit_sha[:7] if commit_sha else '',
                    'message': commit_info.get('message', ''),
                    'title': commit_info.get('message', '').split('\n')[0] if commit_info.get('message') else '',
                    'author_name': author_info.get('name'),
                    'author_email': author_info.get('email'),
                    'authored_date': author_info.get('date'),
                    'committer_name': committer_info.get('name'),
                    'committer_email': committer_info.get('email'),
                    'committed_date': committer_info.get('date'),
                    'html_url': commit_item.get('html_url'),
                    'diff': None,
                    'files_changed': []
                }
                
                # 如果需要获取diff
                if include_diff:
                    diff_result = get_commit_diff(
                        api_base_url=api_base_url,
                        project_id=project_id,
                        commit_id=commit_sha,
                        access_token=access_token,
                        platform=platform
                    )
                    
                    if diff_result['success']:
                        commit_data['diff'] = diff_result
                        commit_data['files_changed'] = diff_result['files']
                    else:
                        commit_data['diff'] = {'error': diff_result['error']}
                    
                    # 避免请求过快，稍微延迟
                    time.sleep(0.1)
                
                formatted_commits.append(commit_data)
        
        # 设置成功响应
        response['success'] = True
        response['commits'] = formatted_commits
        response['count'] = len(formatted_commits)
        
    except requests.exceptions.HTTPError as e:
        # HTTP错误处理
        error_msg = f'API请求失败: {str(e)}'
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg += f' - {error_detail}'
            except ValueError:
                error_msg += f' - {e.response.text}'
        print(error_msg)
        response['error'] = error_msg
        
    except requests.exceptions.RequestException as e:
        # 网络请求异常
        error_msg = f'网络请求错误: {str(e)}'
        print(error_msg)
        response['error'] = error_msg
        
    except Exception as e:
        # 其他异常
        error_msg = f'发生错误: {str(e)}'
        print(error_msg)
        response['error'] = error_msg
    
    # 返回结果字典，确保所有情况下都有相同的键
    return response


if __name__ == '__main__':
    # 命令行使用示例
    import argparse
    
    parser = argparse.ArgumentParser(description='获取Git项目的最新提交内容')
    parser.add_argument('--token', help='API访问令牌（如果不传，从config.json读取）')
    parser.add_argument('--project-id', type=int, help='项目ID (GitLab) 或仓库路径 (GitHub: owner/repo)，如果不传，从config.json读取）')
    parser.add_argument('--platform', choices=['gitlab', 'github'], help='平台类型（如果不传，从config.json读取）')
    parser.add_argument('--base-url', help='自定义API基础URL（如果不传，从config.json读取）')
    parser.add_argument('--per-page', type=int, help='返回的提交数量（如果不传，从config.json读取）')
    parser.add_argument('--ref', help='分支或标签名称（如果不传，从config.json读取）')
    parser.add_argument('--config', default='config.json', help='配置文件路径（默认: config.json）')
    parser.add_argument('--output', help='保存到JSON文件')
    parser.add_argument('--no-diff', action='store_true', help='不获取改动内容（diff），只获取提交基本信息')
    parser.add_argument('--ai-review', action='store_true', help='输出AI审核格式（Markdown格式，便于传给AI审核）')
    parser.add_argument('--ai-review-output', help='将AI审核格式保存到文件（Markdown格式）')
    
    args = parser.parse_args()
    
    # 调用main函数，如果命令行没有传参数，传None，让main函数从配置文件读取
    call_kwargs = {
        'config_file': args.config,
    }
    
    # 只有命令行传了参数时才添加到kwargs中，否则传None让函数从配置文件读取
    call_kwargs['access_token'] = args.token if args.token else None
    call_kwargs['project_id'] = args.project_id if args.project_id is not None else None
    call_kwargs['platform'] = args.platform if args.platform else None
    call_kwargs['base_url'] = args.base_url if args.base_url else None
    call_kwargs['per_page'] = args.per_page if args.per_page is not None else None
    call_kwargs['ref_name'] = args.ref if args.ref else None
    # 处理diff参数：如果指定了--no-diff，则设为False；否则传None让函数从配置文件读取
    call_kwargs['include_diff'] = False if args.no_diff else None
    
    # 调用main函数（None参数会从配置文件读取）
    result = main(**call_kwargs)
    
    # 输出结果
    if result['success']:
        print(f"\n{'='*80}")
        print(f"成功获取 {result['count']} 条提交记录")
        print(f"{'='*80}\n")
        
        for idx, commit in enumerate(result['commits'], 1):
            print(f"[提交 #{idx}]")
            
            # GitLab使用id，GitHub使用sha
            if 'short_id' in commit:
                print(f"  ID: {commit.get('short_id', 'N/A')}")
            elif 'short_sha' in commit:
                print(f"  SHA: {commit.get('short_sha', 'N/A')}")
            
            print(f"  标题: {commit.get('title', 'N/A')}")
            print(f"  作者: {commit.get('author_name', 'N/A')} <{commit.get('author_email', 'N/A')}>")
            print(f"  提交时间: {commit.get('authored_date', 'N/A')}")
            
            if commit.get('web_url'):
                print(f"  链接: {commit.get('web_url')}")
            elif commit.get('html_url'):
                print(f"  链接: {commit.get('html_url')}")
            
            # 显示改动统计
            if commit.get('diff') and commit.get('diff').get('success'):
                diff_info = commit['diff']
                files_count = len(diff_info.get('files', []))
                total_additions = sum(f.get('additions', 0) for f in diff_info.get('files', []))
                total_deletions = sum(f.get('deletions', 0) for f in diff_info.get('files', []))
                print(f"  改动文件: {files_count} 个")
                print(f"  新增行数: +{total_additions}")
                print(f"  删除行数: -{total_deletions}")
                
                # 显示每个文件的完整改动内容
                if diff_info.get('files'):
                    print("\n" + "="*80)
                    print("代码改动详情（完整diff）:")
                    print("="*80 + "\n")
                    
                    for idx, file_change in enumerate(diff_info['files'], 1):
                        old_path = file_change.get('old_path', '')
                        new_path = file_change.get('new_path', '')
                        diff_content = file_change.get('diff', '')
                        change_type = file_change.get('change_type', 'modified')
                        
                        # 文件标题
                        change_type_names = {
                            'added': '[新增]',
                            'deleted': '[删除]',
                            'modified': '[修改]',
                            'renamed': '[重命名]'
                        }
                        change_label = change_type_names.get(change_type, '[修改]')
                        
                        if old_path != new_path and change_type == 'renamed':
                            print(f"\n文件 {idx}/{len(diff_info['files'])}: {change_label}")
                            print(f"  原路径: {old_path}")
                            print(f"  新路径: {new_path}")
                        else:
                            print(f"\n文件 {idx}/{len(diff_info['files'])}: {change_label} {new_path or old_path}")
                        
                        # 显示完整的diff内容
                        if diff_content:
                            print("\n" + "-"*80)
                            print(diff_content)
                            print("-"*80)
                        elif change_type == 'deleted':
                            print("\n[文件已完全删除]")
                        elif change_type == 'added':
                            print("\n[新文件]")
                    
                    print("\n" + "="*80)
            elif commit.get('diff'):
                print(f"  获取改动内容失败: {commit['diff'].get('error', '未知错误')}")
            
            print(f"\n{'-'*80}\n")
        
        # 保存到文件
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"结果已保存到: {args.output}")
        
        # 输出AI审核格式
        if args.ai_review or args.ai_review_output:
            ai_review_contents = []
            
            # 获取API配置用于获取文件完整内容
            call_kwargs_for_api = {}
            if args.token:
                call_kwargs_for_api['access_token'] = args.token
            if args.project_id is not None:
                call_kwargs_for_api['project_id'] = args.project_id
            if args.platform:
                call_kwargs_for_api['platform'] = args.platform
            
            # 如果命令行没传参数，从配置文件读取用于API调用
            config_for_api = load_config(args.config)
            api_token = call_kwargs_for_api.get('access_token') or config_for_api.get('access_token')
            api_project_id = call_kwargs_for_api.get('project_id') or config_for_api.get('project_id')
            api_platform = call_kwargs_for_api.get('platform') or config_for_api.get('platform', 'gitlab')
            
            # 获取api_base_url
            api_base_url_for_format = None
            base_url_config = args.base_url if args.base_url else config_for_api.get('base_url')
            if base_url_config:
                base_url_config = base_url_config.rstrip('/')
                if not base_url_config.endswith('/api/v4'):
                    if base_url_config.endswith('/api'):
                        api_base_url_for_format = f'{base_url_config}/v4'
                    else:
                        api_base_url_for_format = f'{base_url_config}/api/v4'
                else:
                    api_base_url_for_format = base_url_config
            else:
                api_base_url_for_format = 'http://git.server.tongbu.com/api/v4' if api_platform == 'gitlab' else 'https://api.github.com'
            
            for idx, commit in enumerate(result['commits'], 1):
                formatted = format_for_ai_review(
                    commit,
                    api_base_url=api_base_url_for_format,
                    project_id=api_project_id,
                    access_token=api_token,
                    platform=api_platform
                )
                if formatted:
                    ai_review_contents.append(formatted)
                    if args.ai_review:
                        print(f"\n{'='*80}")
                        print(f"【AI审核格式 - 提交 #{idx}】")
                        print(f"{'='*80}\n")
                        print(formatted)
            
            # 保存AI审核格式到文件
            if args.ai_review or args.ai_review_output:
                # 创建输出文件夹
                output_dir = "代码提交记录"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # 生成文件名（如果指定了文件名则使用，否则自动生成）
                if args.ai_review_output:
                    # 如果指定了完整路径，直接使用
                    if os.path.dirname(args.ai_review_output):
                        output_file = args.ai_review_output
                    else:
                        # 如果只是文件名，保存到代码提交记录文件夹
                        output_file = os.path.join(output_dir, args.ai_review_output)
                else:
                    # 自动生成文件名：ai审核_时间
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"ai审核_{timestamp}.md"
                    output_file = os.path.join(output_dir, filename)
                
                # 保存文件
                separator = "\n\n" + "="*80 + "\n\n"
                all_content = separator.join(ai_review_contents)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(all_content)
                print(f"\n✓ AI审核格式已保存到: {output_file}")
    else:
        print(f"\n错误: {result['error']}")

