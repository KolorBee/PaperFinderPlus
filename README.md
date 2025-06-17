# PaperFinder - 论文查找和分类工具

PaperFinder 是一个用于从学术网站查找包含特定关键词的论文并进行分类整理的工具。目前专注于查找区块链相关论文。

## 项目结构

```
paperfinder/
├── run.py                  # 启动文件
├── requirements.txt        # 项目依赖
├── README.md               # 项目说明
├── input/                  # 输入文件目录
├── output/                 # 输出文件目录
└── src/                    # 源代码目录
    ├── main.py             # 主程序入口
    ├── core/               # 核心功能模块
    │   ├── __init__.py
    │   └── config.py       # 配置文件
    ├── utils/              # 工具函数模块
    │   ├── __init__.py
    │   ├── data_extractor.py  # 数据提取模块
    │   └── file_handler.py    # 文件处理模块
    └── crawlers/           # 网络爬虫模块
        ├── __init__.py
        └── web_crawler.py  # 网页爬取模块
```

## 主要功能

- 从指定的文件中读取会议/期刊信息和链接
- 自动查找并识别近三年内的论文
- 基于关键词筛选相关论文
- 按照专题分类整理结果
- 将结果保存为文本文件

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python run.py
```

这将使用默认配置运行程序，读取当前目录下的`input/新建文本文档.txt`作为输入文件，并将结果保存在`output`目录中。

### 定制输入和输出

现在支持通过命令行参数自定义输入目录、输入文件、输出目录以及期刊类和会议类的输出文件格式：

```bash
python run.py --input-dir "your_input_directory" --input-file "your_input_file.txt" --output-dir "your_output_directory"
```

### 可用命令行参数

- `--input-dir`: 指定输入文件所在目录
- `--input-file`: 指定输入文件名
- `--output-dir`: 指定输出目录
- `--journal-format`: 设置期刊类输出文件名格式，使用`{topic}`作为专题名称占位符
- `--conference-format`: 设置会议类输出文件名格式，使用`{topic}`作为专题名称占位符

示例：

```bash
# 自定义输入和输出路径
python run.py --input-dir "data" --input-file "venues.txt" --output-dir "results"

# 自定义输出文件名格式
python run.py --journal-format "期刊_{topic}.txt" --conference-format "会议_{topic}.txt"

# 完整示例
python run.py --input-dir "data" --input-file "venues.txt" --output-dir "results" --journal-format "期刊_{topic}.txt" --conference-format "会议_{topic}.txt"
```

## 输入文件格式

输入文件应包含会议和期刊信息，格式类似于：

```
中国计算机学会推荐国际学术期刊（计算机体系结构-并行与分布计算-存储系统）
序号 简称 全称 网址
1 TOCS ACM Transactions on Computer Systems http://tocs.acm.org/

中国计算机学会推荐国际学术会议（计算机体系结构-并行与分布计算-存储系统）
序号 简称 全称 网址
1 ASPLOS Architectural Support for Programming Languages and Operating Systems https://www.asplos2023.org/
```

## 结果输出

程序会按照专题和类别（期刊/会议）分别生成结果文件，包含找到的区块链相关论文信息。 