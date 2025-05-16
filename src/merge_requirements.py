import json
import os
import logging
from datetime import datetime
from utils.llm_utils import call_llm
from config.settings import ONLINE_MODE

# 配置日志
def setup_logger():
    """配置日志记录器"""
    # 确保日志目录存在
    log_dir = "data/log"
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件名（包含时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"merge_{timestamp}.log")
    
    # 配置日志记录器
    logger = logging.getLogger("merge_requirements")
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

def check_semantic_similarity(text1: str, text2: str) -> bool:
    """检查两段文本是否描述同一事物
    
    Args:
        text1: 第一段文本
        text2: 第二段文本
    
    Returns:
        bool: 是否描述同一事物
    """
    prompt = f"""请判断以下两段文本是否描述的主体是否是同一个事物，只要描述的对象同一即可，具体的描述内容和指标可以不同。只需要回答"是"或"否"。

文本1：{text1}

文本2：{text2}

请只回答"是"或"否"："""
    
    response = call_llm(prompt, not ONLINE_MODE, temperature=0.0)
    logger.info(response)
    return "是" in response

def merge_similar_increments(increments: list, user_feedback: str = None) -> str:
    """合并相似的需求增量描述
    
    Args:
        increments: 需求增量描述列表
        user_feedback: 用户反馈的指导信息
    
    Returns:
        str: 合并后的需求增量描述
    """
    prompt = """我现在有若干条对军事装备领域特定装备的需求增量描述，请你阅读并理解，并将其中出现的指标合并。规则为：
同一装备的同一指标根据语义选择最高标准的指标（如打击距离要求，选择最大值；而响应时间要求，选择最小值）；其余的需求增量描述直接按照语义拼接即可。"""
    
    if user_feedback:
        prompt += f"\n请特别注意：{user_feedback}"
    
    prompt += """\n你的输出应当严格遵循以下格式：
合并结果：<你认为的合并结果>
以下是所有的需求增量描述，用回车隔开：\n""" + "\n".join(increments)
    
    response = call_llm(prompt, not ONLINE_MODE, temperature=0.0)
    logger.info(response)
    try:
        ans = response.split("合并结果：")[1].strip()
        return ans
    except:
        return "Format Error"

def generate_final_report(processed_data: list) -> str:
    """生成最终需求报告
    
    Args:
        processed_data: 处理后的数据
    
    Returns:
        str: 生成的需求报告
    """
    # 构建报告内容
    report_content = []
    for entry in processed_data:
        level1 = entry['能力项1级']
        level2 = entry['能力项2级']
        level3 = entry['能力项3级']
        
        for req in entry['需求列表']:
            report_content.append(f"能力项：{level1} - {level2} - {level3}")
            report_content.append(f"需求描述：{req['整体需求增量']}")
            report_content.append("-" * 50)
    
    # 构建提示词
    prompt = """请根据以下军事装备领域的需求描述，生成一份完整的需求报告。报告应包含：
1. 总体概述：简要总结所有需求的主要方向和重点
2. 分项总结：按照不同能力项，分条列举具体需求要点

以下是所有需求描述：
""" + "\n".join(report_content)
    
    # 调用大模型生成报告
    report = call_llm(prompt, not ONLINE_MODE, temperature=0.0)
    return report

def process_entry(entry, current_index: int = 0, total_entries: int = 0):
    """处理单个条目
    
    Args:
        entry: 输入条目
        current_index: 当前处理的条目索引
        total_entries: 总条目数
    
    Returns:
        dict: 处理后的条目
    """
    processed = entry.copy()
    increments = [req["能力需求"] for req in entry["需求列表"]]
    
    # 显示进度
    logger.info(f"\n处理进度: {current_index + 1}/{total_entries}")
    logger.info("=" * 50)
    logger.info(f"当前处理能力项: {entry['能力项1级']} - {entry['能力项2级']} - {entry['能力项3级']}")
    logger.info("=" * 50)
    
    # 对需求进行分组
    groups = []
    for increment in increments:
        # 检查是否属于已有组
        found_group = False
        for group in groups:
            # 检查与组内第一个元素是否相似
            if check_semantic_similarity(increment, group[0]):
                group.append(increment)
                found_group = True
                break
        
        # 如果不属于任何组，创建新组
        if not found_group:
            groups.append([increment])
    
    # 合并每个组内的需求
    merged_requirements = []
    for group in groups:
        if len(group) > 1:
            # 如果组内有多个需求，进行合并
            merged = merge_similar_increments(group)
            merged_requirements.append({
                "整体需求增量": merged,
                "原始内容": group
            })
            # 显示合并结果
            logger.info("\n合并结果:")
            logger.info(f"{merged}")
            logger.info("原始内容:")
            for content in group:
                logger.info(f"- {content}")
            logger.info("-" * 50)
            
            # 循环获取用户反馈，直到用户满意（输入enter）
            while True:
                logger.info("\n*****请输入反馈（直接回车继续，输入内容则重新合并）：")
                user_feedback = input().strip()
                
                # 如果用户输入enter，退出循环
                if not user_feedback:
                    break
                
                # 根据用户反馈重新合并
                logger.info("\n根据用户反馈重新合并...")
                merged = merge_similar_increments(group, user_feedback)
                merged_requirements[-1]["整体需求增量"] = merged
                logger.info("\n重新合并结果:")
                logger.info(f"{merged}")
                logger.info("-" * 50)
        else:
            # 如果组内只有一个需求，直接使用
            merged_requirements.append({
                "整体需求增量": group[0],
                "原始内容": group
            })
            # 显示单个需求
            logger.info("\n合并结果:")
            logger.info(f"{group[0]}")
            logger.info("原始内容:")
            logger.info(f"- {group[0]}")
            logger.info("-" * 50)
    
    processed["需求列表"] = merged_requirements
    return processed

def merge_requirements(input_file: str = "data/output/MergeInput.json", 
                      output_file: str = "data/output/MergedData.json",
                      report_file: str = "data/output/FinalReport.txt"):
    """合并需求数据
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        report_file: 报告文件路径
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 读取输入数据
    with open(input_file, "r", encoding='utf-8') as f:
        data = json.load(f)
    
    # 处理每个条目
    total_entries = len(data)
    processed_data = [
        process_entry(entry, idx, total_entries) 
        for idx, entry in enumerate(data)
    ]

    # 保存结果
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n需求合并完成，结果已保存至 {output_file}")
    
    # 生成并保存最终报告
    logger.info("\n正在生成最终需求报告...")
    final_report = generate_final_report(processed_data)
    
    with open(report_file, "w", encoding='utf-8') as f:
        f.write(final_report)
    
    logger.info(f"最终需求报告已保存至 {report_file}")

if __name__ == "__main__":
    # 合并需求
    merge_requirements()