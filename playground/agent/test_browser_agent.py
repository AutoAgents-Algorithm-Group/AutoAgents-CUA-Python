import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagents_cua.client import ChatClient
from src.autoagents_cua.models import ClientConfig, ModelConfig
from src.autoagents_cua.agent import BrowserAgent
from src.autoagents_cua.browser import Browser


def main():
    llm = ChatClient(
        client_config=ClientConfig(
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
        ),
        model_config=ModelConfig(
            name=os.getenv("OPENAI_MODEL", "gpt-4o"),
            temperature=0.0
        ),
        enable_token_tracking=True
    )
    
    browser = Browser(
        headless=False,  # 显示浏览器窗口
        window_size={'width': 1000, 'height': 700}  # 设置窗口大小
    )

    agent = BrowserAgent(browser=browser, llm=llm)
    result = agent.invoke("请帮我打开谷歌")
        
if __name__ == "__main__":
    main()

