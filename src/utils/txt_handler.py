"""
文本文件输出处理模块，专门用于生成文本格式的结果文件
"""
import os
import re

# 从excel_handler模块导入DOI提取函数，保持一致性
# 如果excel_handler不可用，则在本模块中实现该函数
try:
    from .excel_handler import extract_doi_link
except ImportError:
    def extract_doi_link(paper):
        """
        从论文条目中提取DOI链接
        
        Args:
            paper: 原始论文条目文本
            
        Returns:
            (paper_title, doi_link): 论文标题和DOI链接（无链接则返回空字符串）
        """
        # 检查是否包含标准DOI链接
        doi_match = re.search(r'\[DOI: (https?://doi\.org/[^\]]+)\]', paper)
        if doi_match:
            doi_link = doi_match.group(1)
            # 移除原始DOI标记
            paper_title = paper.replace(f" [DOI: {doi_link}]", "")
            return paper_title, doi_link
        
        # 检查是否包含会议链接作为DOI（新增支持）
        conf_match = re.search(r'\[DOI: (https?://[^\]]+)\]', paper)
        if conf_match:
            doi_link = conf_match.group(1)
            # 移除原始DOI标记
            paper_title = paper.replace(f" [DOI: {doi_link}]", "")
            return paper_title, doi_link
        
        # 如果使用其他格式，也尝试提取
        doi_match = re.search(r'DOI: (https?://doi\.org/\S+)', paper)
        if doi_match:
            doi_link = doi_match.group(1)
            # 移除原始DOI标记
            paper_title = paper.replace(f" DOI: {doi_link}", "")
            return paper_title, doi_link
        
        # 尝试提取其他格式的会议链接（新增支持）
        conf_match = re.search(r'DOI: (https?://\S+)', paper)
        if conf_match:
            doi_link = conf_match.group(1)
            # 移除原始DOI标记
            paper_title = paper.replace(f" DOI: {doi_link}", "")
            return paper_title, doi_link
        
        return paper, ""

def format_paper_with_doi(paper):
    """
    格式化论文条目，提取DOI链接并以更美观的方式显示
    
    Args:
        paper: 原始论文条目文本
        
    Returns:
        格式化后的论文条目
    """
    # 提取DOI链接
    paper_title, doi_link = extract_doi_link(paper)
    
    # 如果有DOI链接，则以更美观的方式显示
    if doi_link:
        return f"{paper_title} DOI: {doi_link}"
    
    return paper

def save_topic_results(results, all_papers, topic_name, output_file, is_journal=True):
    """保存结果到文本文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write("# 包含关键词的论文\n")
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
        
        return True
    except Exception as e:
        print(f"保存文本文件时出错: {e}")
        return False

def save_venue_result(venue_name, venue_full_name, year, papers, source_link, 
                     volume_link=None, contents_link=None, topic_name="",
                     is_journal=True, output_file=None):
    """
    保存单个会议/期刊的结果到文本文件
    
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
        output_file: 输出文件路径
    """
    if not output_file:
        print("错误：未指定输出文件路径")
        return False
    
    try:
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
                file.write("# 包含关键词的论文\n")
                file.write("="*50 + "\n\n")
                file.write("## 详细信息\n\n")
                file.write(result_entry)
        else:
            # 文件已存在，追加内容
            with open(output_file, 'a', encoding='utf-8') as file:
                file.write(result_entry)
        
        return True
    except Exception as e:
        print(f"保存文本文件时出错: {e}")
        return False 