AGENT_SYSTEM_PROMPT = """
你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具:
- `get_weather(city: str)`: 查询指定城市的实时天气。
- `get_attraction(city: str, weather: str)`: 根据城市和天气搜索推荐的旅游景点。

# 行动格式:
你的回答必须严格遵循以下格式。首先是你的思考过程，然后是你要执行的具体行动，每次回复只输出一对Thought-Action：
Thought: [这里是你的思考过程和下一步计划]
Action: [这里是你要调用的工具，格式为 function_name(arg_name="arg_value")]

# 任务完成:
当你收集到足够的信息，能够回答用户的最终问题时，你必须在`Action:`字段后使用 `finish(answer="...")` 来输出最终答案。

请开始吧！
"""


import requests
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_weather(city: str) -> str:
    """
    通过调用 wttr.in API 查询真实的天气信息。
    """
    # API端点，我们请求JSON格式的数据
    url = f"https://wttr.in/{city}?format=j1"
    
    try:
        # 发起网络请求
        response = requests.get(url)
        # 检查响应状态码是否为200 (成功)
        response.raise_for_status() 
        # 解析返回的JSON数据
        data = response.json()
        
        # 提取当前天气状况
        current_condition = data['current_condition'][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']
        
        # 格式化成自然语言返回
        return f"{city}当前天气：{weather_desc}，气温{temp_c}摄氏度"
        
    except requests.exceptions.RequestException as e:
        # 处理网络错误
        return f"错误：查询天气时遇到网络问题 - {e}"
    except (KeyError, IndexError) as e:
        # 处理数据解析错误
        return f"错误：解析天气数据失败，可能是城市名称无效 - {e}"



import os
from tavily import TavilyClient

def get_attraction(city: str, weather: str) -> str:
    """
    根据城市和天气，使用Tavily Search API搜索并返回优化后的景点推荐。
    """

    # 从环境变量或主程序配置中获取API密钥
    api_key = os.environ.get("TAVILY_API_KEY") # 推荐方式
    # 或者，我们可以在主循环中传入，如此处代码所示

    if not api_key:
        return "错误：未配置TAVILY_API_KEY。"

    # 2. 初始化Tavily客户端
    tavily = TavilyClient(api_key=api_key)
    
    # 3. 构造一个精确的查询
    query = f"'{city}' 在'{weather}'天气下最值得去的旅游景点推荐及理由"
    
    try:
        # 4. 调用API，include_answer=True会返回一个综合性的回答
        response = tavily.search(query=query, search_depth="basic", include_answer=True)
        
        # 5. Tavily返回的结果已经非常干净，可以直接使用
        # response['answer'] 是一个基于所有搜索结果的总结性回答
        if response.get("answer"):
            return response["answer"]
        
        # 如果没有综合性回答，则格式化原始结果
        formatted_results = []
        for result in response.get("results", []):
            formatted_results.append(f"- {result['title']}: {result['content']}")
        
        if not formatted_results:
             return "抱歉，没有找到相关的旅游景点推荐。"

        return "根据搜索，为您找到以下信息：\n" + "\n".join(formatted_results)

    except Exception as e:
        return f"错误：执行Tavily搜索时出现问题 - {e}"


# 将所有工具函数放入一个字典，方便后续调用
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
}

class OpenAICompatibleClient:
    """
    调用豆包大模型的客户端
    使用Chat API，端点为：https://ark.cn-beijing.volces.com/api/v3/chat/completions
    """
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.api_key = api_key
        base_url = base_url.rstrip('/')
        self.chat_url = f"{base_url}/chat/completions"

    def generate(self, prompt: str, system_prompt: str) -> str:
        """调用豆包Chat API来生成回应。"""
        print("正在调用豆包大语言模型...")
        logger.info("=" * 60)
        logger.info("开始调用豆包Chat API")
        logger.info(f"API URL: {self.chat_url}")
        logger.info(f"Model/Endpoint ID: {self.model}")
        
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]
            
            # 记录请求内容
            logger.info("请求消息:")
            logger.info(f"  System: {system_prompt[:100]}..." if len(system_prompt) > 100 else f"  System: {system_prompt}")
            logger.info(f"  User: {prompt[:100]}..." if len(prompt) > 100 else f"  User: {prompt}")
            
            # 使用requests直接调用豆包Chat API
            headers = {
                'Authorization': f'Bearer {self.api_key[:20]}...' if len(self.api_key) > 20 else f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 2000
            }
            
            logger.info(f"请求参数: model={self.model}, temperature=0.7, max_tokens=2000")
            logger.info(f"发送POST请求到: {self.chat_url}")
            
            # 调用豆包Chat API：https://ark.cn-beijing.volces.com/api/v3/chat/completions
            response = requests.post(self.chat_url, headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }, json=data)
            
            # 记录响应状态
            logger.info(f"响应状态码: {response.status_code}")
            logger.info(f"响应头: {dict(response.headers)}")
            
            response.raise_for_status()
            
            result = response.json()
            
            # 记录完整响应内容
            logger.info("API响应内容:")
            logger.info(json.dumps(result, ensure_ascii=False, indent=2))
            
            answer = result['choices'][0]['message']['content']
            
            # 记录提取的答案
            logger.info("提取的回复内容:")
            logger.info(f"{answer}")
            logger.info("=" * 60)
            
            print("豆包大语言模型响应成功。")
            return answer
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            logger.error("=" * 60)
            logger.error(f"调用豆包API时发生HTTP错误: {error_msg}")
            logger.error(f"请求URL: {self.chat_url}")
            logger.error(f"请求模型: {self.model}")
            
            error_detail = None
            if e.response is not None:
                logger.error(f"响应状态码: {e.response.status_code}")
                logger.error(f"响应头: {dict(e.response.headers)}")
                try:
                    error_detail = e.response.json()
                    logger.error("错误响应内容:")
                    logger.error(json.dumps(error_detail, ensure_ascii=False, indent=2))
                    print(f"错误详情: {error_detail}")
                except:
                    logger.error(f"响应文本内容: {e.response.text}")
                    print(f"响应内容: {e.response.text}")
            logger.error("=" * 60)
            
            # 根据错误类型提供详细的解决建议
            if e.response and e.response.status_code == 404:
                error_info = ""
                if error_detail and 'error' in error_detail:
                    error_info = error_detail['error'].get('message', '')
                
                return f"""错误：模型或端点不存在（404错误）"""
            elif e.response and e.response.status_code == 401:
                return "错误：API Key无效或未授权，请检查DOUBAO_API_KEY配置。"
            else:
                return f"错误：调用豆包API失败 - {error_msg}"
        except requests.exceptions.RequestException as e:
            logger.error("=" * 60)
            logger.error(f"网络请求异常: {e}")
            logger.error(f"请求URL: {self.chat_url}")
            logger.error(f"请求模型: {self.model}")
            logger.error("=" * 60)
            print(f"调用豆包API时发生网络错误: {e}")
            return f"错误：调用语言模型服务时出错 - {str(e)}"
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"未知错误: {e}", exc_info=True)
            logger.error(f"请求URL: {self.chat_url}")
            logger.error(f"请求模型: {self.model}")
            logger.error("=" * 60)
            print(f"调用豆包API时发生错误: {e}")
            return f"错误：调用语言模型服务时出错 - {str(e)}"

import re
API_KEY = os.environ.get("DOUBAO_API_KEY", "") or os.environ.get("ARK_API_KEY", "")
BASE_URL = os.environ.get("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
MODEL_ID = os.environ.get("DOUBAO_MODEL", "")

if not API_KEY:
    API_KEY = "YOUR_DOUBAO_API_KEY" 

if not MODEL_ID or MODEL_ID == "YOUR_MODEL_ID":
    MODEL_ID = "YOUR_ENDPOINT_ID"  # 请替换为您的端点ID

# Tavily API配置
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
if not TAVILY_API_KEY or TAVILY_API_KEY == "YOUR_TAVILY_API_KEY":
    TAVILY_API_KEY = "YOUR_TAVILY_API_KEY"  # 如果未设置，使用占位符
os.environ['TAVILY_API_KEY'] = TAVILY_API_KEY

print(f"豆包大模型配置:")
print(f"  Model/Endpoint ID: {MODEL_ID}")
print(f"  Chat API URL: {BASE_URL.rstrip('/')}/chat/completions")
print(f"  API Key: {'已设置' if API_KEY and API_KEY != 'YOUR_DOUBAO_API_KEY' else '未设置，请配置'}")
if MODEL_ID.startswith("ep-"):
    print(f"  ✅ 使用端点ID格式（正确）")
elif MODEL_ID == "YOUR_ENDPOINT_ID" or not MODEL_ID:
    print(f"  ❌ 端点ID未配置！")
else:
    print(f"  ⚠️  使用模型名称，如果遇到404错误，请创建端点并使用端点ID")
print()

llm = OpenAICompatibleClient(
    model=MODEL_ID,
    api_key=API_KEY,
    base_url=BASE_URL
)

# --- 2. 初始化 ---
user_prompt = "你好，请帮我查询一下今天伦敦的天气，然后根据天气推荐一个合适的旅游景点。"
prompt_history = [f"用户请求: {user_prompt}"]

print(f"用户输入: {user_prompt}\n" + "="*40)

# --- 3. 运行主循环 ---
for i in range(5): # 设置最大循环次数
    print(f"--- 循环 {i+1} ---\n")
    logger.info("=" * 80)
    logger.info(f"主循环 - 第 {i+1} 轮")
    logger.info("=" * 80)
    
    # 3.1. 构建Prompt
    full_prompt = "\n".join(prompt_history)
    logger.info("当前Prompt历史:")
    logger.info(full_prompt)
    logger.info("-" * 80)
    
    # 3.2. 调用LLM进行思考
    llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)
    
    # 记录原始输出
    logger.info("模型原始输出:")
    logger.info(llm_output)
    
    # 模型可能会输出多余的Thought-Action，需要截断
    match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)', llm_output, re.DOTALL)
    if match:
        truncated = match.group(1).strip()
        if truncated != llm_output.strip():
            llm_output = truncated
            logger.info("已截断多余的 Thought-Action 对")
            logger.info("截断后的输出:")
            logger.info(llm_output)
    
    print(f"模型输出:\n{llm_output}\n")
    logger.info("-" * 80)
    prompt_history.append(llm_output)
    
    # 3.3. 解析并执行行动
    action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
    if not action_match:
        logger.error("解析错误：模型输出中未找到 Action")
        logger.error(f"当前输出内容: {llm_output}")
        print("解析错误：模型输出中未找到 Action。")
        break
    action_str = action_match.group(1).strip()
    logger.info(f"解析到的Action: {action_str}")

    if action_str.startswith("finish"):
        finish_match = re.search(r'finish\(answer="(.*)"\)', action_str)
        if finish_match:
            final_answer = finish_match.group(1)
            logger.info("=" * 80)
            logger.info("任务完成！")
            logger.info(f"最终答案: {final_answer}")
            logger.info("=" * 80)
            print(f"任务完成，最终答案: {final_answer}")
            break
        else:
            logger.warning(f"finish格式不正确: {action_str}")
    
    tool_name = re.search(r"(\w+)\(", action_str).group(1)
    args_str = re.search(r"\((.*)\)", action_str).group(1)
    kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))
    
    logger.info(f"工具名称: {tool_name}")
    logger.info(f"工具参数: {kwargs}")

    if tool_name in available_tools:
        logger.info(f"调用工具: {tool_name}")
        observation = available_tools[tool_name](**kwargs)
        logger.info(f"工具返回结果: {observation}")
    else:
        observation = f"错误：未定义的工具 '{tool_name}'"
        logger.error(observation)

    # 3.4. 记录观察结果
    observation_str = f"Observation: {observation}"
    print(f"{observation_str}\n" + "="*40)
    logger.info(f"观察结果: {observation_str}")
    logger.info("=" * 80)
    logger.info("")  # 空行分隔
    prompt_history.append(observation_str)