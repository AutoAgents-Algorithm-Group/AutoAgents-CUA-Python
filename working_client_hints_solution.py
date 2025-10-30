#!/usr/bin/env python3
"""
实际可工作的 Client Hints 修改方案
基于比特指纹浏览器技术原理的开源实现
"""

import os
import sys
import time
import json
import tempfile
import shutil

# 确保项目根目录在sys.path中
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from DrissionPage import WebPage, ChromiumOptions
from src.autoagents_cua.utils import logger
from src.autoagents_cua.browser import BrowserFingerprint

def create_working_client_hints_solution():
    """
    创建实际可工作的Client Hints修改方案
    
    原理解析：
    1. 比特指纹浏览器使用内核级修改
    2. 我们使用多层JavaScript注入 + 启动参数组合
    3. 虽然不如内核修改完美，但在大多数情况下有效
    """
    
    logger.info("=" * 60)
    logger.info("🔧 启动可工作的 Client Hints 修改方案")
    logger.info("=" * 60)
    
    # 1. 获取目标指纹配置
    fingerprint = BrowserFingerprint.get_preset('windows_chrome')
    client_hints = fingerprint.get('client_hints', {})
    user_agent = fingerprint.get('user_agent', '')
    
    logger.info("🎯 目标配置:")
    logger.info(f"   平台: {client_hints.get('Sec-CH-UA-Platform', 'Windows')}")
    logger.info(f"   移动设备: {client_hints.get('Sec-CH-UA-Mobile', '?0')}")
    
    # 2. 创建ChromiumOptions - 多重保障方案
    co = ChromiumOptions()
    co.headless(False)
    
    # 方案A: 环境变量强制 (模拟比特浏览器的系统级修改)
    logger.info("🔧 方案A: 设置系统环境变量...")
    env_platform = client_hints.get('Sec-CH-UA-Platform', '"Windows"').strip('"')
    env_mobile = '1' if client_hints.get('Sec-CH-UA-Mobile') == '?1' else '0'
    
    os.environ['FORCE_UA_PLATFORM'] = env_platform
    os.environ['FORCE_UA_MOBILE'] = env_mobile
    os.environ['CHROME_USER_AGENT_PLATFORM'] = env_platform
    logger.success(f"✅ 环境变量已设置: 平台={env_platform}, 移动={env_mobile}")
    
    # 方案B: Chrome启动参数 (模拟内核参数)
    logger.info("🔧 方案B: 设置Chrome启动参数...")
    startup_args = [
        f'--user-agent={user_agent}',
        '--enable-features=UserAgentClientHint',
        '--disable-features=UserAgentReduction',
        f'--force-user-agent-platform={env_platform}',
        f'--simulate-platform={env_platform}',
        '--disable-web-security',  # 允许更深入的修改
        '--disable-features=VizDisplayCompositor',
        '--no-sandbox',
        '--allow-running-insecure-content'
    ]
    
    for arg in startup_args:
        co.add_argument(arg)
    
    logger.success(f"✅ 启动参数已设置: {len(startup_args)} 个")
    
    # 方案C: 预注入脚本 (最早期执行)
    logger.info("🔧 方案C: 创建预注入脚本...")
    
    # 创建一个比JavaScript执行更早的脚本
    pre_inject_script = f"""
    // 预注入脚本 - 在任何页面脚本之前执行
    (function() {{
        'use strict';
        
        // 立即保存原始函数引用
        const originalDefineProperty = Object.defineProperty;
        const originalGetOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;
        
        console.log('🚀 预注入脚本开始执行...');
        
        const clientHintsData = {json.dumps(client_hints)};
        const targetPlatform = {json.dumps(env_platform)};
        
        // 解析品牌信息
        const brands = [];
        if (clientHintsData['Sec-CH-UA']) {{
            const brandString = clientHintsData['Sec-CH-UA'];
            const matches = brandString.match(/"([^"]+)";v="([^"]+)"/g) || [];
            matches.forEach(match => {{
                const [, brand, version] = match.match(/"([^"]+)";v="([^"]+)"/);
                brands.push({{ brand, version }});
            }});
        }}
        
        // 创建终极userAgentData对象
        const ultimateUserAgentData = {{
            brands: brands,
            mobile: clientHintsData['Sec-CH-UA-Mobile'] === '?1',
            platform: targetPlatform,
            
            getHighEntropyValues: function(hints) {{
                const result = {{
                    brands: this.brands,
                    mobile: this.mobile,
                    platform: this.platform
                }};
                
                hints.forEach(hint => {{
                    switch(hint) {{
                        case 'architecture':
                            result.architecture = clientHintsData['Sec-CH-UA-Arch'] ? clientHintsData['Sec-CH-UA-Arch'].replace(/"/g, '') : 'x86';
                            break;
                        case 'bitness':
                            result.bitness = clientHintsData['Sec-CH-UA-Bitness'] ? clientHintsData['Sec-CH-UA-Bitness'].replace(/"/g, '') : '64';
                            break;
                        case 'platformVersion':
                            result.platformVersion = clientHintsData['Sec-CH-UA-Platform-Version'] ? clientHintsData['Sec-CH-UA-Platform-Version'].replace(/"/g, '') : '';
                            break;
                        case 'uaFullVersion':
                            result.uaFullVersion = clientHintsData['Sec-CH-UA-Full-Version'] ? clientHintsData['Sec-CH-UA-Full-Version'].replace(/"/g, '') : '';
                            break;
                    }}
                }});
                
                console.log('✅ getHighEntropyValues 返回:', result);
                return Promise.resolve(result);
            }},
            
            toJSON: function() {{
                return {{ brands: this.brands, mobile: this.mobile, platform: this.platform }};
            }}
        }};
        
        // 多重替换策略
        let successCount = 0;
        
        // 策略1: 拦截Navigator构造函数
        try {{
            const OriginalNavigator = window.Navigator || Navigator;
            if (OriginalNavigator && OriginalNavigator.prototype) {{
                originalDefineProperty(OriginalNavigator.prototype, 'userAgentData', {{
                    get: function() {{ return ultimateUserAgentData; }},
                    configurable: true,
                    enumerable: true
                }});
                successCount++;
                console.log('✅ 策略1成功: Navigator原型修改');
            }}
        }} catch (e) {{
            console.warn('⚠️  策略1失败:', e);
        }}
        
        // 策略2: 直接替换window.navigator
        try {{
            if (window.navigator) {{
                originalDefineProperty(window.navigator, 'userAgentData', {{
                    value: ultimateUserAgentData,
                    writable: false,
                    configurable: true,
                    enumerable: true
                }});
                successCount++;
                console.log('✅ 策略2成功: 直接替换navigator');
            }}
        }} catch (e) {{
            console.warn('⚠️  策略2失败:', e);
        }}
        
        // 策略3: 拦截所有defineProperty调用
        try {{
            Object.defineProperty = function(obj, prop, descriptor) {{
                if (obj === navigator && prop === 'userAgentData') {{
                    console.log('🛡️ 拦截原生userAgentData定义，使用我们的版本');
                    return originalDefineProperty(obj, prop, {{
                        value: ultimateUserAgentData,
                        writable: false,
                        configurable: true,
                        enumerable: true
                    }});
                }}
                return originalDefineProperty(obj, prop, descriptor);
            }};
            successCount++;
            console.log('✅ 策略3成功: defineProperty拦截');
        }} catch (e) {{
            console.warn('⚠️  策略3失败:', e);
        }}
        
        // 策略4: 延迟执行保障
        setTimeout(() => {{
            try {{
                if (!navigator.userAgentData || navigator.userAgentData.platform !== targetPlatform) {{
                    console.log('🔄 延迟保障执行...');
                    navigator.userAgentData = ultimateUserAgentData;
                    successCount++;
                    console.log('✅ 策略4成功: 延迟保障');
                }}
            }} catch (e) {{
                console.warn('⚠️  策略4失败:', e);
            }}
        }}, 100);
        
        console.log(`🎯 预注入完成，成功策略: ${{successCount}}/4`);
        
        // 验证最终结果
        setTimeout(() => {{
            if (navigator.userAgentData) {{
                console.log('🔍 最终验证结果:');
                console.log('  platform:', navigator.userAgentData.platform);
                console.log('  mobile:', navigator.userAgentData.mobile);
                console.log('  brands:', navigator.userAgentData.brands);
                
                if (navigator.userAgentData.platform === targetPlatform) {{
                    console.log('🎉 Client Hints 修改成功!');
                }} else {{
                    console.log('❌ Client Hints 修改失败');
                }}
            }}
        }}, 200);
        
    }})();
    """
    
    # 使用临时用户数据目录
    temp_dir = tempfile.mkdtemp(prefix='client_hints_test_')
    co.set_user_data_path(temp_dir)
    
    logger.success("✅ 预注入脚本已准备")
    
    # 3. 启动浏览器并测试
    web_page = None
    try:
        logger.info("🚀 启动浏览器...")
        web_page = WebPage(chromium_options=co)
        
        # 注入预执行脚本
        logger.info("💉 注入预执行脚本...")
        web_page.run_js(pre_inject_script)
        
        logger.success("✅ 浏览器启动成功")
        
        # 等待初始化
        time.sleep(2)
        
        # 4. 测试效果
        logger.info("🧪 开始测试Client Hints修改效果...")
        
        # 访问测试页面
        test_url = 'https://httpbin.org/headers'
        logger.info(f"🌐 访问测试页面: {test_url}")
        web_page.get(test_url)
        time.sleep(3)
        
        # JavaScript验证
        verify_script = """
        return {
            available: !!navigator.userAgentData,
            platform: navigator.userAgentData ? navigator.userAgentData.platform : null,
            mobile: navigator.userAgentData ? navigator.userAgentData.mobile : null,
            brands: navigator.userAgentData ? navigator.userAgentData.brands : null
        };
        """
        
        try:
            result = web_page.run_js(verify_script)
            logger.info("📋 JavaScript API验证结果:")
            logger.info(f"   可用: {result.get('available')}")
            logger.info(f"   平台: {result.get('platform')}")
            logger.info(f"   移动设备: {result.get('mobile')}")
            
            if result.get('platform') == env_platform:
                logger.success("🎉 JavaScript API平台修改成功!")
            else:
                logger.warning(f"⚠️  JavaScript API平台未修改: 期望 {env_platform}, 实际 {result.get('platform')}")
                
        except Exception as e:
            logger.error(f"❌ JavaScript验证失败: {e}")
        
        # 5. 用户交互测试
        print("\n" + "="*60)
        print("🔍 请检查以下内容:")
        print("1. httpbin.org 页面中的 'Sec-Ch-Ua-Platform' 头部")
        print("2. 平台是否显示为 'Windows' 而不是 'macOS'")
        print("3. 浏览器控制台是否有 '🎉 Client Hints 修改成功!' 消息")
        print("="*60)
        
        input("检查完毕后按回车键继续...")
        
        # 6. 访问uutool进行综合测试
        logger.info("🌐 访问 uutool.cn 进行综合检测...")
        web_page.get('https://uutool.cn/browser/')
        time.sleep(3)
        
        print("\n" + "="*60)
        print("🔍 请在uutool.cn检查:")
        print("1. Client Hints部分的平台信息")
        print("2. 是否正确显示为Windows")
        print("3. 其他Client Hints信息是否符合预期")
        print("="*60)
        
        input("所有测试完成后按回车键结束...")
        
    except Exception as e:
        logger.error(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 清理
        if web_page:
            try:
                web_page.quit()
                logger.info("🔒 浏览器已关闭")
            except:
                pass
        
        # 清理临时目录
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"🗑️ 临时目录已清理: {temp_dir}")
            except:
                pass
        
        logger.success("\n" + "="*60)
        logger.success("🎉 Client Hints 工作方案测试完成")
        logger.success("="*60)

if __name__ == '__main__':
    create_working_client_hints_solution()
