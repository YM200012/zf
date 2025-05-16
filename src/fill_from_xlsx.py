import pandas as pd
import json
import os
import logging
from datetime import datetime
from utils.llm_utils import call_llm

# 配置日志
def setup_logger():
    """配置日志记录器"""
    # 确保日志目录存在
    log_dir = "data/log"
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件名（包含时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"fill_{timestamp}.log")
    
    # 配置日志记录器
    logger = logging.getLogger("fill_from_xlsx")
    logger.setLevel(logging.INFO)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 创建日志记录器
logger = setup_logger()

def fill_capabilities(use_local_model: bool = False):
    """处理能力项数据"""
    # 加载分类数据
    with open("data/processed/Category.json", 'r', encoding='utf-8') as f:
        categories = json.load(f)
    
    # 读取能力项数据
    df = pd.read_excel("data/raw/Input.xlsx")
    total_rows = len(df)
    
    # 用于存储所有处理结果的列表
    all_results = []
    
    # 处理每一行
    for index, row in df.iterrows():
        description = f"{row['一级能力']} - {row['二级能力']} - {row['三级能力']}"
        if pd.notna(description):
            # 创建提示词
            categories_str = "\n".join([
                f"{cat['序号']}. {cat['一级指标']} - {cat['二级指标']} - {cat['三级指标']}"
                for cat in categories
            ])
            
            # 构建初始提示词
            prompt = f"""请分析以下关于装备能力的描述，并判断它最符合以下哪个能力项分类。请只返回最匹配的序号。

能力描述：{description}

可选分类：
{categories_str}

请只返回最匹配的序号数字，不要包含其他任何文字。"""
            
            try:
                # 调用模型
                matched_index = int(call_llm(prompt, use_local_model, temperature=0.0))
                
                # 找到对应的分类
                matched_category = None
                for cat in categories:
                    if cat['序号'] == matched_index:
                        matched_category = cat
                        df.at[index, '一级指标'] = cat['一级指标']
                        df.at[index, '二级指标'] = cat['二级指标']
                        df.at[index, '三级指标'] = cat['三级指标']
                        break
                
                # 输出进度信息
                logger.info(f"进度: {index + 1}/{total_rows}")
                logger.info(f"当前处理: {description}")
                if matched_category:
                    logger.info(f"匹配结果: {matched_category['序号']}. {matched_category['一级指标']} - {matched_category['二级指标']} - {matched_category['三级指标']}")
                logger.info("=" * 50)
                
                # 获取用户反馈
                logger.info("\n*****请输入反馈（直接回车继续，输入内容则重新匹配）：")
                user_feedback = input().strip()
                
                # 如果用户提供了反馈，重新匹配
                if user_feedback:
                    logger.info("\n根据用户反馈重新匹配...")
                    # 构建新的提示词
                    new_prompt = f"""请分析以下关于装备能力的描述，并判断它最符合以下哪个能力项分类。请只返回最匹配的序号。

请特别注意优先满足该指令：{user_feedback}

能力描述：{description}

可选分类：
{categories_str}

请只返回最匹配的序号数字，不要包含其他任何文字。"""
                    
                    # 重新调用模型
                    matched_index = int(call_llm(new_prompt, use_local_model, temperature=0.0))
                    
                    # 更新匹配结果
                    for cat in categories:
                        if cat['序号'] == matched_index:
                            matched_category = cat
                            df.at[index, '一级指标'] = cat['一级指标']
                            df.at[index, '二级指标'] = cat['二级指标']
                            df.at[index, '三级指标'] = cat['三级指标']
                            break
                    
                    logger.info("\n重新匹配结果:")
                    if matched_category:
                        logger.info(f"{matched_category['序号']}. {matched_category['一级指标']} - {matched_category['二级指标']} - {matched_category['三级指标']}")
                    logger.info("-" * 50)
                
                # 收集当前行的所有数据
                result_item = {
                    "序号": row["序号"],
                    "一级能力": row["一级能力"],
                    "二级能力": row["二级能力"],
                    "三级能力": row["三级能力"],
                    "能力需求": row["能力需求"],
                    "能力现状": row["能力现状"],
                    "能力差距": row["能力差距"],
                    "建设需求": row["建设需求"],
                    "一级指标": df.at[index, "一级指标"],
                    "二级指标": df.at[index, "二级指标"],
                    "三级指标": df.at[index, "三级指标"]
                }
                all_results.append(result_item)
                
            except (ValueError, IndexError):
                logger.info(f"警告：第{index+1}行匹配失败")
                logger.info("=" * 50)
    
    # 确保目录存在
    os.makedirs("data/output", exist_ok=True)
    
    # 保存Excel结果
    df.to_excel("data/output/Output.xlsx", index=False)
    
    # 保存JSON结果
    with open("data/output/Output.json", 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    logger.info("能力项处理完成，已生成Excel和JSON文件")

if __name__ == "__main__":
    # 处理能力项（使用在线模型）
    fill_capabilities(use_local_model=False) 