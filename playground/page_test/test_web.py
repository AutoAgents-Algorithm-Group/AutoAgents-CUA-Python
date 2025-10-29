import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from DrissionPage import WebPage
from src.autoagents_web.utils import PageExtractor, logger
import time


def test_google_page_extraction():
    """测试 Google 页面元素提取"""
    
    # 创建浏览器页面
    page = WebPage()
    
    try:
        # 访问 Google 首页
        logger.info("正在访问 Google 首页...")
        page.get('https://www.google.com')
        
        # 等待页面加载
        time.sleep(3)
        logger.success("✅ Google 页面加载完成")
        
        # 创建页面元素提取器
        extractor = PageExtractor(page)
        
        # 提取所有可交互元素
        logger.info("开始提取页面可交互元素...")
        elements = extractor.extract_elements()
        
        # 保存到 HTML 文件
        logger.info("正在保存元素信息到 HTML 文件...")
        extractor.save_to_html_file("google_elements.html")
        
        # 打印提取结果
        logger.info("=" * 80)
        logger.info("Google 页面可交互元素提取结果")
        logger.info("=" * 80)
        
        # 1. 打印所有元素的详细信息
        extractor.print_elements(detailed=True)
        
        logger.info("\n" + "=" * 80)
        logger.info("按类型分组的元素")
        logger.info("=" * 80)
        
        # 2. 按类型分组打印
        extractor.print_grouped_selectors()
        
        logger.info("\n" + "=" * 80)
        logger.info("统计信息")
        logger.info("=" * 80)
        
        # 3. 统计各类型元素数量
        tag_counts = {}
        for element in elements:
            tag = element['tag']
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        for tag, count in sorted(tag_counts.items()):
            logger.info(f"{tag.upper()}: {count} 个")
        
        logger.info(f"\n总计: {len(elements)} 个可交互元素")
        
        # 4. 展示一些具体的定位语法示例
        logger.info("\n" + "=" * 80)
        logger.info("定位语法使用示例")
        logger.info("=" * 80)
        
        # 获取前5个元素的定位语法作为示例
        selectors = extractor.get_selector_list()[:5]
        for i, selector in enumerate(selectors, 1):
            logger.info(f"示例 {i}: page.ele('{selector}')")
        
        # 5. 按标签类型展示元素
        logger.info("\n" + "=" * 80)
        logger.info("各类型元素详情")
        logger.info("=" * 80)
        
        for tag in ['input', 'button', 'a', 'select']:
            elements_of_tag = extractor.get_elements_by_tag(tag)
            if elements_of_tag:
                logger.info(f"\n{tag.upper()} 元素 ({len(elements_of_tag)} 个):")
                for i, element in enumerate(elements_of_tag[:3], 1):  # 只显示前3个
                    logger.info(f"  {i}. {element['selector']}")
                    if element['text']:
                        logger.info(f"     文本: {element['text']}")
                    if element['attrs']:
                        logger.info(f"     属性: {element['attrs']}")
                if len(elements_of_tag) > 3:
                    logger.info(f"     ... 还有 {len(elements_of_tag) - 3} 个 {tag} 元素")
        
        input("\n按回车键关闭浏览器...")
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        page.quit()
        logger.info("浏览器已关闭")


if __name__ == '__main__':
    test_google_page_extraction()
