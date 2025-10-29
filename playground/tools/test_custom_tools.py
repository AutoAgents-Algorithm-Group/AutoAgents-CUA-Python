"""
自定义工具测试

演示如何选择性使用工具和创建自定义工具组合
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagents_cua.client import ChatClient
from src.autoagents_cua.models import ClientConfig, ModelConfig
from src.autoagents_cua.tools import (
    # 导入单个工具
    open_website,
    extract_page_elements,
    click_element,
    input_text_to_element,
    get_current_url,
    
    # 导入工具集
    BASIC_WEB_TOOLS,
    ALL_WEB_TOOLS,
)
from src.autoagents_cua.agent import BrowserAgent
from src.autoagents_cua.computer import Browser
from src.autoagents_cua.utils import logger


def example1_basic_tools_only():
    """示例1：只使用基础工具"""
    logger.info("=" * 80)
    logger.info("示例1：只使用基础工具")
    logger.info("=" * 80)
    
    llm = ChatClient(
        client_config=ClientConfig(
            base_url="https://api.openai.com/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        model_config=ModelConfig(name="gpt-4o")
    )
    
    browser = Browser(headless=False)
    
    # 只使用基础工具（不包括导航和辅助工具）
    agent = BrowserAgent(browser=browser, llm=llm, tools=BASIC_WEB_TOOLS)
    
    logger.info(f"✅ Agent 创建成功，工具数量: {len(BASIC_WEB_TOOLS)}")
    logger.info(f"可用工具: open_website, extract_page_elements, click_element, input_text_to_element, get_current_url")
    
    return agent


def example2_custom_tool_combination():
    """示例2：自定义工具组合"""
    logger.info("=" * 80)
    logger.info("示例2：自定义工具组合")
    logger.info("=" * 80)
    
    llm = ChatClient(
        client_config=ClientConfig(
            base_url="https://api.openai.com/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        model_config=ModelConfig(name="gpt-4o")
    )
    
    browser = Browser(headless=False)
    
    # 自定义工具组合：只允许打开网站和提取元素
    custom_tools = [
        open_website,
        extract_page_elements,
        get_current_url,
    ]
    
    agent = BrowserAgent(browser=browser, llm=llm, tools=custom_tools)
    
    logger.info(f"✅ Agent 创建成功，工具数量: {len(custom_tools)}")
    logger.info(f"可用工具: open_website, extract_page_elements, get_current_url")
    logger.info("限制: 不能点击或输入，只能浏览和提取信息")
    
    return agent


def example3_minimal_tools():
    """示例3：最小工具集"""
    logger.info("=" * 80)
    logger.info("示例3：最小工具集")
    logger.info("=" * 80)
    
    llm = ChatClient(
        client_config=ClientConfig(
            base_url="https://api.openai.com/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        model_config=ModelConfig(name="gpt-4o")
    )
    
    browser = Browser(headless=False)
    
    # 最小工具集：只能打开网站
    minimal_tools = [open_website]
    
    agent = BrowserAgent(browser=browser, llm=llm, tools=minimal_tools)
    
    logger.info(f"✅ Agent 创建成功，工具数量: {len(minimal_tools)}")
    logger.info(f"可用工具: open_website")
    logger.info("限制: 只能打开网站，不能进行其他操作")
    
    return agent


def example4_read_only_agent():
    """示例4：只读 Agent（只能浏览，不能操作）"""
    logger.info("=" * 80)
    logger.info("示例4：只读 Agent")
    logger.info("=" * 80)
    
    llm = ChatClient(
        client_config=ClientConfig(
            base_url="https://api.openai.com/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        model_config=ModelConfig(name="gpt-4o")
    )
    
    browser = Browser(headless=False)
    
    # 只读工具：只能浏览，不能修改
    readonly_tools = [
        open_website,
        extract_page_elements,
        get_current_url,
    ]
    
    agent = BrowserAgent(browser=browser, llm=llm, tools=readonly_tools)
    
    logger.info(f"✅ 只读 Agent 创建成功，工具数量: {len(readonly_tools)}")
    logger.info("可以: 打开网站、提取元素、获取URL")
    logger.info("不可以: 点击、输入、提交表单")
    
    return agent


def example5_full_featured_agent():
    """示例5：全功能 Agent"""
    logger.info("=" * 80)
    logger.info("示例5：全功能 Agent")
    logger.info("=" * 80)
    
    llm = ChatClient(
        client_config=ClientConfig(
            base_url="https://api.openai.com/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        model_config=ModelConfig(name="gpt-4o")
    )
    
    browser = Browser(headless=False)
    
    # 使用所有工具
    agent = BrowserAgent(browser=browser, llm=llm, tools=ALL_WEB_TOOLS)
    
    logger.info(f"✅ 全功能 Agent 创建成功，工具数量: {len(ALL_WEB_TOOLS)}")
    logger.info("支持所有操作: 导航、提取、点击、输入、截图等")
    
    return agent


def demonstrate_tool_selection():
    """演示工具选择的重要性"""
    logger.info("\n" + "=" * 80)
    logger.info("工具选择建议")
    logger.info("=" * 80)
    
    print("""
工具选择建议：

1. 只读任务（数据抓取、信息提取）
   → 使用: [open_website, extract_page_elements, get_current_url]
   
2. 简单交互（浏览和点击）
   → 使用: BASIC_WEB_TOOLS
   
3. 复杂交互（表单填写、完整流程）
   → 使用: ALL_WEB_TOOLS
   
4. 调试和截图
   → 添加: take_screenshot
   
5. 安全考虑
   → 限制: 不提供可能危险的工具（如 input_text）

示例代码：

# 数据抓取 Agent
browser1 = Browser(headless=True)
readonly_agent = BrowserAgent(
    browser=browser1,
    llm=llm, 
    tools=[open_website, extract_page_elements]
)

# 交互 Agent
browser2 = Browser(headless=False)
interactive_agent = BrowserAgent(
    browser=browser2,
    llm=llm,
    tools=ALL_WEB_TOOLS
)

# 自定义组合
browser3 = Browser(headless=False, window_size={'width': 1000, 'height': 700})
custom_agent = BrowserAgent(
    browser=browser3,
    llm=llm,
    tools=[open_website, click_element, take_screenshot]
)
    """)


def main():
    """主函数"""
    logger.info("🚀 自定义工具测试")
    
    # 显示工具选择建议
    demonstrate_tool_selection()
    
    # 选择要运行的示例
    print("\n请选择示例:")
    print("1. 基础工具 Agent")
    print("2. 自定义工具组合")
    print("3. 最小工具集")
    print("4. 只读 Agent")
    print("5. 全功能 Agent")
    
    choice = input("\n请输入选项 (1-5): ").strip()
    
    try:
        if choice == "1":
            agent = example1_basic_tools_only()
            agent.invoke("打开谷歌")
            
        elif choice == "2":
            agent = example2_custom_tool_combination()
            agent.invoke("打开谷歌并告诉我页面上有什么元素")
            
        elif choice == "3":
            agent = example3_minimal_tools()
            agent.invoke("打开谷歌")
            
        elif choice == "4":
            agent = example4_read_only_agent()
            agent.invoke("打开谷歌并提取页面元素")
            
        elif choice == "5":
            agent = example5_full_featured_agent()
            agent.invoke("打开谷歌")
            
        else:
            logger.error("无效的选项")
            return
        
        input("\n按 Enter 关闭...")
        agent.close()
        
    except Exception as e:
        logger.error(f"发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

