import pandas as pd
import json
import os

def process_input_to_json():
    """将输入表格转换为能力项JSON格式"""
    # 读取输入Excel
    df = pd.read_excel("data/raw/Category.xlsx")
    
    # 转换为JSON格式
    categories = []
    last_values = {"一级指标": "", "二级指标": "", "三级指标": ""}
    
    for _, row in df.iterrows():
        # 处理合并单元格的情况
        for field in ["一级指标", "二级指标", "三级指标"]:
            if pd.notna(row[field]):
                last_values[field] = row[field]
        
        category = {
            "序号": row["序号"],
            "一级指标": last_values["一级指标"],
            "二级指标": last_values["二级指标"],
            "三级指标": last_values["三级指标"]
        }
        categories.append(category)
    
    # 确保目录存在
    os.makedirs("data/processed", exist_ok=True)
    
    # 保存JSON
    with open("data/processed/Category.json", 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)
    print("分类体系JSON已保存到: data/processed/Category.json")

if __name__ == "__main__":
    process_input_to_json() 