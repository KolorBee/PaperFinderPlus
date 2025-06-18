"""
主入口文件，用于执行论文查找和分类任务
"""
import os
import time
import re
import argparse

from utils.data_extractor import extract_venue_info, read_links_from_file, get_topic_info_from_file
from crawlers.web_crawler import get_recent_volume_links, find_blockchain_papers, process_conference_page, get_journal_volume_links
from utils.file_handler import save_topic_results, save_venue_result, set_output_directory, set_output_formats, reset_file_counters
from core.config import INPUT_FILE, OUTPUT_DIR, JOURNAL_OUTPUT_FORMAT, CONFERENCE_OUTPUT_FORMAT, INPUT_DIR

def process_venue_link(link, venue_info, current_results, current_papers, current_topic="", is_current_journal=True):
    """处理单个会议/期刊链接"""
    print(f"\n处理链接: {link}")
    
    # 判断是期刊还是会议
    is_journal = "journals/" in link
    is_conference = "conf/" in link
    
    # 尝试从链接中提取期刊/会议名称及全称
    venue_name = "未知会议/期刊"
    venue_full_name = ""
    try:
        if is_conference:
            abbr = link.split("conf/")[1].split("/")[0].upper()
            venue_name = abbr
            for key, (full_name, url) in venue_info.items():
                if key.upper() == abbr or url in link:
                    venue_full_name = full_name
                    break
        elif is_journal:
            abbr = link.split("journals/")[1].split("/")[0].upper()
            venue_name = abbr
            for key, (full_name, url) in venue_info.items():
                if key.upper() == abbr or url in link:
                    venue_full_name = full_name
                    break
    except:
        pass
    
    venue_display = venue_name
    if venue_full_name:
        venue_display = f"{venue_name} ({venue_full_name})"
    
    # 根据类型使用不同的处理方法
    if is_journal:
        # 处理期刊
        print(f"检测到期刊链接，使用期刊处理逻辑")
        journal_volumes = get_journal_volume_links(link)
        
        if journal_volumes:
            print(f"找到 {len(journal_volumes)} 个近三年的期刊卷期")
            
            for year, volume_link in journal_volumes:
                print(f"处理 {year} 年的卷期: {volume_link}")
                papers = find_blockchain_papers(volume_link)
                
                if papers:
                    # 立即保存当前会议/期刊的结果 - 根据实际链接类型保存
                    save_venue_result(
                        venue_name=venue_name,
                        venue_full_name=venue_full_name,
                        year=year,
                        papers=papers,
                        source_link=link,
                        volume_link=volume_link,
                        topic_name=current_topic,
                        is_journal=True  # 明确指定为期刊
                    )
                    
                    # 同时保存到累计结果中
                    result_entry = f"\n## {venue_display} {year}年\n"
                    result_entry += f"- 来源: {link}\n"
                    result_entry += f"- 卷期: {volume_link}\n"
                    result_entry += f"- 找到的论文:\n"
                    current_results.append(result_entry)
                    
                    for paper in papers:
                        paper_title = paper
                        # 如果有DOI链接，只在current_papers中添加标题+doi链接的形式
                        doi_match = re.search(r'\[DOI: (https?://doi\.org/[^\]]+)\]', paper)
                        if doi_match:
                            doi_link = doi_match.group(1)
                            paper_title = paper.replace(f" [DOI: {doi_link}]", "")
                            current_results.append(f"  * {paper}")
                            current_papers.append(f"[{venue_name} {year}] {paper}")
                        else:
                            current_results.append(f"  * {paper}")
                            current_papers.append(f"[{venue_name} {year}] {paper}")
                
                # 避免请求过快
                time.sleep(2)
        else:
            print(f"未在期刊页面找到近三年的卷期链接，尝试使用通用方法")
            # 使用force=True强制处理已查询过的链接
            recent_volumes = get_recent_volume_links(link, force=True)
            
            for year, volume_link in recent_volumes:
                print(f"处理 {year} 年的卷期: {volume_link}")
                papers = find_blockchain_papers(volume_link)
                
                if papers:
                    # 立即保存当前会议/期刊的结果 - 根据实际链接类型保存
                    save_venue_result(
                        venue_name=venue_name,
                        venue_full_name=venue_full_name,
                        year=year,
                        papers=papers,
                        source_link=link,
                        volume_link=volume_link,
                        topic_name=current_topic,
                        is_journal=True  # 明确指定为期刊
                    )
                    
                    # 同时保存到累计结果中
                    result_entry = f"\n## {venue_display} {year}年\n"
                    result_entry += f"- 来源: {link}\n"
                    result_entry += f"- 卷期: {volume_link}\n"
                    result_entry += f"- 找到的论文:\n"
                    current_results.append(result_entry)
                    
                    for paper in papers:
                        current_results.append(f"  * {paper}")
                        current_papers.append(f"[{venue_name} {year}] {paper}")
                
                # 避免请求过快
                time.sleep(2)
    else:
        # 处理会议
        print(f"检测到会议链接，使用会议处理逻辑")
        contents_links = process_conference_page(link)
        
        if contents_links:
            print(f"直接在会议页面找到 {len(contents_links)} 个[contents]链接")
            
            for year, contents_link in contents_links:
                print(f"处理{year}年[contents]链接: {contents_link}")
                papers = find_blockchain_papers(contents_link)
                
                if papers:
                    # 立即保存当前会议/期刊的结果 - 根据实际链接类型保存
                    save_venue_result(
                        venue_name=venue_name,
                        venue_full_name=venue_full_name,
                        year=year,
                        papers=papers,
                        source_link=link,
                        contents_link=contents_link,
                        topic_name=current_topic,
                        is_journal=False  # 明确指定为会议
                    )
                    
                    # 同时保存到累计结果中
                    result_entry = f"\n## {venue_display} {year}年\n"
                    result_entry += f"- 来源: {link}\n"
                    result_entry += f"- Contents链接: {contents_link}\n"
                    result_entry += f"- 找到的论文:\n"
                    current_results.append(result_entry)
                    
                    for paper in papers:
                        current_results.append(f"  * {paper}")
                        current_papers.append(f"[{venue_name} {year}] {paper}")
                
                # 避免请求过快
                time.sleep(2)
        else:
            print(f"未在会议页面直接找到[contents]链接，尝试获取卷期链接")
            # 使用force=True强制处理已查询过的链接
            recent_volumes = get_recent_volume_links(link, force=True)
            print(f"找到 {len(recent_volumes)} 个近三年的卷期链接")
            
            for year, volume_link in recent_volumes:
                print(f"处理 {year} 年的卷期: {volume_link}")
                
                contents_links = process_conference_page(volume_link)
                
                if contents_links:
                    print(f"在卷期页面找到 {len(contents_links)} 个[contents]链接")
                    
                    for year_content, contents_link in contents_links:
                        print(f"处理{year_content}年[contents]链接: {contents_link}")
                        papers = find_blockchain_papers(contents_link)
                        
                        if papers:
                            # 立即保存当前会议/期刊的结果 - 根据实际链接类型保存
                            save_venue_result(
                                venue_name=venue_name,
                                venue_full_name=venue_full_name,
                                year=year_content,
                                papers=papers,
                                source_link=link,
                                volume_link=volume_link,
                                contents_link=contents_link,
                                topic_name=current_topic,
                                is_journal=False  # 明确指定为会议
                            )
                            
                            # 同时保存到累计结果中
                            result_entry = f"\n## {venue_display} {year_content}年\n"
                            result_entry += f"- 来源: {link}\n"
                            result_entry += f"- 卷期: {volume_link}\n"
                            result_entry += f"- Contents链接: {contents_link}\n"
                            result_entry += f"- 找到的论文:\n"
                            current_results.append(result_entry)
                            
                            for paper in papers:
                                current_results.append(f"  * {paper}")
                                current_papers.append(f"[{venue_name} {year_content}] {paper}")
                        
                        # 避免请求过快
                        time.sleep(2)
                else:
                    print(f"在卷期页面未找到[contents]链接，直接查找区块链论文")
                    papers = find_blockchain_papers(volume_link)
                    
                    if papers:
                        # 立即保存当前会议/期刊的结果 - 根据实际链接类型保存
                        save_venue_result(
                            venue_name=venue_name,
                            venue_full_name=venue_full_name,
                            year=year,
                            papers=papers,
                            source_link=link,
                            volume_link=volume_link,
                            topic_name=current_topic,
                            is_journal=False  # 明确指定为会议
                        )
                        
                        # 同时保存到累计结果中
                        result_entry = f"\n## {venue_display} {year}年\n"
                        result_entry += f"- 来源: {link}\n"
                        result_entry += f"- 卷期: {volume_link}\n"
                        result_entry += f"- 找到的论文:\n"
                        current_results.append(result_entry)
                        
                        for paper in papers:
                            current_results.append(f"  * {paper}")
                            current_papers.append(f"[{venue_name} {year}] {paper}")
                
                # 避免请求过快
                time.sleep(2)

def extract_topic_name(line):
    """从文本行中提取专题名称，并格式化处理"""
    # 匹配括号中的内容
    pattern = r'（([^）]+)）'
    match = re.search(pattern, line)
    if match:
        topic = match.group(1).strip()
        # 确保提取到了内容
        if topic:
            return topic
    
    # 如果没有找到有效的专题名称，返回默认值
    return "未知专题"

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='论文查找和分类工具')
    
    # 输入相关参数
    parser.add_argument('--input-dir', dest='input_dir', 
                        help='输入文件目录路径，默认为当前目录')
    parser.add_argument('--input-file', dest='input_file', 
                        help=f'输入文件名，默认为 {INPUT_FILE}')
    
    # 输出相关参数
    parser.add_argument('--output-dir', dest='output_dir', 
                        help=f'输出目录路径，默认为 {OUTPUT_DIR}')
    parser.add_argument('--journal-format', dest='journal_format',
                        help='期刊类输出文件名格式，使用{topic}作为专题名称占位符')
    parser.add_argument('--conference-format', dest='conference_format',
                        help='会议类输出文件名格式，使用{topic}作为专题名称占位符')
    parser.add_argument('--output-format', dest='output_format', choices=['txt', 'xlsx'],
                        help='输出文件格式，可选txt或xlsx，默认为txt')
    
    return parser.parse_args()

def main():
    """主函数"""
    # 重置文件计数器，确保每次运行时文件编号从1开始
    reset_file_counters()
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置输入文件路径
    input_file_path = args.input_file or INPUT_FILE
    input_dir = args.input_dir or INPUT_DIR
    
    if args.input_dir:
        # 导入数据提取模块中的全局变量
        import data_extractor
        data_extractor.INPUT_DIR = args.input_dir
    
    # 设置输出目录
    if args.output_dir:
        set_output_directory(args.output_dir)
    
    # 设置输出文件名格式
    set_output_formats(args.journal_format, args.conference_format)
    
    # 设置输出文件格式（txt或xlsx）
    if args.output_format:
        from utils.file_handler import set_output_format
        set_output_format(args.output_format)
    
    # 检查模板文件是否存在
    # 先尝试在input_dir中找文件
    template_file = os.path.join(input_dir, input_file_path)
    if not os.path.exists(template_file):
        # 如果未找到，尝试在当前目录中查找
        template_file = input_file_path
        if not os.path.exists(template_file):
            print(f"错误: 模板文件 {input_file_path} 不存在于 {input_dir} 目录或当前目录")
            return
    
    # 提取会议/期刊信息
    venue_info = extract_venue_info(template_file)
    if not venue_info:
        print("错误: 无法提取会议/期刊信息")
        return
    
    # 提取专题信息
    topic_info = get_topic_info_from_file(template_file)
    if not topic_info:
        print("错误: 无法提取专题信息")
        return
        
    for topic_name, (journal_links, conference_links) in topic_info.items():
        print(f"\n\n处理专题: {topic_name}")
        
        # 跟踪当前专题的所有结果
        current_journal_results = []
        current_journal_papers = []
        current_conference_results = []
        current_conference_papers = []
        
        # 处理期刊链接
        print(f"\n处理专题 '{topic_name}' 的期刊链接:")
        for link in journal_links:
            process_venue_link(link, venue_info, current_journal_results, current_journal_papers, topic_name, is_current_journal=True)
            # 避免请求过快
            time.sleep(1)
            
        # 处理会议链接
        print(f"\n处理专题 '{topic_name}' 的会议链接:")
        for link in conference_links:
            process_venue_link(link, venue_info, current_conference_results, current_conference_papers, topic_name, is_current_journal=False)
            # 避免请求过快
            time.sleep(1)
            
        # 保存当前专题的期刊和会议结果
        save_topic_results(current_journal_results, current_journal_papers, topic_name, is_journal=True)
        save_topic_results(current_conference_results, current_conference_papers, topic_name, is_journal=False)

if __name__ == "__main__":
    main() 