from ..utils.logging import logger
from collections import defaultdict



class PageExtractor:
    """页面元素提取器 - 高性能批量提取页面可交互元素"""
    
    # 【已废弃】定义可交互元素的标签
    # 注意：此列表已被 test_highlight 中的 CSS 选择器逻辑替代
    # 新逻辑使用更精确的选择器：'a[href]', 'button', 'input:not([type="hidden"])', 等
    INTERACTIVE_TAGS = [
        'a',        # 链接
        'button',   # 按钮
        'input',    # 输入框
        'textarea', # 文本域
        'select',   # 下拉框
        'option',   # 选项
        'div',      # 通用容器（可能通过 role 属性变为可交互）
        'span',     # 内联元素（可能通过 role 属性变为可交互）
    ]
    
    # 常见属性列表
    COMMON_ATTRS = ['id', 'class', 'name', 'type', 'href', 'value', 'placeholder', 'title', 'role', 'aria-label', 'tabindex']
    
    # 属性优先级（用于生成定位器）
    PRIORITY_ATTRS = ['id', 'name', 'type', 'role', 'class', 'aria-label', 'placeholder', 'title', 'href', 'value']
    
    def __init__(self, page):
        """
        初始化页面元素提取器
        
        Args:
            page: DrissionPage 的页面对象
        """
        self.page = page
        self.interactive_elements = []
    
    def generate_selector(self, tag, attrs, text=''):
        """
        生成 DrissionPage 的 ele() 定位字符串
        
        Args:
            tag: 标签名
            attrs: 属性字典
            text: 文本内容
            
        Returns:
            定位字符串
        """
        # 基础选择器：标签名
        selector = f"t:{tag}"
        
        # 添加属性选择器
        used_attrs = []
        for attr in self.PRIORITY_ATTRS:
            if attr in attrs and attrs[attr]:
                used_attrs.append(f"@@{attr}={attrs[attr]}")
        
        selector += ''.join(used_attrs)
        
        # 如果没有任何属性，尝试使用文本
        if not used_attrs and text:
            selector += f"@@text()={text[:20]}"
        
        return selector
    
    
    
    def _extract_elements_fallback(self):
        """
        【已废弃】降级方案：使用传统方法提取元素（优化版）
        
        注意：此方法已被 test_highlight 的逻辑替代，仅作为降级备用方案保留。
        推荐使用 extract_elements() 方法，它使用更高效的 CSS 选择器和可见性过滤。
        
        Returns:
            提取的元素列表
        """
        self.interactive_elements = []
        
        # 优化：使用CSS选择器一次性获取所有可交互元素
        selector = ', '.join(self.INTERACTIVE_TAGS)
        try:
            # 一次性获取所有可交互元素
            all_elements = self.page.eles(f'css:{selector}')
            
            for idx, ele in enumerate(all_elements, start=1):
                # 批量获取属性
                try:
                    tag = ele.tag.lower()
                    text = ele.text[:50] if ele.text else ''
                    
                    # 只获取需要的属性
                    attrs = {}
                    for attr in self.COMMON_ATTRS:
                        try:
                            attr_value = ele.attr(attr)
                            if attr_value:
                                attrs[attr] = attr_value
                        except:
                            continue
                    
                    # 生成定位字符串
                    selector = self.generate_selector(tag, attrs, text)
                    
                    info = {
                        'index': idx,  # 添加索引（从1开始）
                        'tag': tag,
                        'selector': selector,
                        'text': text,
                        'attrs': attrs,
                        'element': ele
                    }
                    self.interactive_elements.append(info)
                except Exception as e:
                    # 跳过有问题的元素
                    continue
            
        except Exception as e:
            logger.error(f"元素提取失败: {e}")
        
        return self.interactive_elements
    
    def print_elements(self, detailed=True):
        """
        打印所有可交互元素
        
        Args:
            detailed: 是否打印详细信息
        """
        logger.info("可交互元素列表（DrissionPage 定位语法）：")
        
        for idx, info in enumerate(self.interactive_elements, 1):
            logger.info(f"[{idx}] 标签: {info['tag']}")
            logger.info(f"  定位语法: {info['selector']}")
            
            if detailed:
                if info['text']:
                    logger.info(f"  文本内容: {info['text']}")
                if info['attrs']:
                    logger.info(f"  属性: {info['attrs']}")
            
            logger.info(f"  使用示例: element = page.ele('{info['selector']}')")
        
        logger.info(f"共找到 {len(self.interactive_elements)} 个可交互元素")
    
    def print_grouped_selectors(self):
        """按类型分组打印定位语法"""
        logger.info("按类型分组的定位语法：")
        
        grouped = defaultdict(list)
        for info in self.interactive_elements:
            grouped[info['tag']].append(info['selector'])
        
        for tag, selectors in grouped.items():
            logger.info(f"{tag.upper()} 元素 ({len(selectors)} 个):")
            for i, sel in enumerate(selectors, 1):
                print(f"  {i}. {sel}")
    
    def get_elements_by_tag(self, tag):
        """
        获取指定标签的所有元素
        
        Args:
            tag: 标签名
            
        Returns:
            该标签的所有元素列表
        """
        return [info for info in self.interactive_elements if info['tag'] == tag]
    
    def get_selector_list(self):
        """
        获取所有定位器列表
        
        Returns:
            所有元素的定位器列表
        """
        return [info['selector'] for info in self.interactive_elements]
    
    def get_elements(self):
        """
        获取所有提取的元素
        
        Returns:
            所有元素的列表
        """
        return self.interactive_elements
    
    def clear(self):
        """清空已提取的元素"""
        self.interactive_elements = []
    
    
    
    def _save_elements_to_txt(self, elements, filename):
        """
        内部方法：将元素列表保存为 txt 文件
        
        Args:
            elements: 元素列表
            filename: 保存的文件名（相对于 playground/outputs 目录）
        """
        import os
        
        try:
            # 获取当前文件所在目录（backend/src/utils）
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建 playground/outputs 目录路径
            output_dir = os.path.join(current_dir, '..', '..', 'playground', 'outputs')
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 构建完整文件路径
            full_path = os.path.join(output_dir, filename)
            
            lines = []
            for element in elements:
                index = element.get('index', '?')
                tag = element['tag']
                attrs = element.get('attrs', {})
                text = element.get('text', '')
                
                # 格式: [index]:<tag attr="value">text</tag>
                attr_str = ""
                if attrs:
                    attr_parts = []
                    for key, value in attrs.items():
                        # 截断过长的属性值
                        if key in ['class'] and len(str(value)) > 50:
                            value = str(value)[:50] + '...'
                        elif key in ['href', 'src'] and len(str(value)) > 100:
                            value = str(value)[:100] + '...'
                        attr_parts.append(f'{key}="{value}"')
                    attr_str = " " + " ".join(attr_parts)
                
                # 构建完整的行
                if text:
                    line = f"[{index}]:<{tag}{attr_str}>{text}</{tag}>"
                else:
                    line = f"[{index}]:<{tag}{attr_str}></{tag}>"
                
                lines.append(line)
            
            # 写入文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            logger.success(f"✅ 已保存 {len(elements)} 个元素到: {full_path}")
        except Exception as e:
            logger.error(f"❌ 保存文件失败: {e}")
    
    
    def save_to_text_file(self, filename="extracted_elements.txt"):
        """
        【已废弃】将提取的元素保存为文本文件
        
        注意：此方法已废弃，请使用 extract_elements(save_to_file="xxx.txt") 或 
             highlight_elements(save_to_file="xxx.txt") 代替
        
        Args:
            filename: 保存的文件名
        """
        logger.warning("⚠️  save_to_text_file() 已废弃，请使用 extract_elements(save_to_file='xxx.txt')")
        self._save_elements_to_txt(self.interactive_elements, filename)
    
    
    
    def _generate_text_content(self):
        """生成简洁的文本内容（专用于喂给大模型）"""
        text_lines = []
        
        # 添加统计信息
        tag_counts = {}
        for element in self.interactive_elements:
            tag = element['tag']
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        text_lines.append(f"总计: {len(self.interactive_elements)} 个可交互元素")
        text_lines.append("统计: " + ", ".join([f"{tag.upper()}: {count}" for tag, count in sorted(tag_counts.items())]))
        text_lines.append("")
        
        # 按类型分组
        grouped = {}
        for element in self.interactive_elements:
            tag = element['tag']
            if tag not in grouped:
                grouped[tag] = []
            grouped[tag].append(element)
        
        for tag, elements in sorted(grouped.items()):
            text_lines.append(f"=== {tag.upper()} 元素 ({len(elements)} 个) ===")
            
            for i, element in enumerate(elements, 1):
                text_lines.append(f"{i}. {element['selector']}")
                
                # 显示所有属性
                if element['attrs']:
                    attrs_str = ", ".join([f"{k}={v}" for k, v in element['attrs'].items()])
                    text_lines.append(f"   属性: {attrs_str}")
                
                text_lines.append("")  # 空行分隔
            
            text_lines.append("")  # 类型间空行
        
        return "\n".join(text_lines)



    def extract_elements(self, highlight=True, save_to_file=None):
            """
            提取所有可交互元素（使用 test_highlight 的优化逻辑）
            
            Args:
                highlight: 是否在页面上高亮显示元素
                save_to_file: 可选，保存提取结果到 txt 文件的路径（例如："elements.txt"）
            
            Returns:
                提取的元素列表，格式为: [{'index': 0, 'tag': 'a', 'attrs': {...}, 'text': '...', ...}, ...]
            """
            
            # 清空已提取元素
            self.clear()
            
            try:
                # 使用 test_highlight 的逻辑：基于 CSS 选择器批量提取
                js_script = """
                // 可交互元素选择器（与 test_highlight 保持一致）
                const selectors = [
                    'a[href]',
                    'button',
                    'input:not([type="hidden"])',
                    'select',
                    'textarea',
                    '[role="button"]',
                    '[onclick]',
                    '[tabindex]'
                ];
                
                // 需要提取的属性列表
                const attrs = ['id', 'class', 'name', 'type', 'href', 'value', 'placeholder', 'title', 'role', 'aria-label', 'tabindex'];
                
                const results = [];
                
                // 获取所有可交互元素
                const elements = Array.from(document.querySelectorAll(selectors.join(',')))
                    .filter(el => {
                        // 过滤不可见元素
                        const style = window.getComputedStyle(el);
                        const rect = el.getBoundingClientRect();
                        return style.display !== 'none' && 
                            style.visibility !== 'hidden' && 
                            rect.width > 0 && 
                            rect.height > 0;
                    });
                
                // 提取每个元素的信息（下标从 1 开始）
                elements.forEach((el, index) => {
                    const displayIndex = index + 1;  // 下标从 1 开始
                    const info = {
                        tag: el.tagName.toLowerCase(),
                        text: el.textContent ? el.textContent.substring(0, 50).trim() : '',
                        attrs: {},
                        index: displayIndex  // 添加索引，用于后续高亮时的 ID 匹配
                    };
                    
                    // 批量获取属性
                    attrs.forEach(attr => {
                        const value = el.getAttribute(attr);
                        if (value) {
                            info.attrs[attr] = value;
                        }
                    });
                    
                    // 给元素打上标记，方便后续高亮时识别（使用显示索引）
                    el.setAttribute('data-extractor-index', displayIndex);
                    
                    results.push(info);
                });
                
                return results;
                """
                
                # 执行JavaScript获取所有元素信息
                elements_data = self.page.run_js(js_script)
                
                # 调试：检查返回值
                if elements_data is None:
                    raise Exception("JavaScript返回None，可能是代码执行失败")
                
                if not isinstance(elements_data, (list, tuple)):
                    raise Exception(f"JavaScript返回类型错误: {type(elements_data)}, 值: {elements_data}")
                
                # 处理返回的数据
                for data in elements_data:
                    tag = data['tag']
                    text = data['text']
                    attrs = data['attrs']
                    index = data.get('index', len(self.interactive_elements))
                    
                    # 生成定位字符串
                    selector = self.generate_selector(tag, attrs, text)
                    
                    # 重新获取元素对象（用于后续操作）
                    try:
                        element = self.page.ele(selector, timeout=0.5)
                    except:
                        element = None
                    
                    info = {
                        'index': index,
                        'tag': tag,
                        'selector': selector,
                        'text': text,
                        'attrs': attrs,
                        'element': element
                    }
                    self.interactive_elements.append(info)
                
                # 如果需要保存到文件
                if save_to_file:
                    self._save_elements_to_txt(self.interactive_elements, save_to_file)
                
                # 如果需要高亮显示
                if highlight:
                    self.highlight_elements()
                
                return self.interactive_elements
                
            except Exception as e:
                # 如果JavaScript方式失败，降级使用原始方法
                logger.warning(f"JavaScript批量提取失败，使用传统方法: {e}")
                result = self._extract_elements_fallback()
                
                # 降级情况下也需要保存文件
                if save_to_file and result:
                    self._save_elements_to_txt(result, save_to_file)
                
                return result

    def highlight_elements(self, save_to_file=None):
        """
        在页面上高亮显示所有可交互元素（使用与提取时相同的索引）
        
        Args:
            save_to_file: 可选，保存高亮元素列表到 txt 文件的路径（例如："highlighted.txt"）
        
        Returns:
            高亮的元素列表，格式同 extract_elements 返回值
        """
        js_code = """
        // 移除旧的高亮容器
        const oldContainer = document.getElementById('eko-highlight-container');
        if (oldContainer) {
            oldContainer.remove();
        }

        // 获取所有已标记的元素（在 extract_elements 时已经打上 data-extractor-index 标记）
        const elements = Array.from(document.querySelectorAll('[data-extractor-index]'))
            .sort((a, b) => {
                // 按索引排序，确保顺序一致
                return parseInt(a.getAttribute('data-extractor-index')) - 
                    parseInt(b.getAttribute('data-extractor-index'));
            });

        if (elements.length === 0) {
            console.warn('没有找到已标记的元素，请先调用 extract_elements()');
            return 0;
        }

        // 颜色池
        const colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788'
        ];

        // 创建高亮容器
        const container = document.createElement('div');
        container.id = 'eko-highlight-container';
        container.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 999999;
        `;
        document.body.appendChild(container);

        // 给每个元素添加高亮和标签（使用元素上的 data-extractor-index）
        elements.forEach(el => {
            const index = parseInt(el.getAttribute('data-extractor-index'));
            const color = colors[index % colors.length];
            const rect = el.getBoundingClientRect();
            
            if (rect.width > 0 && rect.height > 0) {
                const x = rect.left + window.scrollX;
                const y = rect.top + window.scrollY;

                // 创建高亮框
                const highlightBox = document.createElement('div');
                highlightBox.style.cssText = `
                    position: absolute;
                    left: ${x}px;
                    top: ${y}px;
                    width: ${rect.width}px;
                    height: ${rect.height}px;
                    border: 2px solid ${color};
                    box-sizing: border-box;
                    pointer-events: none;
                    border-radius: 4px;
                `;

                // 创建标签（使用 data-extractor-index 作为标签文本）
                const label = document.createElement('div');
                label.textContent = `[${index}]`;
                label.style.cssText = `
                    position: absolute;
                    right: -2px;
                    top: -20px;
                    background: ${color};
                    color: white;
                    padding: 2px 6px;
                    font-size: 12px;
                    font-weight: bold;
                    border-radius: 3px;
                    font-family: monospace;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                `;

                highlightBox.appendChild(label);
                container.appendChild(highlightBox);
            }
        });

        return elements.length;
        """
        
        try:
            count = self.page.run_js(js_code)
            logger.success(f"✅ 已高亮 {count} 个可交互元素")
            
            # 如果需要保存到文件
            if save_to_file:
                self._save_elements_to_txt(self.interactive_elements, save_to_file)
            
            return self.interactive_elements
        except Exception as e:
            logger.error(f"❌ 高亮元素失败: {e}")
            return []
    
    def clear_highlight(self, remove_markers=False):
        """
        清除页面上的所有高亮标记
        
        Args:
            remove_markers: 是否同时移除 data-extractor-index 标记（默认 False，保留标记以便重新高亮）
        """
        js_code = f"""
        // 移除高亮容器（包含所有边框和标签）
        const container = document.getElementById('eko-highlight-container');
        if (container) {{
            container.remove();
        }}
        
        // 可选：移除元素上的标记
        if ({str(remove_markers).lower()}) {{
            document.querySelectorAll('[data-extractor-index]').forEach(el => {{
                el.removeAttribute('data-extractor-index');
            }});
        }}
        """
        
        try:
            self.page.run_js(js_code)
            if remove_markers:
                logger.success("✅ 已清除所有高亮标记和索引标记")
            else:
                logger.success("✅ 已清除所有高亮标记（保留索引标记）")
        except Exception as e:
            logger.error(f"❌ 清除高亮失败: {e}")