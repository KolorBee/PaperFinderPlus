"""
网页爬取模块，用于从网页中爬取相关数据
"""
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin
from core.config import PROXIES, TIMEOUT, TARGET_YEARS

# 存储已查询过的链接
queried_links = set()

def get_recent_volume_links(url, force=False):
    """获取指定URL页面上近三年的卷期链接
    
    Args:
        url: 要处理的URL
        force: 是否强制处理已查询过的链接
    """
    try:
        # 检查链接是否已查询过
        if not force and url in queried_links:
            print(f"链接已查询过，跳过: {url}")
            return []
            
        queried_links.add(url)  # 将链接添加到已查询集合
        print(f"正在处理页面: {url}")
        response = requests.get(url, timeout=TIMEOUT, proxies=PROXIES)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 寻找卷期链接
        recent_volume_links = []
        years = TARGET_YEARS
        
        # DBLP页面上的卷期链接通常在列表项中
        volume_pattern = re.compile(r'Volume\s+\d+.*?(\d{4})')
        
        # 查找所有链接
        for link in soup.find_all('a'):
            link_text = link.get_text().strip()
            match = volume_pattern.search(link_text)
            
            if match and match.group(1) in years:
                year = match.group(1)
                href = link.get('href')
                if href:
                    full_url = urljoin(url, href)
                    recent_volume_links.append((year, full_url))
                    print(f"找到 {year} 年的卷期链接: {full_url}")
        
        # 如果没有找到符合格式的链接，尝试查找其他格式的年份链接
        if not recent_volume_links:
            for link in soup.find_all('a'):
                link_text = link.get_text().strip()
                # 检查链接文本是否仅包含年份
                if link_text in years:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(url, href)
                        recent_volume_links.append((link_text, full_url))
                        print(f"找到 {link_text} 年的链接: {full_url}")
                # 检查链接是否包含年份和其他文本
                elif any(year in link_text for year in years):
                    for year in years:
                        if year in link_text:
                            href = link.get('href')
                            if href:
                                full_url = urljoin(url, href)
                                recent_volume_links.append((year, full_url))
                                print(f"找到包含 {year} 年的链接: {full_url}")
        
        return recent_volume_links
    except Exception as e:
        print(f"获取 {url} 的卷期链接时出错: {e}")
        return []

def extract_doi(parent):
    """
    从论文条目中提取DOI链接
    
    Args:
        parent: 论文条目的父元素
        
    Returns:
        DOI链接或None（如果未找到）
    """
    if not parent:
        return None
    
    # 首先优先查找class="drop-down"块中的head块内的链接（会议论文链接）
    dropdown = parent.select_one('.drop-down')
    if dropdown:
        head_div = dropdown.select_one('.head')
        if head_div:
            link = head_div.find('a')
            if link and link.get('href'):
                return link.get('href')
    
    # 如果没找到，再查找其他可能的DOI链接
    for link in parent.find_all('a'):
        href = link.get('href', '')
        # 先检查标准DOI链接
        if 'doi.org' in href:
            # 直接返回完整的DOI链接
            return href
            
        # 保存可能的会议链接（以https开头）
        if href.startswith('https://') and ('conference' in href or 'conf' in href or 'proceedings' in href or 'paper' in href or 'presentation' in href):
            return href
            
        # 有时DOI可能在链接的标题或属性中
        title = link.get('title', '')
        if 'doi.org' in title or 'DOI' in title:
            if 'doi.org' in title:
                match = re.search(r'(https?://doi\.org/\S+)(?:\s|"|\'|$)', title)
                if match:
                    return match.group(1)
            # 对于其他形式的DOI链接，检查href
            if href and ('doi' in href or 'DOI' in href):
                return href
    
    # 处理直接嵌在文本中的DOI - 修改为不截断DOI链接尾部
    text = parent.get_text()
    doi_pattern = re.compile(r'(https?://doi\.org/\S+?)(?:\s|\)|$)')
    match = doi_pattern.search(text)
    if match:
        return match.group(1)
    
    # 最后尝试获取任何有效的https链接
    for link in parent.find_all('a'):
        href = link.get('href', '')
        if href.startswith('https://'):
            return href
    
    return None

def find_blockchain_papers(url):
    """在论文列表页面查找包含blockchain关键词的论文，并提取DOI链接"""
    try:
        # 检查链接是否已查询过
        if url in queried_links:
            print(f"链接已查询过，跳过: {url}")
            return []
            
        queried_links.add(url)  # 将链接添加到已查询集合
        print(f"处理链接: {url}")
        response = requests.get(url, timeout=TIMEOUT, proxies=PROXIES)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        blockchain_papers = []
        
        # DBLP内容页面通常有span.title元素
        title_elements = soup.select('span.title')
        if not title_elements:
            # 如果没有找到span.title，尝试其他常见的标题元素
            title_elements = soup.select('li.entry .title, li.entry div.data cite, li.entry')
        
        for element in title_elements:
            title = element.get_text().strip()
            # 关键词替换
            if re.search(r'Graph', title, re.IGNORECASE):
                print(f"找到区块链相关标题: {title}")
                if len(title) > 10 and len(title) < 300:  # 过滤过短或过长的标题
                    cleaned_title = re.sub(r'\s+', ' ', title).strip()
                    
                    # 找到整个论文条目元素
                    parent_entry = element.find_parent('li.entry') or element.find_parent('li') or element.find_parent('div.entry') or element.find_parent('div')
                    
                    # 提取DOI链接
                    doi_link = extract_doi(parent_entry)
                    
                    paper_entry = cleaned_title
                    if doi_link:
                        paper_entry = f"{cleaned_title} [DOI: {doi_link}]"
                        print(f"找到DOI链接: {doi_link}")
                    else:
                        print(f"未找到DOI链接")
                    
                    if paper_entry not in blockchain_papers:
                        blockchain_papers.append(paper_entry)
                        print(f"添加区块链相关论文: {paper_entry}")
        
        # 如果没有找到论文，尝试在整个页面内容中搜索
        if not blockchain_papers:
            print("使用备用方法查找区块链论文...")
            # 尝试查找所有可能的文章条目
            entries = soup.select('li.entry, .data, .publ-list > *')
            for entry in entries:
                entry_text = entry.get_text().lower()
                # 关键词替换
                if 'Graph' in entry_text:
                    # 从条目中提取标题
                    title_element = entry.select_one('.title') or entry
                    title = title_element.get_text().strip()
                    if len(title) > 10 and len(title) < 300:
                        cleaned_title = re.sub(r'\s+', ' ', title).strip()
                        
                        # 提取DOI链接
                        doi_link = extract_doi(entry)
                                
                        paper_entry = cleaned_title
                        if doi_link:
                            paper_entry = f"{cleaned_title} [DOI: {doi_link}]"
                            print(f"通过备用方法找到DOI链接: {doi_link}")
                        else:
                            print(f"通过备用方法未找到DOI链接")
                            
                        if paper_entry not in blockchain_papers:
                            blockchain_papers.append(paper_entry)
                            print(f"通过备用方法添加区块链相关论文: {paper_entry}")
        
        return blockchain_papers
    except Exception as e:
        print(f"查找论文时出错 {url}: {e}")
        return []

def process_conference_page(url):
    """处理会议页面，查找近三年会议条目右侧的[contents]链接"""
    try:
        # 检查链接是否已查询过
        if url in queried_links:
            print(f"链接已查询过，跳过: {url}")
            return []
            
        queried_links.add(url)  # 将链接添加到已查询集合
        print(f"正在处理会议页面: {url}")
        response = requests.get(url, timeout=TIMEOUT, proxies=PROXIES)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        contents_links = []
        years = TARGET_YEARS
        
        # 直接查找所有包含[contents]的链接
        contents_elements = soup.find_all('a', string='[contents]')
        
        for contents_element in contents_elements:
            # 查找链接所在行的上下文
            parent_li = contents_element.find_parent('li')
            if not parent_li:
                continue
                
            # 获取该行的所有文本
            line_text = parent_li.get_text()
            
            # 检查是否包含我们需要的年份
            for year in years:
                if year in line_text:
                    contents_url = urljoin(url, contents_element.get('href'))
                    contents_links.append((year, contents_url))
                    print(f"找到{year}年的[contents]链接: {contents_url}")
                    break
        
        return contents_links
    except Exception as e:
        print(f"处理会议页面时出错 {url}: {e}")
        return []

def get_journal_volume_links(url):
    """获取期刊页面上近三年的卷期链接"""
    try:
        # 检查链接是否已查询过
        if url in queried_links:
            print(f"链接已查询过，跳过: {url}")
            return []
            
        queried_links.add(url)  # 将链接添加到已查询集合
        print(f"正在处理期刊页面: {url}")
        response = requests.get(url, timeout=TIMEOUT, proxies=PROXIES)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        recent_volume_links = []
        years = TARGET_YEARS
        
        # 查找所有链接
        links = soup.find_all('a')
        
        # 期刊页面通常有"Volume X: YYYY"格式的链接
        volume_pattern = re.compile(r'Volume\s+\d+:?\s*(\d{4})')
        
        for link in links:
            link_text = link.get_text().strip()
            match = volume_pattern.search(link_text)
            
            if match and match.group(1) in years:
                year = match.group(1)
                href = link.get('href')
                if href:
                    full_url = urljoin(url, href)
                    recent_volume_links.append((year, full_url))
                    print(f"找到期刊{year}年的卷期链接: {full_url}")
        
        return recent_volume_links
    except Exception as e:
        print(f"获取期刊 {url} 的卷期链接时出错: {e}")
        return [] 