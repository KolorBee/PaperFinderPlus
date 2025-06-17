"""
文件处理模块，用于保存结果到文件
"""
import os
import re
from core.config import OUTPUT_DIR, JOURNAL_OUTPUT_FORMAT, CONFERENCE_OUTPUT_FORMAT

# 保存输出目录的全局变量，可在运行时修改
output_directory = OUTPUT_DIR
journal_output_format = JOURNAL_OUTPUT_FORMAT
conference_output_format = CONFERENCE_OUTPUT_FORMAT

# 用于跟踪文件编号的字典
file_counters = {}

def set_output_directory(directory):
    """设置输出目录"""
    global output_directory
    output_directory = directory
    # 确保目录存在
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    return output_directory

def set_output_formats(journal_format=None, conference_format=None):
    """设置输出文件名格式"""
    global journal_output_format, conference_output_format
    if journal_format:
        journal_output_format = journal_format
    if conference_format:
        conference_output_format = conference_format
    return journal_output_format, conference_output_format

def reset_file_counters():
    """重置文件编号计数器"""
    global file_counters
    file_counters = {}

def get_next_file_number():
    """获取下一个可用的文件序号"""
    # 首先检查输出目录中的文件
    global output_directory, file_counters
    
    # 如果文件计数器为空，初始化它
    if not file_counters:
        # 使用配置的输出目录（现在是绝对路径）
        result_dir = output_directory
        
        # 确保目录存在
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
            return 1  # 如果目录是新创建的，从1开始
        
        # 查找目录中的所有文件
        max_number = 0
        for filename in os.listdir(result_dir):
            # 尝试从文件名中提取序号
            match = re.match(r'^(\d+)', filename)
            if match:
                number = int(match.group(1))
                max_number = max(max_number, number)
        
        # 返回最大序号+1或1（如果没有找到序号）
        return max_number + 1 if max_number > 0 else 1
    else:
        # 如果文件计数器已经初始化，使用当前最大计数器值+1
        current_count = max(file_counters.values()) if file_counters else 0
        return current_count + 1

def get_output_file_path(topic_name, is_journal=True):
    """根据专题名称和类型获取输出文件路径"""
    global output_directory, journal_output_format, conference_output_format, file_counters
    
    # 格式化专题名称
    formatted_topic = format_topic_name(topic_name)
    
    # 生成文件类型键
    type_key = "journal" if is_journal else "conference"
    topic_key = f"{type_key}_{formatted_topic}"
    
    # 如果这个主题和类型的文件还没有编号，分配一个
    if topic_key not in file_counters:
        file_counters[topic_key] = get_next_file_number()
    
    # 获取文件编号
    file_number = file_counters[topic_key]
    
    # 根据类型选择文件名格式
    if is_journal:
        filename = journal_output_format.format(topic=formatted_topic)
    else:
        filename = conference_output_format.format(topic=formatted_topic)
    
    # 检查文件名是否已经包含序号
    if not re.match(r'^\d+\s+', filename):
        # 只有当文件名前面没有序号时，才添加序号前缀
        filename = f"{file_number:02d} {filename}"
    
    # 确保文件名合法，替换Windows不允许的字符
    filename = "".join(c for c in filename if c not in r'\:*?"<>|')
    
    # 确保目录存在
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    return os.path.join(output_directory, filename)

def format_topic_name(topic_name):
    """
    格式化专题名称，将非法字符替换为短横线
    
    Args:
        topic_name: 原始专题名称
        
    Returns:
        格式化后的专题名称
    """
    if not topic_name:
        return "未知专题"
        
    # 保留括号中的内容，但替换斜杠等特殊字符为短横线
    formatted = topic_name.replace("/", "-").replace("\\", "-")
    
    # 确保其他非法字符也被替换为短横线
    for char in ':<>*?"|':
        formatted = formatted.replace(char, "-")
        
    return formatted

def format_paper_with_doi(paper):
    """
    格式化论文条目，提取DOI链接并以更美观的方式显示
    
    Args:
        paper: 原始论文条目文本
        
    Returns:
        格式化后的论文条目
    """
    # 检查是否包含DOI链接
    doi_match = re.search(r'\[DOI: (https?://doi\.org/[^\]]+)\]', paper)
    if doi_match:
        doi_link = doi_match.group(1)
        # 移除原始DOI标记，用更美观的格式替代
        paper_title = paper.replace(f" [DOI: {doi_link}]", "")
        return f"{paper_title} DOI: {doi_link}"
    return paper

def save_topic_results(results, all_papers, topic_name, is_journal=True):
    """
    保存特定专题的结果到对应文件
    
    Args:
        results: 详细结果列表
        all_papers: 所有论文列表
        topic_name: 专题名称
        is_journal: 是否为期刊（True为期刊，False为会议）
    """
    if not topic_name:
        topic_name = "未知专题"

    # 获取输出文件路径 - 此函数确保文件名只添加一次序号
    output_file = get_output_file_path(topic_name, is_journal)
    
    # 写入结果到文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("# 包含 'blockchain' 关键词的论文\n")
        file.write("="*50 + "\n\n")
        
        # 先添加所有论文的总结
        if all_papers:
            file.write("## 所有区块链相关论文一览\n\n")
            for i, paper in enumerate(all_papers, 1):
                formatted_paper = format_paper_with_doi(paper)
                file.write(f"{i}. {formatted_paper}\n")
            file.write("\n" + "="*50 + "\n\n")
        
        # 然后添加详细结果
        if results:
            file.write("## 详细信息\n\n")
            file.write("\n".join(results))
        else:
            file.write("未找到包含 blockchain 关键词的论文。")
    
    print(f"专题 '{topic_name}' 的结果已保存到 {output_file}")

def save_venue_result(venue_name, venue_full_name, year, papers, source_link, volume_link=None, contents_link=None, topic_name="", is_journal=True):
    """
    立即保存单个会议/期刊的结果到专题文件
    
    Args:
        venue_name: 会议/期刊名称
        venue_full_name: 会议/期刊全称
        year: 年份
        papers: 找到的论文列表
        source_link: 来源链接
        volume_link: 卷期链接（可选）
        contents_link: 目录链接（可选）
        topic_name: 专题名称
        is_journal: 是否为期刊
    """
    if not papers:
        print(f"未在 {venue_name} {year}年 找到区块链相关论文，跳过保存")
        return
    
    if not topic_name:
        topic_name = "未知专题"
        
    # 获取输出文件路径 - 此函数现在确保文件名只添加一次序号
    output_file = get_output_file_path(topic_name, is_journal)
    
    # 构建结果条目
    venue_display = venue_name
    if venue_full_name:
        venue_display = f"{venue_name} ({venue_full_name})"
        
    result_entry = f"\n## {venue_display} {year}年\n"
    result_entry += f"- 来源: {source_link}\n"
    
    if volume_link:
        result_entry += f"- 卷期: {volume_link}\n"
        
    if contents_link:
        result_entry += f"- Contents链接: {contents_link}\n"
        
    result_entry += f"- 找到的论文:\n"
    
    for paper in papers:
        formatted_paper = format_paper_with_doi(paper)
        result_entry += f"  * {formatted_paper}\n"
    
    # 如果文件不存在，创建新文件并写入头部
    if not os.path.exists(output_file):
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write("# 包含 'blockchain' 关键词的论文\n")
            file.write("="*50 + "\n\n")
            file.write("## 详细信息\n\n")
            file.write(result_entry)
    else:
        # 文件已存在，追加内容
        with open(output_file, 'a', encoding='utf-8') as file:
            file.write(result_entry)
    
    print(f"已将 {venue_name} {year}年 的 {len(papers)} 篇论文结果立即保存到 {output_file}")

def clean_text(text):
    """清理文本，去除非法字符"""
    return "".join(c for c in text if c not in r'\:*?"<>|') 