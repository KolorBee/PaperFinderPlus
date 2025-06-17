"""
数据提取模块，用于从文件中提取会议/期刊信息
"""
import os
import re
from core.config import INPUT_FILE, INPUT_DIR

def get_full_input_path(file_path=None):
    """获取完整的输入文件路径"""
    if file_path is None:
        file_path = INPUT_FILE
    
    # 如果是绝对路径，直接返回
    if os.path.isabs(file_path):
        return file_path
    
    # 现在INPUT_DIR已是绝对路径，直接在其下查找文件
    input_file_path = os.path.join(INPUT_DIR, file_path)
    if os.path.exists(input_file_path):
        return input_file_path
    
    # 如果在指定的输入目录中没有找到，尝试在当前目录查找
    current_dir_path = os.path.join(os.getcwd(), file_path)
    if os.path.exists(current_dir_path):
        return current_dir_path
    
    # 最后返回默认路径
    return os.path.join(INPUT_DIR, file_path)

def extract_venue_info(file_path=None):
    """提取会议/期刊的简称、全称和网址信息"""
    full_path = get_full_input_path(file_path)
    
    venue_info = {}  # {简称: (全称, 网址)}
    
    try:
        with open(full_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                # 检测当前处理的是期刊还是会议
                if "期刊" in line:
                    current_section = "journals"
                elif "会议" in line:
                    current_section = "conferences"
                    
                # 跳过表头和空行
                if not line or "序号" in line or "网址" in line or "A 类" in line:
                    continue
                    
                # 尝试提取会议/期刊信息
                if 'http' in line and current_section:
                    parts = line.split()
                    if len(parts) >= 4:  # 至少包含序号、简称、全称和网址
                        # 找到URL的位置
                        url_index = -1
                        for i, part in enumerate(parts):
                            if part.startswith('http'):
                                url_index = i
                                break
                        
                        if url_index > 1:  # 确保有简称和URL
                            abbr = parts[1]  # 通常简称在第二列
                            full_name = ' '.join(parts[2:url_index])  # 全称可能有多个单词
                            url = parts[url_index]
                            venue_info[abbr] = (full_name, url)
                            print(f"提取到会议/期刊: {abbr} - {full_name}")
        
        print(f"共提取到 {len(venue_info)} 个会议/期刊信息")
        return venue_info
    except Exception as e:
        print(f"提取会议/期刊信息时出错: {e}")
        return {}

def read_links_from_file(file_path=None):
    """从文件中读取链接，适应表格式的输入文件"""
    full_path = get_full_input_path(file_path)
        
    links = []
    try:
        with open(full_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                # 匹配包含http的URL
                if 'http' in line:
                    # 提取URL（通常在行尾）
                    parts = line.split()
                    for part in parts:
                        if part.startswith('http'):
                            links.append(part)
                            break
        print(f"从文件中成功提取了 {len(links)} 个链接")
        return links
    except Exception as e:
        print(f"读取文件 {full_path} 时出错: {e}")
        return []

def get_topic_info_from_file(file_path=None):
    """从文件中提取专题信息和对应的链接"""
    full_path = get_full_input_path(file_path)
        
    topic_info = {}  # {专题名称: ([期刊链接], [会议链接])}
    
    try:
        with open(full_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # 查找所有期刊专题部分
            journal_sections = re.findall(r'中国计算机学会推荐国际学术期刊\s*（([^）]+)）(.*?)(?=中国计算机学会推荐国际学术|$)', content, re.DOTALL)
            
            # 查找所有会议专题部分
            conference_sections = re.findall(r'中国计算机学会推荐国际学术会议\s*（([^）]+)）(.*?)(?=中国计算机学会推荐国际学术|$)', content, re.DOTALL)
            
            # 处理期刊专题
            for topic, section_content in journal_sections:
                topic = topic.strip()
                print(f"处理期刊专题: {topic}")
                
                # 提取该专题下的链接
                links = []
                for line in section_content.split('\n'):
                    if 'http' in line:
                        parts = line.split()
                        for part in parts:
                            if part.startswith('http'):
                                links.append(part)
                                print(f"  - 添加期刊链接: {part}")
                                break
                
                # 添加到专题信息中
                if topic in topic_info:
                    existing_journals, existing_conferences = topic_info[topic]
                    topic_info[topic] = (existing_journals + links, existing_conferences)
                else:
                    topic_info[topic] = (links, [])
            
            # 处理会议专题
            for topic, section_content in conference_sections:
                topic = topic.strip()
                print(f"处理会议专题: {topic}")
                
                # 提取该专题下的链接
                links = []
                for line in section_content.split('\n'):
                    if 'http' in line:
                        parts = line.split()
                        for part in parts:
                            if part.startswith('http'):
                                links.append(part)
                                print(f"  - 添加会议链接: {part}")
                                break
                
                # 添加到专题信息中
                if topic in topic_info:
                    existing_journals, existing_conferences = topic_info[topic]
                    topic_info[topic] = (existing_journals, existing_conferences + links)
                else:
                    topic_info[topic] = ([], links)
        
        # 创建默认专题，以防没有提取到任何专题
        if not topic_info:
            print("未找到任何专题，创建默认专题")
            # 提取所有链接
            links = read_links_from_file(full_path)
            # 区分期刊和会议链接
            journal_links = [link for link in links if 'journals/' in link]
            conference_links = [link for link in links if 'conf/' in link]
            topic_info["默认专题"] = (journal_links, conference_links)
        
        print(f"共提取到 {len(topic_info)} 个专题信息")
        for topic, (journals, conferences) in topic_info.items():
            print(f"专题 '{topic}': {len(journals)} 个期刊链接, {len(conferences)} 个会议链接")
        
        return topic_info
    except Exception as e:
        print(f"提取专题信息时出错: {e}")
        import traceback
        traceback.print_exc()
        return {} 