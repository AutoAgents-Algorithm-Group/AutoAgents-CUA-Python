#!/usr/bin/env python3
"""
测试文本保存功能
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from DrissionPage import WebPage
from src.autoagents_web.utils.page_extractor import PageExtractor


def test_text_save():
    """测试文本保存功能"""
    print("🚀 开始测试文本保存功能...")
    
    try:
        # 创建页面对象
        page = WebPage()
        page.get('https://www.google.com')
        
        # 创建提取器
        extractor = PageExtractor(page)
        
        # 提取元素
        print("📋 正在提取可交互元素...")
        elements = extractor.extract_elements()
        print(f"✅ 成功提取 {len(elements)} 个可交互元素")
        
        # 测试文本保存
        print("\n📄 生成文本文件...")
        extractor.save_to_text_file("google_elements.txt")
        
        print("\n✅ 测试完成！")
        print("📁 生成的文件：")
        print("  - google_elements.txt (文本格式，专用于喂给大模型)")
        
        # 显示文本格式特点
        print("\n📊 文本格式特点：")
        print("  - 极简格式，只包含 selector 和 attrs")
        print("  - 按元素类型分组")
        print("  - 无 HTML 标签，纯文本")
        print("  - 适合直接喂给大模型")
        
        # 显示文件大小
        import os
        if os.path.exists("google_elements.txt"):
            size = os.path.getsize("google_elements.txt")
            print(f"  - 文件大小: {size} 字节")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_text_save()