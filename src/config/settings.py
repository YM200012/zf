import os
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent

# 数据目录
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"

# 模型配置
MODEL_CONFIG = {
    "local": {
        "model_name": "/data/models/LvShang_32B",
        "embedding_model": "/data/models/m3e-base",
        "api_base": "http://localhost:8000/v1/",  # 本地模型服务地址
    },
    "online": {
        "model_name": "Qwen/Qwen3-32B",
        "api_base": "https://api.siliconflow.cn/v1",
        "api_key": "sk-eccxsnpdetsbgrqkfebysqhzvfljqmcsxmnjwmsrsldrtzki"
    }
}

# 文件路径配置
FILE_PATHS = {
    "category_file": str(RAW_DATA_DIR / "Category.xlsx"),
    "category_json": str(PROCESSED_DATA_DIR / "Category.json"),
    "capabilities_json": str(PROCESSED_DATA_DIR / "Capabilities.json"),
}

# LLM配置
LLM_CONFIG = {
    "context_window": 4096,
    "max_new_tokens": 1024,
    "temperature": 0.1,
    "do_sample": False,
}

# 创建必要的目录
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 模型配置
ONLINE_MODE = True  # True: 使用在线模型, False: 使用本地模型

# 文件路径配置
CAPABILITY_CONFIG = {
    "input_file": "data/raw/Input.xlsx",
    "output_file": "data/output/Output.xlsx",
    "category_file": "data/raw/Category.xlsx",
    "processed_category_file": "data/processed/Category.json"
} 