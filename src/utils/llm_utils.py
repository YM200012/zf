from openai import OpenAI
from config.settings import MODEL_CONFIG, LLM_CONFIG

def call_llm(prompt: str, use_local_model: bool = False, temperature: float = 0.0):
    """
    调用大模型进行推理
    
    Args:
        prompt: 提示词
        use_local_model: 是否使用本地模型
        api_key: API密钥
        temperature: 温度参数
    
    Returns:
        str: 模型返回的结果
    """
    # 初始化OpenAI客户端
    if use_local_model:
        model_config = MODEL_CONFIG["local"]
        pass
    else:
        model_config = MODEL_CONFIG["online"]
        client = OpenAI(
        base_url=model_config["api_base"],
        api_key=model_config["api_key"]
    )
    
    # 调用模型
    response = client.chat.completions.create(
        model=model_config["model_name"],
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的能力项分类专家，需要准确判断能力描述所属的分类。"
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        temperature=temperature,
        max_tokens=LLM_CONFIG["max_new_tokens"]
    )
    
    return response.choices[0].message.content.strip() 