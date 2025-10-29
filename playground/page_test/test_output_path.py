"""
测试输出路径：验证文件保存到 playground/outputs 目录
"""
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from DrissionPage import ChromiumPage, ChromiumOptions
from src.autoagents_web.utils.page_extractor import PageExtractor


def test_output_path():
    """测试输出路径"""
    
    print("=" * 60)
    print("🚀 测试输出路径")
    print("=" * 60)
    
    options = ChromiumOptions()
    options.auto_port()
    page = ChromiumPage(addr_or_opts=options)
    
    try:
        # 访问 Google
        print("\n🌐 正在打开 Google...")
        page.get('https://www.google.com')
        page.wait(2)
        
        extractor = PageExtractor(page)
        
        # 测试保存功能
        print("\n" + "=" * 60)
        print("📍 测试：extract_elements(save_to_file='test_google.txt')")
        print("=" * 60)
        
        elements = extractor.extract_elements(
            highlight=True, 
            save_to_file="test_google.txt"
        )
        
        print(f"✅ 提取到 {len(elements)} 个元素")
        
        # 验证文件是否在正确的位置
        expected_path = os.path.join(
            os.path.dirname(__file__), 
            'outputs', 
            'test_google.txt'
        )
        
        if os.path.exists(expected_path):
            print(f"\n✅ 文件已正确保存到: {expected_path}")
            with open(expected_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            print(f"✅ 文件包含 {len(lines)} 行")
            print("\n前3行预览:")
            for line in lines[:3]:
                print(f"  {line.strip()}")
        else:
            print(f"\n❌ 文件未找到: {expected_path}")
        
        # 查看 outputs 目录中的所有文件
        outputs_dir = os.path.join(os.path.dirname(__file__), 'outputs')
        if os.path.exists(outputs_dir):
            files = os.listdir(outputs_dir)
            print(f"\n📁 outputs 目录中的文件:")
            for file in files:
                file_path = os.path.join(outputs_dir, file)
                size = os.path.getsize(file_path)
                print(f"  - {file} ({size} bytes)")
        
        input("\n按 Enter 键关闭浏览器...")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 键关闭浏览器...")


if __name__ == "__main__":
    test_output_path()

