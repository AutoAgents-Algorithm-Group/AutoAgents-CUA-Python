from DrissionPage import ChromiumPage
import time

from DrissionPage._functions import elements

def label_interactive_elements(page):
    """
    给页面上所有可交互元素添加编号标签，使用绝对定位的边框容器
    """
    # 注入 JavaScript 来标记元素
    js_code = """
    (function() {
        // 移除旧的高亮容器
        const oldContainer = document.getElementById('eko-highlight-container');
        if (oldContainer) {
            oldContainer.remove();
        }

        // 可交互元素选择器
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

        // 获取所有可交互元素
        const elements = Array.from(document.querySelectorAll(selectors.join(',')))
            .filter(el => {
                // 过滤不可见元素
                const style = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                return style.display !== 'none' && 
                       style.visibility !== 'hidden' && 
                       style.opacity !== '0' &&
                       rect.width > 0 && 
                       rect.height > 0;
            });

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

        // 给每个元素添加高亮和标签
        elements.forEach((el, index) => {
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

                // 创建标签
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

        return elements;
    })();
    """

    # count = page.run_js(js_code)
    # return count
    elements = page.run_js(js_code)
    return elements

def clear_labels(page):
    """清除所有标签和高亮"""
    js_code = """
    (function() {
        // 移除高亮容器（包含所有边框和标签）
        const container = document.getElementById('eko-highlight-container');
        if (container) {
            container.remove();
        }
    })();
    """
    page.run_js(js_code)

# 主程序
p = ChromiumPage()

# 访问 Google
print("🌐 正在打开 Google...")
p.get('https://www.google.com')
time.sleep(2)
print("\n🎯 标记页面上的可交互元素...")
count = label_interactive_elements(p)
print(f"✅ 已标记 内容\n {count} ")
print("\n⏰ 标签将显示 10 秒...")
time.sleep(10)