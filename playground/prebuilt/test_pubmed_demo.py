from time import sleep
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))


from src.autoagents_cua.browser import WebOperator
from src.autoagents_cua.browser import PageExtractor
from src.autoagents_cua.utils.logging import logger


class PubMedCrawler:
    """PubMed Central 爬虫"""
    
    def __init__(self, headless=False):
        """
        初始化爬虫
        
        Args:
            headless: 是否使用无头模式
        """
        self.operator = WebOperator(headless=headless)
        self.extractor = PageExtractor(self.operator.page)
        self.results = []
    
    def search(self, query):
        """
        在 PubMed Central 搜索
        
        Args:
            query: 搜索关键词
            
        Returns:
            bool: 是否成功
        """
        try:
            # 1. 打开 PubMed Central
            logger.info("=" * 60)
            logger.info("步骤 1: 打开 PubMed Central 网站")
            logger.info("=" * 60)
            
            success = self.operator.navigate("https://pmc.ncbi.nlm.nih.gov/", wait_time=3)
            if not success:
                logger.error("打开网站失败")
                return False
            
            # 2. 等待页面加载并提取元素
            sleep(2)
            logger.info("\n正在分析页面元素...")
            elements = self.extractor.extract_elements(highlight=True, save_to_file="pubmed_homepage.txt")
            logger.info(f"找到 {len(elements)} 个可交互元素")
            
            # 3. 查找搜索框
            logger.info("\n" + "=" * 60)
            logger.info("步骤 2: 输入搜索关键词")
            logger.info("=" * 60)
            
            # PMC 搜索框的定位器（根据页面分析）
            search_selectors = [
                'css:#pmc-search',  # PMC 主搜索框 ID
                'css:input[name="term"]',  # 搜索框 name
                'css:input[placeholder*="Search PMC"]',  # placeholder 包含 Search PMC
                'css:input[type="search"]',  # 搜索框 type
            ]
            
            search_box = None
            for selector in search_selectors:
                search_box = self.operator.input_text(selector, query, clear=True)
                if search_box:
                    logger.success(f"✅ 找到搜索框: {selector}")
                    break
            
            if not search_box:
                logger.error("❌ 未找到搜索框")
                return False
            
            logger.success(f"✅ 已输入搜索关键词: {query}")
            sleep(1)
            
            # 4. 点击搜索按钮或按回车
            logger.info("\n提交搜索...")
            
            # 记录当前URL，用于判断页面是否跳转
            current_url = self.operator.page.url
            search_submitted = False
            
            # 方法1: 尝试在输入框中按回车（模拟输入 Enter 键）
            if search_box:
                try:
                    logger.info("尝试在输入框中按回车...")
                    search_box.input('\n')  # 输入换行符触发提交
                    
                    # 等待页面跳转（最多等待5秒）
                    for i in range(10):
                        sleep(0.5)
                        if self.operator.page.url != current_url:
                            logger.success("✅ 页面已跳转到搜索结果页")
                            search_submitted = True
                            break
                except Exception as e:
                    logger.warning(f"输入回车失败: {e}")
            
            # 方法2: 尝试点击"Search in PMC"按钮（最可靠的方法）
            if not search_submitted:
                try:
                    logger.info("尝试点击 'Search in PMC' 按钮...")
                    # 根据按钮文本查找
                    submit_button = self.operator.page.ele('css:button[type="submit"]', timeout=2)
                    if submit_button and 'Search in PMC' in submit_button.text:
                        submit_button.click()
                        logger.info("已点击 'Search in PMC' 按钮")
                        
                        # 等待页面跳转
                        for i in range(10):
                            sleep(0.5)
                            new_url = self.operator.page.url
                            # 确保跳转到 PMC 搜索结果页
                            if new_url != current_url and 'pmc.ncbi.nlm.nih.gov' in new_url:
                                logger.success("✅ 页面已跳转到 PMC 搜索结果页")
                                search_submitted = True
                                break
                except Exception as e:
                    logger.warning(f"点击按钮失败: {e}")
            
            # 方法3: 尝试使用JavaScript提交表单
            if not search_submitted:
                try:
                    logger.info("尝试使用JavaScript提交表单...")
                    # 查找 PMC 搜索表单并提交
                    self.operator.page.run_js("""
                        let searchInput = document.querySelector('#pmc-search') || 
                                         document.querySelector('input[name="term"]');
                        if (searchInput && searchInput.form) {
                            searchInput.form.submit();
                        }
                    """)
                    
                    # 等待页面跳转
                    for i in range(10):
                        sleep(0.5)
                        new_url = self.operator.page.url
                        if new_url != current_url and 'pmc.ncbi.nlm.nih.gov' in new_url:
                            logger.success("✅ 页面已跳转到 PMC 搜索结果页")
                            search_submitted = True
                            break
                except Exception as e:
                    logger.warning(f"JavaScript提交失败: {e}")
            
            # 方法4: 最后的备用方案 - 直接构造 PMC 搜索URL
            if not search_submitted:
                logger.info("尝试直接构造 PMC 搜索URL...")
                import urllib.parse
                # PMC 的正确搜索URL格式
                search_url = f"https://pmc.ncbi.nlm.nih.gov/?term={urllib.parse.quote(query)}"
                if self.operator.navigate(search_url, wait_time=3):
                    new_url = self.operator.page.url
                    if 'pmc.ncbi.nlm.nih.gov' in new_url:
                        search_submitted = True
                        logger.success("✅ 已通过URL导航到 PMC 搜索结果页")
            
            if not search_submitted:
                logger.error("❌ 搜索提交失败")
                return False
            
            # 5. 等待搜索结果加载
            sleep(3)
            logger.success("✅ 搜索结果已加载")
            
            # 保存搜索结果页面元素
            self.extractor.extract_elements(highlight=True, save_to_file="pubmed_search_results.txt")
            
            return True
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def extract_article_info(self, article_index):
        """
        提取文章信息（标题、作者、摘要）
        
        Args:
            article_index: 文章序号（用于日志）
            
        Returns:
            dict: 文章信息字典
        """
        try:
            logger.info("\n" + "=" * 60)
            logger.info(f"提取文章 #{article_index} 的信息")
            logger.info("=" * 60)
            
            sleep(2)  # 等待页面完全加载
            
            article_info = {
                'index': article_index,
                'title': None,
                'authors': None,
                'abstract': None
            }
            
            # 1. 提取标题
            logger.info("\n📖 提取标题...")
            title_selectors = [
                'css:h1.content-title',
                'css:.article-title',
                'css:h1[class*="title"]',
                'css:.title-content',
                'tag:h1',
            ]
            
            for selector in title_selectors:
                title = self.operator.get_element_text(selector)
                if title and len(title) > 10:  # 标题通常较长
                    article_info['title'] = title.strip()
                    logger.success(f"✅ 标题: {article_info['title'][:100]}...")
                    break
            
            if not article_info['title']:
                logger.warning("⚠️  未找到标题")
            
            # 2. 提取作者
            logger.info("\n👥 提取作者...")
            author_selectors = [
                'css:.authors',
                'css:.article-authors',
                'css:.contrib-group',
                'css:[class*="author"]',
                'css:.fm-author',
            ]
            
            for selector in author_selectors:
                authors = self.operator.get_element_text(selector)
                if authors and len(authors) > 3:
                    article_info['authors'] = authors.strip()
                    logger.success(f"✅ 作者: {article_info['authors'][:150]}...")
                    break
            
            if not article_info['authors']:
                logger.warning("⚠️  未找到作者信息")
            
            # 3. 提取摘要
            logger.info("\n📄 提取摘要...")
            abstract_selectors = [
                'css:#abstract',
                'css:.abstract',
                'css:[class*="abstract"]',
                'css:.article-abstract',
                'css:#Abs1',
            ]
            
            for selector in abstract_selectors:
                abstract = self.operator.get_element_text(selector)
                if abstract and len(abstract) > 50:  # 摘要通常较长
                    article_info['abstract'] = abstract.strip()
                    logger.success(f"✅ 摘要: {article_info['abstract'][:200]}...")
                    break
            
            if not article_info['abstract']:
                logger.warning("⚠️  未找到摘要")
            
            # 保存文章页面元素
            self.extractor.extract_elements(
                highlight=True, 
                save_to_file=f"pubmed_article_{article_index}.txt"
            )
            
            return article_info
            
        except Exception as e:
            logger.error(f"提取文章信息失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def crawl_search_results(self, max_results=2):
        """
        爬取搜索结果
        
        Args:
            max_results: 最多爬取几篇文章
            
        Returns:
            list: 文章信息列表
        """
        try:
            for i in range(1, max_results + 1):
                logger.info("\n" + "=" * 60)
                logger.info(f"步骤 {2 + i}: 处理第 {i} 个搜索结果")
                logger.info("=" * 60)
                
                # 记录当前URL，用于判断是否成功跳转
                search_page_url = self.operator.page.url
                
                # 1. 查找并点击第 i 个搜索结果
                logger.info(f"\n🔍 查找第 {i} 个搜索结果...")
                
                # 先等待页面完全加载
                sleep(2)
                
                # PubMed 搜索结果通常在一个列表中
                result_selectors = [
                    f'css:.search-results article:nth-of-type({i}) a',
                    f'css:.results-list .result-item:nth-of-type({i}) a',
                    f'css:.search-result:nth-of-type({i}) a.article-title',
                    f'css:.rslt:nth-of-type({i}) a',
                    f'css:article:nth-of-type({i}) .title a',
                    f'css:.docsum-title:nth-of-type({i})',
                ]
                
                clicked = False
                article_url = None
                
                for selector in result_selectors:
                    try:
                        element = self.operator.page.ele(selector, timeout=2)
                        if element:
                            # 先获取链接URL（如果有的话）
                            if element.tag == 'a':
                                article_url = element.attr('href')
                            
                            # 点击元素
                            element.click()
                            logger.info(f"已点击元素: {selector}")
                            
                            # 等待页面跳转
                            for j in range(10):
                                sleep(0.5)
                                current_url = self.operator.page.url
                                if current_url != search_page_url:
                                    logger.success(f"✅ 已跳转到第 {i} 个文章页面")
                                    clicked = True
                                    break
                            
                            if clicked:
                                break
                    except Exception as e:
                        continue
                
                # 备用方案：如果点击失败，尝试直接导航
                if not clicked and article_url:
                    logger.info(f"尝试直接导航到文章页面: {article_url}")
                    if not article_url.startswith('http'):
                        # 相对链接，需要补全
                        base_url = "https://pmc.ncbi.nlm.nih.gov"
                        article_url = base_url + article_url
                    
                    if self.operator.navigate(article_url, wait_time=3):
                        clicked = True
                        logger.success(f"✅ 已导航到第 {i} 个文章页面")
                
                if not clicked:
                    logger.warning(f"⚠️  未找到第 {i} 个搜索结果，尝试提取所有文章链接...")
                    
                    # 最后备用方案：提取所有文章链接
                    try:
                        # 使用DrissionPage直接查找所有链接
                        all_links = self.operator.page.eles('tag:a', timeout=2)
                        
                        # 过滤出真正的文章链接
                        article_links = []
                        skip_keywords = ['skip', 'menu', 'footer', 'header', 'login', 
                                       'accessibility', 'journal', 'about', 'guide']
                        
                        for link in all_links:
                            try:
                                href = link.attr('href') or ''
                                text = link.text.strip() if link.text else ''
                                
                                # 跳过空链接、导航链接等
                                if not text or len(text) < 20:
                                    continue
                                if any(kw in text.lower() for kw in skip_keywords):
                                    continue
                                if not href or href.startswith('#'):
                                    continue
                                    
                                # 可能的文章链接（包含文章路径或看起来像标题）
                                if '/articles/' in href or len(text) > 30:
                                    article_links.append((link, text, href))
                            except:
                                continue
                        
                        logger.info(f"找到 {len(article_links)} 个可能的文章链接")
                        
                        if i <= len(article_links):
                            link_elem, link_text, link_href = article_links[i - 1]
                            logger.info(f"尝试点击第 {i} 个文章: {link_text[:60]}...")
                            logger.info(f"链接: {link_href[:80]}...")
                            
                            # 点击链接
                            try:
                                link_elem.click()
                                
                                # 等待页面跳转
                                for j in range(10):
                                    sleep(0.5)
                                    current_url = self.operator.page.url
                                    if current_url != search_page_url:
                                        logger.success(f"✅ 已跳转到文章页面")
                                        clicked = True
                                        break
                                
                                if not clicked:
                                    logger.warning("点击后页面未跳转")
                            except Exception as e:
                                logger.error(f"点击文章链接失败: {e}")
                        else:
                            logger.error(f"找到的文章链接不足 {i} 个")
                    except Exception as e:
                        logger.error(f"提取文章链接失败: {e}")
                
                if not clicked:
                    logger.error(f"❌ 无法点击第 {i} 个搜索结果")
                    continue
                
                # 2. 提取文章信息
                article_info = self.extract_article_info(i)
                
                if article_info:
                    self.results.append(article_info)
                    logger.success(f"\n✅ 第 {i} 篇文章信息已提取")
                
                # 3. 返回搜索结果页（如果不是最后一个）
                if i < max_results:
                    logger.info(f"\n⬅️  返回搜索结果页...")
                    
                    # 记录当前URL
                    article_page_url = self.operator.page.url
                    
                    # 返回上一页
                    self.operator.page.back()
                    
                    # 等待页面返回到搜索结果页
                    for j in range(10):
                        sleep(0.5)
                        current_url = self.operator.page.url
                        if current_url != article_page_url and current_url == search_page_url:
                            logger.success("✅ 已返回搜索结果页")
                            break
                    
                    # 额外等待页面完全加载
                    sleep(2)
            
            return self.results
            
        except Exception as e:
            logger.error(f"爬取搜索结果失败: {e}")
            import traceback
            traceback.print_exc()
            return self.results
    
    def save_results(self, filename="pubmed_results.txt"):
        """
        保存爬取结果
        
        Args:
            filename: 保存文件名
        """
        try:
            # 获取输出目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(current_dir, 'outputs')
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("PubMed Central 爬取结果\n")
                f.write("搜索关键词: characterization of solid superlubrication\n")
                f.write("=" * 80 + "\n\n")
                
                for article in self.results:
                    f.write(f"\n{'=' * 80}\n")
                    f.write(f"文章 #{article['index']}\n")
                    f.write(f"{'=' * 80}\n\n")
                    
                    f.write(f"📖 标题:\n{article['title']}\n\n")
                    f.write(f"👥 作者:\n{article['authors']}\n\n")
                    f.write(f"📄 摘要:\n{article['abstract']}\n\n")
            
            logger.success(f"✅ 结果已保存到: {output_path}")
            
        except Exception as e:
            logger.error(f"保存结果失败: {e}")
    
    def close(self):
        """关闭浏览器"""
        self.operator.close()


def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("🚀 PubMed Central 论文爬取任务开始")
    logger.info("=" * 80)
    
    # 创建爬虫实例（不使用无头模式，方便观察）
    crawler = PubMedCrawler(headless=False)
    
    try:
        # 1. 搜索
        search_query = "characterization of solid superlubrication"
        success = crawler.search(search_query)
        
        if not success:
            logger.error("❌ 搜索失败，任务终止")
            return
        
        # 2. 爬取前两个搜索结果
        results = crawler.crawl_search_results(max_results=2)
        
        # 3. 显示结果
        logger.info("\n" + "=" * 80)
        logger.info("📊 爬取结果汇总")
        logger.info("=" * 80)
        
        for article in results:
            logger.info(f"\n文章 #{article['index']}:")
            logger.info(f"  标题: {article['title'][:80] if article['title'] else 'N/A'}...")
            logger.info(f"  作者: {article['authors'][:80] if article['authors'] else 'N/A'}...")
            logger.info(f"  摘要: {article['abstract'][:80] if article['abstract'] else 'N/A'}...")
        
        # 4. 保存结果
        crawler.save_results()
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ 任务完成！")
        logger.info("=" * 80)
        
        input("\n按 Enter 键关闭浏览器...")
        
    except Exception as e:
        logger.error(f"任务执行失败: {e}")
        import traceback
        traceback.print_exc()
        
        input("\n按 Enter 键关闭浏览器...")
    
    finally:
        crawler.close()


if __name__ == "__main__":
    main()


