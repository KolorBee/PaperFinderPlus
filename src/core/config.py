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



# 关键词替换
# 单关键词：
#  TARGET_KEYWORDS = ["blockchain"]
# 多关键词（AND，默认）：
#  TARGET_KEYWORDS = ["blockchain", "ledger"]
# 切换到 OR 模式：
#  TARGET_KEYWORDS_MODE = 'OR'
# 启用词边界（英文场景）：
#  TARGET_KEYWORDS_WORD_BOUNDARY = True

TARGET_KEYWORDS = ["Fibonacci","blockchain"] 

# 关键词匹配模式: 'AND' 表示必须同时包含所有关键词, 'OR' 表示任一关键词即可
TARGET_KEYWORDS_MODE = 'AND'

# 是否在关键词匹配时使用词边界（word boundary）。
# 对于中文关键词通常设置为 False，因为 \b 对中文效果有限。
TARGET_KEYWORDS_WORD_BOUNDARY = False

# 匹配范围: 'title' 只匹配标题, 'entry' 只匹配条目整体, 'title_or_entry' 先尝试标题再条目（默认）
MATCH_SCOPE = 'title'

# 目标年份 TARGET_YEARS = ["2024", "2025"] 或者TARGET_YEARS = ["2024"]
TARGET_YEARS = ["2024", "2025"]

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