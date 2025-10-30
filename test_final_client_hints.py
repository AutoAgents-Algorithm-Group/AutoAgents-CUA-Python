#!/usr/bin/env python3
"""
Client Hints 最终修复测试 - 使用底层方法
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.autoagents_cua.utils import logger
from src.autoagents_cua.browser import BrowserFingerprint
from DrissionPage import WebPage, ChromiumOptions
import json
import tempfile


def create_enhanced_browser():
    """创建增强的浏览器实例，专门针对Client Hints"""
    
    logger.info("🔧 创建增强的浏览器实例...")
    
    # 获取指纹配置
    fingerprint = BrowserFingerprint.get_preset('windows_chrome')
    client_hints = fingerprint.get('client_hints', {})
    user_agent = fingerprint.get('user_agent', '')
    
    logger.info("📋 目标 Client Hints 配置:")
    for key, value in client_hints.items():
        logger.info(f"  {key}: {value}")
    
    # 创建ChromiumOptions（简化配置，确保稳定启动）
    co = ChromiumOptions()
    co.headless(False)
    
    # 基本稳定性参数
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-dev-shm-usage')
    co.set_argument('--disable-gpu')
    co.set_argument('--disable-blink-features=AutomationControlled')
    co.set_argument('--no-first-run')
    co.set_argument('--no-default-browser-check')
    
    # 方法1: 设置User-Agent
    co.set_user_agent(user_agent)
    
    # 方法2: 设置关键的Client Hints参数（精简版）
    try:
        # 只设置最关键的参数，避免启动失败
        co.set_argument('--enable-features=UserAgentClientHint')
        co.set_argument('--disable-features=UserAgentReduction')
        
        logger.info("✅ 设置了关键的Client Hints启动参数")
        
    except Exception as e:
        logger.warning(f"设置启动参数失败: {e}")
    
    # 自动端口配置避免冲突
    co.auto_port()
    
    # 方法3: 创建临时用户数据目录（简化版）
    temp_dir = None
    try:
        # 创建临时用户数据目录
        temp_dir = tempfile.mkdtemp(prefix='chrome_test_')
        co.set_user_data_path(temp_dir)
        logger.info(f"✅ 设置临时用户数据目录: {temp_dir}")
        
    except Exception as e:
        logger.warning(f"设置用户数据目录失败: {e}")
        temp_dir = None
    
    # 创建WebPage实例（添加重试机制）
    logger.info("🚀 启动浏览器...")
    page = None
    
    for attempt in range(3):
        try:
            page = WebPage(chromium_options=co)
            logger.success(f"✅ 浏览器启动成功 (尝试 {attempt+1})")
            break
        except Exception as e:
            logger.warning(f"⚠️  浏览器启动失败 (尝试 {attempt+1}): {e}")
            if attempt < 2:
                import time
                time.sleep(2)
                # 尝试不同的端口
                co.auto_port()
            else:
                raise Exception(f"浏览器启动失败，已尝试3次: {e}")
    
    return page, temp_dir


def test_enhanced_client_hints():
    """测试增强的Client Hints修复"""
    
    logger.info("🎯 Client Hints 最终修复测试")
    logger.info("=" * 60)
    
    # 创建增强的浏览器
    page, temp_dir = create_enhanced_browser()
    
    try:
        # 等待浏览器完全启动
        import time
        time.sleep(3)
        
        # 应用CDP级别的修复
        logger.info("🔧 应用CDP级别的修复...")
        
        fingerprint = BrowserFingerprint.get_preset('windows_chrome')
        client_hints = fingerprint.get('client_hints', {})
        user_agent = fingerprint.get('user_agent', '')
        
        # 启用CDP domains
        page.run_cdp('Network.enable')
        page.run_cdp('Runtime.enable')
        page.run_cdp('Page.enable')
        
        # 构建userAgentMetadata
        user_agent_metadata = {
            'brands': [],
            'mobile': client_hints.get('Sec-CH-UA-Mobile') == '?1',
            'platform': client_hints.get('Sec-CH-UA-Platform', '').replace('"', ''),
            'platformVersion': client_hints.get('Sec-CH-UA-Platform-Version', '').replace('"', ''),
            'architecture': client_hints.get('Sec-CH-UA-Arch', '').replace('"', ''),
            'bitness': client_hints.get('Sec-CH-UA-Bitness', '').replace('"', ''),
            'model': client_hints.get('Sec-CH-UA-Model', '').replace('"', ''),
            'fullVersion': client_hints.get('Sec-CH-UA-Full-Version', '').replace('"', '')
        }
        
        # 解析品牌信息
        if 'Sec-CH-UA' in client_hints:
            brands_string = client_hints['Sec-CH-UA']
            import re
            brand_matches = re.findall(r'"([^"]+)";v="([^"]+)"', brands_string)
            for brand, version in brand_matches:
                user_agent_metadata['brands'].append({
                    'brand': brand,
                    'version': version
                })
        
        # 强制设置User-Agent Override
        override_params = {
            'userAgent': user_agent,
            'userAgentMetadata': user_agent_metadata
        }
        
        # 多次尝试设置
        for method in ['Network.setUserAgentOverride', 'Emulation.setUserAgentOverride']:
            for attempt in range(5):
                try:
                    result = page.run_cdp(method, override_params)
                    logger.success(f"✅ {method} 设置成功 (尝试 {attempt+1})")
                    break
                except Exception as e:
                    logger.warning(f"⚠️  {method} 尝试 {attempt+1} 失败: {e}")
                    time.sleep(0.5)
        
        # 立即执行JavaScript覆盖
        immediate_script = f"""
        (function() {{
            const clientHintsData = {json.dumps(client_hints)};
            console.log('🔧 立即执行JavaScript覆盖:', clientHintsData);
            
            if (typeof navigator !== 'undefined') {{
                const brands = [];
                if (clientHintsData['Sec-CH-UA']) {{
                    const brandString = clientHintsData['Sec-CH-UA'];
                    const brandMatches = brandString.match(/"([^"]+)";v="([^"]+)"/g);
                    if (brandMatches) {{
                        for (const match of brandMatches) {{
                            const [, brand, version] = match.match(/"([^"]+)";v="([^"]+)"/);
                            brands.push({{ brand, version }});
                        }}
                    }}
                }}
                
                const newUserAgentData = {{
                    brands: brands,
                    mobile: clientHintsData['Sec-CH-UA-Mobile'] === '?1',
                    platform: clientHintsData['Sec-CH-UA-Platform'] ? clientHintsData['Sec-CH-UA-Platform'].replace(/"/g, '') : 'Windows',
                    getHighEntropyValues: function(hints) {{
                        return Promise.resolve({{
                            brands: this.brands,
                            mobile: this.mobile,
                            platform: this.platform,
                            architecture: clientHintsData['Sec-CH-UA-Arch'] ? clientHintsData['Sec-CH-UA-Arch'].replace(/"/g, '') : 'x86',
                            bitness: clientHintsData['Sec-CH-UA-Bitness'] ? clientHintsData['Sec-CH-UA-Bitness'].replace(/"/g, '') : '64',
                            model: clientHintsData['Sec-CH-UA-Model'] ? clientHintsData['Sec-CH-UA-Model'].replace(/"/g, '') : '',
                            platformVersion: clientHintsData['Sec-CH-UA-Platform-Version'] ? clientHintsData['Sec-CH-UA-Platform-Version'].replace(/"/g, '') : '',
                            uaFullVersion: clientHintsData['Sec-CH-UA-Full-Version'] ? clientHintsData['Sec-CH-UA-Full-Version'].replace(/"/g, '') : ''
                        }});
                    }}
                }};
                
                // 强制替换
                try {{
                    delete navigator.userAgentData;
                    Object.defineProperty(navigator, 'userAgentData', {{
                        value: newUserAgentData,
                        writable: false,
                        configurable: false,
                        enumerable: true
                    }});
                    console.log('✅ 立即JavaScript覆盖成功');
                }} catch (e) {{
                    console.warn('立即JavaScript覆盖失败:', e);
                }}
            }}
            
            return navigator.userAgentData;
        }})();
        """
        
        js_result = page.run_js(immediate_script)
        logger.info(f"JavaScript执行结果: {js_result}")
        
        # 注册页面加载脚本
        page.run_cdp('Page.addScriptToEvaluateOnNewDocument', {
            'source': immediate_script,
            'worldName': 'final_client_hints'
        })
        
        # 创建测试页面
        test_html = """<!DOCTYPE html>
<html>
<head>
    <title>Final Client Hints Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .success { color: #28a745; font-weight: bold; }
        .error { color: #dc3545; font-weight: bold; }
        .info { background: #e9ecef; padding: 10px; border-radius: 4px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>🎯 Final Client Hints Test</h1>
    
    <div id="result"></div>
    
    <button onclick="testHttpHeaders()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; margin: 10px 0;">测试HTTP请求头</button>
    <div id="httpResult"></div>
    
    <script>
        console.log('🔍 页面脚本开始执行...');
        
        function checkClientHints() {
            const resultDiv = document.getElementById('result');
            let html = '<h3>检查结果:</h3>';
            
            // 基本信息
            html += '<div class="info">';
            html += '<strong>User-Agent:</strong> ' + navigator.userAgent + '<br>';
            html += '<strong>Platform:</strong> ' + navigator.platform + '<br>';
            html += '</div>';
            
            // Client Hints检查
            if (navigator.userAgentData) {
                html += '<div class="success">✅ navigator.userAgentData 可用</div>';
                html += '<div class="info">';
                html += '<strong>brands:</strong> ' + JSON.stringify(navigator.userAgentData.brands) + '<br>';
                html += '<strong>mobile:</strong> ' + navigator.userAgentData.mobile + '<br>';
                html += '<strong>platform:</strong> ' + navigator.userAgentData.platform + '<br>';
                html += '</div>';
                
                // 获取高熵值
                navigator.userAgentData.getHighEntropyValues(['architecture', 'bitness', 'model', 'platformVersion', 'uaFullVersion'])
                    .then(data => {
                        html += '<h4>高熵值数据:</h4>';
                        html += '<div class="info">' + JSON.stringify(data, null, 2) + '</div>';
                        resultDiv.innerHTML = html;
                    })
                    .catch(err => {
                        html += '<div class="error">获取高熵值失败: ' + err.message + '</div>';
                        resultDiv.innerHTML = html;
                    });
            } else {
                html += '<div class="error">❌ navigator.userAgentData 不可用</div>';
            }
            
            resultDiv.innerHTML = html;
        }
        
        function testHttpHeaders() {
            const resultDiv = document.getElementById('httpResult');
            resultDiv.innerHTML = '<div>🔄 测试HTTP请求头...</div>';
            
            fetch('https://httpbin.org/headers')
                .then(response => response.json())
                .then(data => {
                    let html = '<h4>📡 HTTP请求头结果:</h4>';
                    html += '<div class="info">';
                    
                    const headers = data.headers;
                    let foundClientHints = false;
                    
                    // 检查Client Hints头部
                    ['Sec-Ch-Ua', 'Sec-CH-UA', 'Sec-Ch-Ua-Mobile', 'Sec-CH-UA-Mobile', 'Sec-Ch-Ua-Platform', 'Sec-CH-UA-Platform'].forEach(header => {
                        if (headers[header]) {
                            html += '<span class="success">' + header + '</span>: ' + headers[header] + '<br>';
                            foundClientHints = true;
                        }
                    });
                    
                    if (!foundClientHints) {
                        html += '<div class="error">❌ 未找到Client Hints头部</div>';
                    }
                    
                    html += '<br><strong>User-Agent:</strong> ' + (headers['User-Agent'] || 'N/A');
                    html += '</div>';
                    
                    resultDiv.innerHTML = html;
                })
                .catch(error => {
                    resultDiv.innerHTML = '<div class="error">❌ 请求失败: ' + error.message + '</div>';
                });
        }
        
        // 页面加载时执行检查
        window.addEventListener('load', checkClientHints);
        
        console.log('✅ 页面脚本执行完成');
    </script>
</body>
</html>"""
        
        # 保存并访问测试页面
        temp_html = "/tmp/final_client_hints_test.html"
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(test_html)
        
        logger.info("🌐 访问最终测试页面...")
        page.get(f"file://{temp_html}")
        
        # 等待页面加载
        time.sleep(3)
        
        # 执行最终验证
        final_check = page.run_js("""
            return {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                hasUserAgentData: typeof navigator.userAgentData !== 'undefined',
                userAgentData: navigator.userAgentData ? {
                    brands: navigator.userAgentData.brands,
                    mobile: navigator.userAgentData.mobile,
                    platform: navigator.userAgentData.platform
                } : null
            };
        """)
        
        logger.info("📊 最终验证结果:")
        logger.info(f"  User-Agent: {final_check.get('userAgent', 'N/A')[:60]}...")
        logger.info(f"  Platform: {final_check.get('platform', 'N/A')}")
        logger.info(f"  有 userAgentData: {final_check.get('hasUserAgentData', False)}")
        
        if final_check.get('userAgentData'):
            uad = final_check['userAgentData']
            logger.info(f"  userAgentData.platform: {uad.get('platform', 'N/A')}")
            logger.info(f"  userAgentData.brands: {uad.get('brands', 'N/A')}")
        
        input("\n👀 请查看页面结果，点击'测试HTTP请求头'按钮，然后按回车键继续...")
        
        # 访问原始测试网站
        logger.info("\n🌐 访问原始测试网站...")
        page.get('https://uutool.cn/browser/')
        
        input("\n📊 请查看uutool.cn的检测结果，按回车键结束测试...")
        
    finally:
        # 清理
        try:
            page.quit()
            os.remove(temp_html)
            # 清理临时目录
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.debug(f"清理失败: {e}")
    
    logger.success("✅ 最终测试完成!")


if __name__ == "__main__":
    try:
        test_enhanced_client_hints()
    except KeyboardInterrupt:
        logger.info("用户中断测试")
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
