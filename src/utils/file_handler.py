"""
文件处理模块，用于保存结果到文件
此模块作为协调器，根据配置的输出格式选择调用相应的处理模块
"""
import os
import re
from core.config import OUTPUT_DIR, JOURNAL_OUTPUT_FORMAT, CONFERENCE_OUTPUT_FORMAT, OUTPUT_FORMAT
from core.config import TARGET_KEYWORDS, TARGET_KEYWORDS_MODE


def _build_keyword_desc():
    """构建关键词描述字符串，用于日志输出"""
    try:
        if isinstance(TARGET_KEYWORDS, (list, tuple)):
            kws = [str(k).strip() for k in TARGET_KEYWORDS if k]
        else:
            kws = [str(TARGET_KEYWORDS)] if TARGET_KEYWORDS else []
    except Exception:
        kws = [str(TARGET_KEYWORDS)]

    joined = ', '.join(kws) if kws else '指定'
    if TARGET_KEYWORDS_MODE and TARGET_KEYWORDS_MODE.upper() == 'AND':
        return f"同时包含 {joined} 关键词"
    else:
        return f"包含任一关键词 ({joined})"

# 导入文本和Excel处理模块
try:
    from .txt_handler import save_topic_results as save_topic_results_to_txt
    from .txt_handler import save_venue_result as save_venue_result_to_txt
    TXT_SUPPORTED = True
except ImportError:
    TXT_SUPPORTED = False
    print("警告：无法导入文本处理模块")

try:
    from .excel_handler import save_topic_results as save_topic_results_to_excel
    from .excel_handler import save_venue_result as save_venue_result_to_excel
    from .excel_handler import check_excel_support
    EXCEL_SUPPORTED = check_excel_support()
except ImportError:
    EXCEL_SUPPORTED = False
    print("警告：无法导入Excel处理模块")

# 保存输出目录的全局变量，可在运行时修改
output_directory = OUTPUT_DIR
journal_output_format = JOURNAL_OUTPUT_FORMAT
conference_output_format = CONFERENCE_OUTPUT_FORMAT

# 支持的输出格式列表
supported_formats = []
if TXT_SUPPORTED:
    supported_formats.append("txt")
if EXCEL_SUPPORTED:
    supported_formats.append("xlsx")

# 根据配置设置输出格式
output_formats = [fmt.strip().lower() for fmt in OUTPUT_FORMAT.split(",")]
# 过滤掉不支持的格式
output_formats = [fmt for fmt in output_formats if fmt in supported_formats]
# 如果没有支持的格式，默认使用文本格式
if not output_formats and TXT_SUPPORTED:
    output_formats = ["txt"]
elif not output_formats:
    print("错误：没有可用的输出格式处理程序")

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

def set_output_format(format_type):
    """设置输出文件格式（txt或xlsx或两者）"""
    global output_formats
    # 解析格式，支持逗号分隔的多格式
    formats = [fmt.strip().lower() for fmt in format_type.split(",")]
    # 只保留支持的格式
    valid_formats = [fmt for fmt in formats if fmt in supported_formats]
    
    if valid_formats:
        output_formats = valid_formats
        print(f"设置输出格式为: {', '.join(output_formats)}")
    else:
        print(f"警告：指定的输出格式 '{format_type}' 不受支持，将使用默认格式")
        # 如果没有有效格式，设置为默认的文本格式（如果支持）
        if "txt" in supported_formats:
            output_formats = ["txt"]
            print("使用默认的txt文本格式")
        elif supported_formats:
            output_formats = [supported_formats[0]]
            print(f"使用可用的 {supported_formats[0]} 格式")
        else:
            output_formats = []
            print("错误：没有可用的输出格式处理程序")
            
    return output_formats

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

def get_output_file_path(topic_name, is_journal=True, file_format="txt"):
    """根据专题名称、类型和文件格式获取输出文件路径"""
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
    
    # 根据输出格式修改文件扩展名
    # 移除已有的扩展名
    filename = re.sub(r'\.(txt|xlsx)$', '', filename, flags=re.IGNORECASE)
    # 添加指定的扩展名
    filename += f".{file_format}"
    
    # 确保目录存在
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    return os.path.join(output_directory, filename)

def save_topic_results(results, all_papers, topic_name, is_journal=True):
    """
    保存特定专题的结果到对应文件
    根据配置的输出格式保存一个或多个版本的文件
    
    Args:
        results: 详细结果列表
        all_papers: 所有论文列表
        topic_name: 专题名称
        is_journal: 是否为期刊（True为期刊，False为会议）
    """
    if not topic_name:
        topic_name = "未知专题"

    success_formats = []
    
    # 遍历所有配置的输出格式
    for fmt in output_formats:
        # 获取此格式的输出文件路径
        output_file = get_output_file_path(topic_name, is_journal, fmt)
    
        # 根据格式选择不同的保存方式
        if fmt == "txt" and TXT_SUPPORTED:
            if save_topic_results_to_txt(results, all_papers, topic_name, output_file, is_journal):
                success_formats.append(fmt)
        elif fmt == "xlsx" and EXCEL_SUPPORTED:
            if save_topic_results_to_excel(results, all_papers, topic_name, output_file, is_journal):
                success_formats.append(fmt)
    
    if success_formats:
        print(f"专题 '{topic_name}' 的结果已成功保存为以下格式: {', '.join(success_formats)}")
    else:
        print(f"错误：专题 '{topic_name}' 的结果保存失败")

def save_venue_result(venue_name, venue_full_name, year, papers, source_link, 
                     volume_link=None, contents_link=None, topic_name="", is_journal=True):
    """
    立即保存单个会议/期刊的结果到专题文件
    根据配置的输出格式保存一个或多个版本的文件
    
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
        kw_desc = _build_keyword_desc()
        print(f"未在 {venue_name} {year}年 找到{kw_desc}的论文，跳过保存")
        return
    
    if not topic_name:
        topic_name = "未知专题"
        
    success_formats = []
    
    # 遍历所有配置的输出格式
    for fmt in output_formats:
        # 获取此格式的输出文件路径
        output_file = get_output_file_path(topic_name, is_journal, fmt)
    
        # 根据格式选择不同的保存方式
        if fmt == "txt" and TXT_SUPPORTED:
            if save_venue_result_to_txt(venue_name, venue_full_name, year, papers, 
                                      source_link, volume_link, contents_link, 
                                      topic_name, is_journal, output_file):
                success_formats.append(fmt)
        elif fmt == "xlsx" and EXCEL_SUPPORTED:
            if save_venue_result_to_excel(venue_name, venue_full_name, year, papers, 
                                        source_link, volume_link, contents_link, 
                                        topic_name, is_journal, output_file):
                success_formats.append(fmt)
    
    if success_formats:
        print(f"已将 {venue_name} {year}年 的 {len(papers)} 篇论文结果保存为以下格式: {', '.join(success_formats)}")
    else:
        print(f"错误：{venue_name} {year}年 的论文结果保存失败")

def clean_text(text):
    """清理文本，去除非法字符"""
    return "".join(c for c in text if c not in r'\:*?"<>|') 