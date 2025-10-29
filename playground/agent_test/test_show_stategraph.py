import os
import sys

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagents_web.utils.web_operator import WebOperator
from src.autoagents_web.utils.page_extractor import PageExtractor
from src.autoagents_web.utils.logging import logger

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated
from langgraph.prebuilt import InjectedState

from src.autoagents_web.utils.agent import WebAgent
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    agent = WebAgent(headless=False)
    # 拿到 StateGraph（未编译状态）
    # 打印成 Mermaid 格式文本
    print(agent.graph.draw_mermaid())