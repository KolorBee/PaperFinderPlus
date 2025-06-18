"""
配置文件，包含全局常量和配置项
"""
import os

# 获取项目根目录的路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 代理设置，默认为None，可以根据需要修改
PROXIES = None
# 例如: PROXIES = {'http': 'http://127.0.0.1:10809', 'https': 'http://127.0.0.1:10809'}

# 请求超时时间设置为30秒
TIMEOUT = 30

# 目标年份
TARGET_YEARS = ["2023", "2024", "2025"]

# 关键词
TARGET_KEYWORDS = ["blockchain"]

# 输入配置
INPUT_DIR = os.path.join(ROOT_DIR, "input")  # 输入目录，设置为根目录下的input
INPUT_FILE = "新建文本文档.txt"  # 输入文件名

# 输出配置
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")  # 结果输出目录，设置为根目录下的output

# 输出格式，支持"txt"或"xlsx"或两者都支持"txt, xlsx"
# 多种格式之间用逗号分隔，例如："txt, xlsx"
OUTPUT_FORMAT = "txt, xlsx"  # 默认为txt文本格式

# 输出文件名格式
JOURNAL_OUTPUT_FORMAT = "学术期刊 类别A （{topic}）.txt"  # 期刊类输出文件格式
CONFERENCE_OUTPUT_FORMAT = "学术会议 类别A （{topic}）.txt"  # 会议类输出文件格式 