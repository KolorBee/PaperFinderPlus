"""
PaperFinder启动文件
"""
import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# 导入主程序
from main import main

if __name__ == "__main__":
    main() 