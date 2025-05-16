# 军事装备需求分析系统

本系统用于处理和分析军事装备领域的需求数据，支持从Excel文件到结构化数据的转换、需求匹配和需求合并等功能。

## 项目结构

```
.
├── data/                # 数据目录
│   ├── raw/            # 原始数据
│   ├── processed/      # 中间处理数据
│   └── output/         # 输出结果
├── src/                # 源代码
│   ├── config/         # 配置文件
│   ├── utils/          # 工具函数
│   ├── process_category.py    # 分类系统处理
│   ├── fill_from_xlsx.py      # Excel数据填充
│   └── merge_requirements.py  # 需求合并
├── other/              # 其他代码（历史版本和未使用代码）
├── requirements.txt    # 项目依赖
└── README.md          # 项目说明
```

## 功能说明

### 1. 分类系统处理 (process_category.py)

将分类系统Excel文件转换为JSON格式。

**输入文件**：
- 位置：`data/raw/Category.xlsx`
- 格式：Excel文件，包含分类系统的层级结构

**输出文件**：
- 位置：`data/processed/Category.json`
- 格式：JSON文件，包含处理后的分类系统数据

**使用方法**：
```bash
python src/process_category.py
```

### 2. Excel数据填充 (fill_from_xlsx.py)

将Excel文件中的能力项与分类系统进行匹配，并生成结构化数据。

**输入文件**：
- 位置：`data/raw/Input.xlsx`
- 格式：Excel文件，包含能力项描述

**输出文件**：
- 位置：`data/output/Output.xlsx` 和 `data/output/Output.json`
- 格式：Excel文件和JSON文件，包含匹配结果

**使用方法**：
```bash
python src/fill_from_xlsx.py
```

### 3. 需求合并 (merge_requirements.py)

将相似的需求描述进行合并，并生成需求报告。

**输入文件**：
- 位置：`data/output/MergeInput.json`
- 格式：JSON文件，包含需要合并的需求数据

**输出文件**：
- 位置：`data/output/MergedData.json` 和 `data/output/FinalReport.txt`
- 格式：JSON文件（合并后的需求数据）和文本文件（需求报告）

**使用方法**：
```bash
python src/merge_requirements.py
```

**交互功能**：
- 在处理过程中，系统会显示每个合并结果
- 用户可以选择直接回车继续，或输入反馈来调整合并结果
- 最终会生成一份包含总体概述和分项总结的需求报告

## 环境要求

- Python 3.8+
- 依赖包：见 requirements.txt

## 安装

```bash
pip install -r requirements.txt
```

## 模型配置

系统支持在线和离线两种模型模式，可以通过修改配置文件轻松切换：

1. 打开 `src/config/settings.py`
2. 修改 `ONLINE_MODE` 参数：
   - `ONLINE_MODE = True`: 使用在线模型（默认）
   - `ONLINE_MODE = False`: 使用本地模型

**注意事项**：
- 使用在线模型需要确保网络连接正常
- 使用本地模型需要确保模型文件已正确部署
- 切换模型模式后，所有功能模块都会自动使用相应的模型

## 注意事项

1. 确保输入文件放在正确的目录下
2. 处理大量数据时，建议使用在线模型（默认配置）
3. 如需使用本地模型，请修改配置文件中的相关设置