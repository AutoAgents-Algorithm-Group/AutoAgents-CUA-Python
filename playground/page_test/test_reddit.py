import time
import sys
sys.path.insert(0, '/Users/forhheart/AIGC/DrrisonPage')

from src.autoagents_web.utils.web_operator import WebOperator
from src.autoagents_web.utils.shadow_dom_parser import ShadowDOMParser
from src.autoagents_web.utils.logging import logger
from src.autoagents_web.models.stage import Stage

# ============= AI 相关代码（已注释） =============
import openai
openai.api_key = "sk-zfCHwb5DjKxuks62DeD39e57F0Fb4bB2Bd00E0A0215480D9"
openai.base_url = "https://api.gpt.ge/v1/"
openai.default_headers = {"x-foo": "true"}

# 使用 WebOperator 创建浏览器实例
log = logger.bind(stage=Stage.SYSTEM)
log.info("初始化 Reddit 测试")

web_op = WebOperator(headless=False)
page = web_op.page  # 获取底层 page 对象以兼容现有代码

# 创建 ShadowDOMParser 实例
shadow_parser = ShadowDOMParser(page)
log.info("ShadowDOM 解析器已创建")


# 调试辅助函数：查找包含特定按钮的 Shadow host
def find_shadow_host_for_button(page, button_name="comments-action-button"):
    """
    查找包含指定按钮的 Shadow host
    
    Args:
        page: DrissionPage 页面对象
        button_name: 按钮的 name 属性值
    """
    js_script = f"""
    // 查找所有可能的自定义元素（潜在的 Shadow host）
    const customElements = document.querySelectorAll('*');
    const results = [];
    
    for (let el of customElements) {{
        // 检查元素是否有 shadowRoot
        if (el.shadowRoot) {{
            // 在 shadowRoot 中查找按钮
            const button = el.shadowRoot.querySelector('button[name="{button_name}"]');
            if (button) {{
                results.push({{
                    tagName: el.tagName.toLowerCase(),
                    id: el.id || null,
                    className: el.className || null,
                    hasButton: true
                }});
            }}
        }}
    }}
    
    return results;
    """
    
    try:
        result = page.run_js(js_script)
        if result and len(result) > 0:
            log.info(f"找到 {len(result)} 个包含按钮的 Shadow host:")
            for item in result:
                log.info(f"  - 标签: {item['tagName']}, ID: {item['id']}, Class: {item['className']}")
        else:
            log.warning(f"未找到包含 button[name='{button_name}'] 的 Shadow host")
            log.info("按钮可能不在 Shadow DOM 中，或者需要检查页面结构")
        return result
    except Exception as e:
        log.error(f"查找 Shadow host 失败: {e}")
        return []


## cookie 登录
cookies=[[
{
    "domain": ".reddit.com",
    "expirationDate": 1781940559.22136,
    "hostOnly": False,
    "httpOnly": False,
    "name": "csv",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": True,
    "session": False,
    "storeId": "0",
    "value": "2",
    "id": 1
},
{
    "domain": ".reddit.com",
    "expirationDate": 1781940559.221381,
    "hostOnly": False,
    "httpOnly": False,
    "name": "edgebucket",
    "path": "/",
    "sameSite": "unspecified",
    "secure": True,
    "session": False,
    "storeId": "0",
    "value": "j6cPiudu7UuMHoDGey",
    "id": 2
},
{
    "domain": ".reddit.com",
    "expirationDate": 1786017637.771346,
    "hostOnly": False,
    "httpOnly": False,
    "name": "loid",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": True,
    "session": False,
    "storeId": "0",
    "value": "00000000009ynq1gv1.2.1611456996000.Z0FBQUFBQm9KdWxyMmRPQWQxUkpHS3U0dEJySlVlZ2ZRYk1VVWlEMlFodmxPc05DT0M5S1BMWnlpdGNfb1pxWFpQY0pKNjNQelhUcU12b3BqWTFaaE9WTWxxa2hJS3diSDczZ2pRLTA5VW95Tk5sb3BReURDVmZNdlJxZThJWk93WnB4ZWtwbGRfN1k",
    "id": 3
},
{
    "domain": ".reddit.com",
    "expirationDate": 1791883187,
    "hostOnly": False,
    "httpOnly": False,
    "name": "pc",
    "path": "/",
    "sameSite": "unspecified",
    "secure": True,
    "session": False,
    "storeId": "0",
    "value": "ng",
    "id": 4
},
{
    "domain": ".reddit.com",
    "expirationDate": 1772435422.712683,
    "hostOnly": False,
    "httpOnly": True,
    "name": "reddit_session",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": True,
    "session": False,
    "storeId": "0",
    "value": "eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpsVFdYNlFVUEloWktaRG1rR0pVd1gvdWNFK01BSjBYRE12RU1kNzVxTXQ4IiwidHlwIjoiSldUIn0.eyJzdWIiOiJ0Ml85eW5xMWd2MSIsImV4cCI6MTc3MjQzNTQyNC41NTQ5NzYsImlhdCI6MTc1Njc5NzAyNC41NTQ5NzYsImp0aSI6Imc4MHBaMk9mcjVCeHdWZ1FzaE1Kc3hTWWRGYWFWQSIsImNpZCI6ImNvb2tpZSIsImxjYSI6MTYxMTQ1Njk5NjAwMCwic2NwIjoiZUp5S2pnVUVBQURfX3dFVkFMayIsInYxIjoiNzgwNzIyNTM2ODYxLDIwMjUtMDctMDJUMTI6MDA6NTksZmRlYzhiZTA4MzEzYzQyNjdjOGRiMzZmODFjNGFjNmFlMTExZjAzMSIsImZsbyI6Mn0.y9iU71n2RDtrQMyArAvsygHBGN3lujErG9H63iVLCNeqzzgdXd6yCgyXfAXjR6uiMW6LBjTyAJ6IXUVJM_Du2G4NdmiApJ2NPheV-4vlaNIAGQT7V8oUpr0ZNTu2NPIE30AAERXZJldpoR10BCo3UFewXtf-y-GPuegOAHGQoDhO2NL8GYtJNNcS2u_ThKwyhrC1mzEWQxkW3AgbapRYUvhycrhn6DK7ouE6vMQYuAmy4CxcVlqO7rkfWrcXEPMONIk9JsmxD-X81vprcNsJrSzB3Xe0OhE_tepcJpF-C4DhMRmq7_W5PDySsk25zCo9hNDbIVr69T7n4gCosU3bOw",
    "id": 5
},
{
    "domain": ".reddit.com",
    "expirationDate": 1760354385.71124,
    "hostOnly": False,
    "httpOnly": False,
    "name": "session_tracker",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": True,
    "session": False,
    "storeId": "0",
    "value": "rifflhlrdhbpgcjbmr.0.1760347184744.Z0FBQUFBQm83TVF6dTFKTHVsMl8wSm9rVlJSR0FvNk1jTzdPNWNkSDJ3SkdGWEwycGdLNFNOSmZBUmlVYUJRR2ZUUnkwTXBuRkx0cVVTZ3Q3bWIwQ0Z6N3VyRTNFOVYyVFZCM0t2SlJZQ3BwcWZSa3N0bEJ3RE04Nm5WZFZsR2wzbDFrNEJqNDJ2aUo",
    "id": 6
},
{
    "domain": "old.reddit.com",
    "expirationDate": 1762932581,
    "hostOnly": True,
    "httpOnly": False,
    "name": "g_state",
    "path": "/",
    "sameSite": "unspecified",
    "secure": False,
    "session": False,
    "storeId": "0",
    "value": "{\"i_l\":0}",
    "id": 7
}
]]


log.info("设置 Cookies")
for cookie in cookies:
    page.set.cookies(cookie) 

log.success("Cookies 设置完成")

## 搜索特定主题
time.sleep(2)
log.info("准备搜索主题")

# 使用 WebOperator 的 navigate 方法
web_op.navigate("https://www.reddit.com/search/?q=tiktok+operation", wait_time=3)


## 点击阅读
time.sleep(3)
log.info("点击帖子标题")

# 使用 WebOperator 的 click_element 方法
web_op.click_element(
    'css:[data-testid="search-sdui-post"]:nth-child(2) [data-testid="post-title"]',
    wait_before=0,
    wait_after=10
)

log.success("已进入帖子详情页")



# 获取帖子内容
log.info("提取帖子内容")
block_text = page.ele('xpath://*[@id="post-title-t3_1o4h4d0"]').texts()
log.info(f"帖子内容: {block_text}")


# ============= AI 生成评论（已注释） =============
post_content = "\n".join(block_text) if isinstance(block_text, list) else str(block_text)
user_prompt = f"""请根据以下 Reddit 帖子内容，为其自动生成一条高质量的英文评论，评论需相关且自然、有真实感，长度 30-50 字：
帖子内容：
{post_content}
"""

completion = openai.chat.completions.create(
    model="gpt-4-all",
    messages=[
        {
            "role": "user",
            "content": user_prompt,
        },
    ],
)
ai_comment = completion.choices[0].message.content
log.info(f"AI生成的评论: {ai_comment}")

# 临时使用固定评论进行测试
# ai_comment = "cool"
# log.info(f"使用测试评论: {ai_comment}")



## 评论
log.info("开始发表评论")

# 先使用调试函数查找正确的 Shadow host
log.info("=" * 60)
log.info("调试：查找评论按钮的 Shadow host")
log.info("=" * 60)
shadow_hosts = find_shadow_host_for_button(page, "comments-action-button")
log.info("=" * 60)

# 根据提供的 HTML 结构，按钮的属性：
# - name="comments-action-button"
# - data-post-click-location="comments-button"
# 
# 可能的 Shadow host 包括：
# - shreddit-post (帖子容器)
# - shreddit-comment-action-row (评论操作行)
# - post-consume-tracker (帖子追踪器)

# 构建要尝试的 Shadow host 配置
shadow_hosts_to_try = []

# 如果找到了 Shadow host，优先使用找到的
if shadow_hosts:
    for host in shadow_hosts:
        tag = host['tagName']
        # 如果有 ID，使用 ID 选择器
        if host['id']:
            shadow_hosts_to_try.append((f'css:{tag}#{host["id"]}', 'css:button[name="comments-action-button"]'))
        # 否则使用标签名
        shadow_hosts_to_try.append((f'css:{tag}', 'css:button[name="comments-action-button"]'))

# 如果没找到，使用预设的常见配置
if not shadow_hosts_to_try:
    log.info("使用预设的 Shadow host 配置")
    shadow_hosts_to_try = [
        ('css:shreddit-post', 'css:button[name="comments-action-button"]'),
        ('css:post-consume-tracker', 'css:button[name="comments-action-button"]'),
        ('css:shreddit-comment-action-row', 'css:button[name="comments-action-button"]'),
    ]

# 尝试使用 ShadowDOM 方式点击
success = False
for host_selector, element_selector in shadow_hosts_to_try:
    log.info(f"尝试 Shadow host: {host_selector}")
    success = shadow_parser.click_element(
        host_selector=host_selector,
        element_selector=element_selector,
        wait_after=3
    )
    if success:
        log.success(f"✓ 成功使用 Shadow host: {host_selector}")
        break
    
log.success("已点击评论按钮")

# 输入评论内容
log.info("输入评论内容")
web_op.input_text('xpath://*[@id="main-content"]/shreddit-async-loader[1]/comment-body-header[1]/shreddit-async-loader[1]/comment-composer-host[1]/faceplate-form[1]/shreddit-composer[1]/div[1]/p[1]', ai_comment, clear=True)
log.success(f"已输入评论: {ai_comment}")

web_op.click_element('xpath://*[@id="main-content"]/shreddit-async-loader[1]/comment-body-header[1]/shreddit-async-loader[1]/comment-composer-host[1]/faceplate-form[1]/shreddit-composer[1]/button[2]/span[1]/span[1]/span[1]/span[1]', wait_before=0, wait_after=3)
time.sleep(3)
log.info("评论操作完成")

# 等待观察结果
time.sleep(10)
log.info("测试结束，关闭浏览器")

# 使用 WebOperator 的 close 方法关闭浏览器
web_op.close()