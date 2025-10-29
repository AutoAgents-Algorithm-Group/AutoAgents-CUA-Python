import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from DrissionPage import WebPage, ChromiumOptions
from src.autoagents_cua.utils.page_extractor import PageExtractor


def test_brief_mode():
    """测试简要输出模式"""
    print("🚀 开始测试简要输出模式...")
    
    try:
        # 创建页面对象
        co = ChromiumOptions()
        page = WebPage(chromium_options=co)
        page.get('https://www.google.com')
        
        # 创建提取器
        extractor = PageExtractor(page)
        
        # 提取元素
        print("📋 正在提取可交互元素...")
        elements = extractor.extract_elements()
        print(f"✅ 成功提取 {len(elements)} 个可交互元素")
        extractor.save_to_html_file("google_elements_full.html", brief_mode=False)
        extractor.save_to_html_file("google_elements_brief.html", brief_mode=True)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_brief_mode()