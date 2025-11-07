from asyncio import Handle
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagents_cua.client import ChatClient
from src.autoagents_cua.models import ClientConfig, ModelConfig
from src.autoagents_cua.agent import BrowserAgent
from src.autoagents_cua.browser import Browser
from dotenv import load_dotenv
from langchain.messages import HumanMessage
from langchain_openai import ChatOpenAI
from src.autoagents_cua.tools import ALL_WEB_TOOLS
from dotenv import load_dotenv
load_dotenv()

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
    while True:
        instruction = input("请输入指令: ")
        if instruction == "exit":
            break   
        result = agent.invoke({"messages": [HumanMessage(content=instruction)]})
        print(result["todos"])
        # print(f"result:\n {result}")
    agent.close()
        

def test_demo1():
    from langchain.agents import create_agent
    from langchain.agents.middleware import TodoListMiddleware
    from langchain.messages import HumanMessage

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )

    
    agent = create_agent(
        model= llm,
        tools=ALL_WEB_TOOLS,
        middleware=[TodoListMiddleware()],
    )

    result = agent.invoke({"messages": [HumanMessage("Help me refactor my codebase")]})
    print(result["todos"])  # Array of todo items with status tracking

if __name__ == "__main__":
    load_dotenv()
    # main()
    test_demo1()
    

