# """
# 测试新的保存逻辑：save_to_file 参数集成到 extract_elements 和 highlight_elements
# """
# import os
# import sys

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# from DrissionPage import ChromiumPage, ChromiumOptions
# from src.utils.page_extractor import PageExtractor


# def test_new_save_logic():
#     """测试新的保存逻辑"""
    
#     print("=" * 60)
#     print("🚀 测试新的保存逻辑")
#     print("=" * 60)
    
#     options = ChromiumOptions()
#     options.auto_port()
#     page = ChromiumPage(addr_or_opts=options)
    
#     try:
#         # 访问 Wikipedia
#         print("\n🌐 正在打开 Wikipedia...")
#         page.get('https://www.google.com/')
#         page.wait(2)
        
#         extractor = PageExtractor(page)
        
#         # ===== 测试 1: extract_elements 带保存 =====
#         print("\n" + "=" * 60)
#         print("📍 测试 1: extract_elements(save_to_file='extracted.txt')")
#         print("=" * 60)
        
#         elements = extractor.extract_elements(
#             highlight=False, 
#             save_to_file="extracted.txt"
#         )
        
#         print(f"✅ 提取到 {len(elements)} 个元素")
#         print(f"✅ 返回值类型: {type(elements)}")
#         print(f"✅ 第一个元素: {elements[0] if elements else 'None'}")
        
#         # 验证文件是否生成
#         if os.path.exists("extracted.txt"):
#             with open("extracted.txt", 'r', encoding='utf-8') as f:
#                 lines = f.readlines()
#             print(f"\n✅ 文件已生成，共 {len(lines)} 行")
#             print("前 3 行:")
#             for line in lines[:3]:
#                 print(f"  {line.strip()}")
#         else:
#             print("\n❌ 文件未生成")
        
#         # ===== 测试 2: extract_elements 不保存 =====
#         print("\n" + "=" * 60)
#         print("📍 测试 2: extract_elements(save_to_file=None)")
#         print("=" * 60)
        
#         elements2 = extractor.extract_elements(highlight=False, save_to_file=None)
#         print(f"✅ 提取到 {len(elements2)} 个元素（不保存文件）")
        
#         # ===== 测试 3: highlight_elements 带保存 =====
#         print("\n" + "=" * 60)
#         print("📍 测试 3: highlight_elements(save_to_file='highlighted.txt')")
#         print("=" * 60)
        
#         highlighted = extractor.highlight_elements(save_to_file="highlighted.txt")
        
#         print(f"✅ 高亮并返回 {len(highlighted)} 个元素")
#         print(f"✅ 返回值类型: {type(highlighted)}")
        
#         # 验证文件是否生成
#         if os.path.exists("highlighted.txt"):
#             with open("highlighted.txt", 'r', encoding='utf-8') as f:
#                 lines = f.readlines()
#             print(f"\n✅ 文件已生成，共 {len(lines)} 行")
#             print("前 3 行:")
#             for line in lines[:3]:
#                 print(f"  {line.strip()}")
#         else:
#             print("\n❌ 文件未生成")
        
#         input("\n按 Enter 键清除高亮...")
#         extractor.clear_highlight()
        
#         # ===== 测试 4: 验证 ID 一致性 =====
#         print("\n" + "=" * 60)
#         print("📍 测试 4: 验证 extracted.txt 和 highlighted.txt 的 ID 一致性")
#         print("=" * 60)
        
#         with open("extracted.txt", 'r', encoding='utf-8') as f:
#             extracted_lines = f.readlines()
        
#         with open("highlighted.txt", 'r', encoding='utf-8') as f:
#             highlighted_lines = f.readlines()
        
#         # 提取 ID
#         extracted_ids = [line.split(':')[0].strip('[]') for line in extracted_lines[:5]]
#         highlighted_ids = [line.split(':')[0].strip('[]') for line in highlighted_lines[:5]]
        
#         print(f"extracted.txt 前5个ID: {extracted_ids}")
#         print(f"highlighted.txt 前5个ID: {highlighted_ids}")
        
#         if extracted_ids == highlighted_ids:
#             print("✅ ID 完全一致！")
#         else:
#             print("❌ ID 不一致！")
        
#         # ===== 测试 5: 测试旧方法（应该显示警告）=====
#         print("\n" + "=" * 60)
#         print("📍 测试 5: 测试废弃的方法（应该显示警告）")
#         print("=" * 60)
        
#         print("\n调用 save_to_text_file():")
#         extractor.save_to_text_file("deprecated_test.txt")
        
#         print("\n调用 save_to_html_file():")
#         extractor.save_to_html_file("deprecated_test.html", brief_mode=True)
        
#         # ===== 测试 6: 验证元素包含 index 字段 =====
#         print("\n" + "=" * 60)
#         print("📍 测试 6: 验证返回的元素包含 index 字段")
#         print("=" * 60)
        
#         for i, element in enumerate(elements[:3]):
#             has_index = 'index' in element
#             index_value = element.get('index', 'N/A')
#             print(f"元素 {i}: has_index={has_index}, index={index_value}, tag={element['tag']}")
        
#         if all('index' in el for el in elements[:10]):
#             print("✅ 所有元素都包含 index 字段")
#         else:
#             print("❌ 部分元素缺少 index 字段")
        
#         print("\n" + "=" * 60)
#         print("✅ 所有测试完成！")
#         print("=" * 60)
        
#         print("\n生成的文件:")
#         print("  - extracted.txt (提取时保存)")
#         print("  - highlighted.txt (高亮时保存)")
#         print("  - deprecated_test.txt (旧方法)")
#         print("  - deprecated_test.html (旧方法)")
        
#         input("\n按 Enter 键关闭浏览器...")
        
#     except Exception as e:
#         print(f"\n❌ 错误: {e}")
#         import traceback
#         traceback.print_exc()
#         input("\n按 Enter 键关闭浏览器...")


# if __name__ == "__main__":
#     test_new_save_logic()

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from DrissionPage import ChromiumPage, ChromiumOptions
from src.autoagents_web.utils.page_extractor import PageExtractor

if __name__ == "__main__":
    options = ChromiumOptions()
    options.auto_port()
    page = ChromiumPage(addr_or_opts=options)

    page.get('https://en.wikipedia.org/')

    page.wait(2)
    extractor = PageExtractor(page)

    # #extractor.extract_elements(save_to_file="google_elements.txt")
    extractor.extract_elements(save_to_file="wiki_elements.txt")
    page.wait(10)
    # extractor.print_elements()

    # extractor.print_grouped_selectors()

    # extractor.get_elements_by_tag('input')

    # extractor.get_selector_list()

    # extractor.get_elements()

    # extractor.clear()

    page.quit()
