# """
# 测试 PageExtractor - 独立使用页面元素提取器
# """
# import os
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# from DrissionPage import WebPage
# from src.utils import PageExtractor, logger


# def main():
#     """测试 PageExtractor 独立使用"""
    
#     # 1. 创建页面对象
#     page = WebPage()
    
#     try:
#         # 2. 加载页面
#         # url = "https://www.baidu.com"  # 示例页面
#         url = "https://www.google.com"
#         logger.info(f"正在加载页面: {url}")
#         page.get(url)
        
#         # 3. 创建 PageExtractor
#         extractor = PageExtractor(page)
        
#         # 4. 提取元素
#         logger.info("开始提取页面元素...")
#         elements = extractor.extract_elements()
#         logger.success(f"✅ 提取完成！共找到 {len(elements)} 个可交互元素")
        
#         # 5. 打印元素信息
#         print("\n" + "="*60)
#         extractor.print_elements(detailed=False)
        
#         # 6. 按类型分组显示
#         print("\n" + "="*60)
#         extractor.print_grouped_selectors()
        
#         # 7. 获取特定类型的元素
#         print("\n" + "="*60)
#         input_elements = extractor.get_elements_by_tag('input')
#         logger.info(f"\n输入框元素 ({len(input_elements)} 个):")
#         for idx, elem in enumerate(input_elements, 1):
#             print(f"  {idx}. {elem['selector']}")
#             if elem['attrs']:
#                 print(f"     属性: {elem['attrs']}")
        
#         # 8. 获取按钮元素
#         button_elements = extractor.get_elements_by_tag('button')
#         logger.info(f"\n按钮元素 ({len(button_elements)} 个):")
#         for idx, elem in enumerate(button_elements, 1):
#             print(f"  {idx}. {elem['selector']}")
#             if elem['text']:
#                 print(f"     文本: {elem['text']}")
        
#         input("\n按回车键关闭浏览器...")
        
#     except Exception as e:
#         logger.error(f"测试失败: {e}")
#         import traceback
#         traceback.print_exc()
#     finally:
#         page.quit()


# if __name__ == '__main__':
#     main()


from DrissionPage import ChromiumPage
from typing import List

def extract_page_elements(url: str) -> List[str]:
    """
    提取网页中的可交互元素和重要元素
    
    Args:
        url: 网页URL
        
    Returns:
        格式化的元素列表，如 [0]:<tag attr="value">text</tag>
    """
    page = ChromiumPage()
    
    try:
        # 访问页面
        page.get(url)
        page.wait.load_start()
        
        # 重要标签选择器
        important_selectors = [
            'body',
            'a',           # 链接
            'button',      # 按钮
            'input',       # 输入框
            'textarea',    # 文本域
            'select',      # 下拉框
            'img',         # 图片
            'div[role]',   # 有role属性的div
            '[aria-label]',# 有aria-label的元素
            '[tabindex]',  # 可聚焦元素
        ]
        
        result = []
        index = 0
        
        for selector in important_selectors:
            elements = page.eles(selector)
            
            for elem in elements:
                try:
                    # 检查元素是否可见
                    if not elem.states.is_displayed:
                        continue
                    
                    tag_name = elem.tag.lower()
                    
                    # 跳过不需要的标签
                    if tag_name in ['script', 'style', 'noscript']:
                        continue
                    
                    # 收集属性
                    attrs = []
                    attr_dict = elem.attrs
                    
                    # 按优先级添加属性
                    priority_attrs = ['id', 'name', 'type', 'role', 'aria-label', 
                                     'aria-expanded', 'tabindex', 'title', 'value', 
                                     'href', 'src', 'alt', 'placeholder']
                    
                    for attr_name in priority_attrs:
                        if attr_name in attr_dict and attr_dict[attr_name]:
                            value = str(attr_dict[attr_name]).strip()
                            if value:
                                attrs.append(f'{attr_name}="{value}"')
                    
                    # 构建属性字符串
                    attr_str = ' ' + ' '.join(attrs) if attrs else ''
                    
                    # 获取元素文本
                    text = elem.text.strip() if elem.text else ''
                    
                    # 限制文本长度
                    if len(text) > 50:
                        text = text[:50] + '...'
                    
                    # 构建元素字符串
                    if text:
                        element_str = f"<{tag_name}{attr_str}>{text}</{tag_name}>"
                    else:
                        element_str = f"<{tag_name}{attr_str}></{tag_name}>"
                    
                    # 添加到结果
                    result.append(f"[{index}]:{element_str}")
                    index += 1
                    
                except Exception:
                    continue
        
        return result
        
    except Exception as e:
        print(f"提取失败: {e}")
        return []
    
    finally:
        page.quit()


# 使用示例
if __name__ == "__main__":
    url = "https://www.google.com"
    elements = extract_page_elements(url)
    
    # 打印所有元素
    for element in elements:
        print(element)
    
    print(f"\n总共提取了 {len(elements)} 个元素")