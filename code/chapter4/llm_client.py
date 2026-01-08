import os
import requests
from dotenv import load_dotenv
from typing import List, Dict

# 加载 .env 文件中的环境变量
load_dotenv()

class HelloAgentsLLM:
    """
    为本书 "Hello Agents" 定制的LLM客户端。
    它用于调用任何兼容OpenAI接口的服务，并默认使用流式响应。
    支持豆包大模型API调用。
    """
    def __init__(self, model: str = None, apiKey: str = None, baseUrl: str = None, timeout: int = None):
        """
        初始化客户端。优先使用传入参数，如果未提供，则从环境变量加载。
        
        对于豆包API：
        - baseUrl 应该是：https://ark.cn-beijing.volces.com/api/v3
        - 实际端点会自动拼接为：{baseUrl}/chat/completions
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))
        
        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        # 处理 baseUrl：如果是完整路径，提取基础URL；否则使用原值
        baseUrl = baseUrl.rstrip('/')
        if '/chat/completions' in baseUrl:
            # 如果 baseUrl 已经包含完整路径，提取基础部分
            baseUrl = baseUrl.split('/chat/completions')[0]
        
        self.api_key = apiKey
        self.base_url = baseUrl
        self.timeout = timeout
        # 豆包 Chat API 端点：https://ark.cn-beijing.volces.com/api/v3/chat/completions
        self.chat_url = f"{self.base_url}/chat/completions"

    def think(self, messages: List[Dict[str, str]], temperature: float = 0) -> str:
        """
        调用大语言模型进行思考，并返回其响应。
        使用 requests 直接调用豆包 Chat API，支持流式响应。
        """
        print(f"🧠 正在调用 {self.model} 模型...")
        print(f"📍 API 端点: {self.chat_url}")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': messages,
                'temperature': temperature,
                'stream': True
            }
            
            # 使用 requests 直接调用豆包 Chat API
            response = requests.post(
                self.chat_url,
                headers=headers,
                json=data,
                timeout=self.timeout,
                stream=True
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 处理流式响应
            print("✅ 大语言模型响应成功:")
            collected_content = []
            
            for line in response.iter_lines():
                if not line:
                    continue
                
                # 豆包流式响应格式：data: {"choices":[{"delta":{"content":"..."}}]}
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # 移除 "data: " 前缀
                    
                    if data_str.strip() == '[DONE]':
                        break
                    
                    try:
                        import json
                        chunk_data = json.loads(data_str)
                        if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                            delta = chunk_data['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                print(content, end="", flush=True)
                                collected_content.append(content)
                    except json.JSONDecodeError:
                        continue
            
            print()  # 在流式输出结束后换行
            return "".join(collected_content)

        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            if e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg = f"Error code: {e.response.status_code} - {error_detail}"
                except:
                    error_msg = f"Error code: {e.response.status_code} - {e.response.text}"
            print(f"❌ 调用LLM API时发生HTTP错误: {error_msg}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ 调用LLM API时发生网络错误: {e}")
            return None
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return None

# --- 客户端使用示例 ---
if __name__ == '__main__':
    try:
        llmClient = HelloAgentsLLM()
        
        exampleMessages = [
            {"role": "system", "content": "You are a helpful assistant that writes Python code."},
            {"role": "user", "content": "写一个快速排序算法"}
        ]
        
        print("--- 调用LLM ---")
        responseText = llmClient.think(exampleMessages)
        if responseText:
            print("\n\n--- 完整模型响应 ---")
            print(responseText)

    except ValueError as e:
        print(e)