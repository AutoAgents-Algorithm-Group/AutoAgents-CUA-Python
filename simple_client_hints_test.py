#!/usr/bin/env python3
"""
简化的Client Hints测试 - 直接使用DrissionPage
演示比特指纹浏览器的技术原理和我们的实现对比
"""

import os
import time
import json
import tempfile
import shutil

from DrissionPage import WebPage, ChromiumOptions

def simple_client_hints_test():
    """简化的Client Hints测试"""
    
    print("=" * 60)
    print("🎯 Client Hints 技术原理对比测试")
    print("=" * 60)
    
    # 目标Client Hints配置
    target_client_hints = {
        'Sec-CH-UA': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Sec-CH-UA-Platform-Version': '"15.0.0"',
        'Sec-CH-UA-Arch': '"x86"',
        'Sec-CH-UA-Bitness': '"64"',
        'Sec-CH-UA-Model': '""',
        'Sec-CH-UA-Full-Version': '"131.0.6778.86"'
    }
    
    target_platform = "Windows"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    
    print(f"🎯 目标平台: {target_platform}")
    print(f"🎯 当前系统: macOS (需要伪装成Windows)")
    
    # 比特指纹浏览器的技术原理说明
    print("\n📋 技术原理对比:")
    print("🔧 比特指纹浏览器: 修改Chromium内核源码，C++层面控制")
    print("🔧 我们的方案: JavaScript多重注入 + 启动参数组合")
    
    # 创建ChromiumOptions
    co = ChromiumOptions()
    co.headless(False)
    
    # 方案1: 启动参数设置
    print("\n🔧 方案1: Chrome启动参数设置...")
    co.set_user_agent(user_agent)
    co.set_argument('--enable-features=UserAgentClientHint')
    co.set_argument('--disable-features=UserAgentReduction')
    co.set_argument('--disable-web-security')
    co.set_argument('--no-sandbox')
    print("✅ 启动参数已设置")
    
    # 方案2: 环境变量设置 (模拟比特浏览器的系统级修改)
    print("\n🔧 方案2: 环境变量设置...")
    os.environ['FORCE_UA_PLATFORM'] = target_platform
    os.environ['CHROME_USER_AGENT_PLATFORM'] = target_platform
    print("✅ 环境变量已设置")
    
    # 方案3: 预注入脚本 (最关键的部分)
    print("\n🔧 方案3: 准备JavaScript预注入脚本...")
    
    # 创建强力注入脚本
    injection_script = f"""
    // Client Hints 强力注入脚本
    (function() {{
        'use strict';
        console.log('🚀 Client Hints 注入脚本开始执行...');
        
        const targetPlatform = "{target_platform}";
        const clientHintsData = {json.dumps(target_client_hints)};
        
        // 解析品牌信息
        const brands = [];
        if (clientHintsData['Sec-CH-UA']) {{
            const brandMatches = clientHintsData['Sec-CH-UA'].match(/"([^"]+)";v="([^"]+)"/g) || [];
            brandMatches.forEach(match => {{
                const [, brand, version] = match.match(/"([^"]+)";v="([^"]+)"/);
                brands.push({{ brand, version }});
            }});
        }}
        
        // 创建新的userAgentData对象
        const newUserAgentData = {{
            brands: brands,
            mobile: clientHintsData['Sec-CH-UA-Mobile'] === '?1',
            platform: targetPlatform,
            
            getHighEntropyValues: function(hints) {{
                console.log('🔍 getHighEntropyValues被调用:', hints);
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
                
                console.log('✅ getHighEntropyValues返回:', result);
                return Promise.resolve(result);
            }},
            
            toJSON: function() {{
                return {{ brands: this.brands, mobile: this.mobile, platform: this.platform }};
            }}
        }};
        
        // 多重替换策略 (模拟比特浏览器的内核级控制)
        let successCount = 0;
        
        // 策略1: 直接替换
        try {{
            Object.defineProperty(navigator, 'userAgentData', {{
                value: newUserAgentData,
                writable: false,
                configurable: true,
                enumerable: true
            }});
            successCount++;
            console.log('✅ 策略1成功: 直接替换');
        }} catch (e) {{
            console.warn('⚠️  策略1失败:', e);
        }}
        
        // 策略2: 原型链修改
        try {{
            if (Navigator && Navigator.prototype) {{
                Object.defineProperty(Navigator.prototype, 'userAgentData', {{
                    get: function() {{ return newUserAgentData; }},
                    configurable: true,
                    enumerable: true
                }});
                successCount++;
                console.log('✅ 策略2成功: 原型链修改');
            }}
        }} catch (e) {{
            console.warn('⚠️  策略2失败:', e);
        }}
        
        // 策略3: 定时保障
        setInterval(() => {{
            try {{
                if (!navigator.userAgentData || navigator.userAgentData.platform !== targetPlatform) {{
                    navigator.userAgentData = newUserAgentData;
                    console.log('🔄 定时保障执行');
                }}
            }} catch (e) {{}}
        }}, 1000);
        
        console.log(`🎯 注入完成，成功策略: ${{successCount}}/2`);
        
        // 立即验证
        setTimeout(() => {{
            if (navigator.userAgentData) {{
                console.log('🔍 验证结果:');
                console.log('  平台:', navigator.userAgentData.platform);
                console.log('  移动设备:', navigator.userAgentData.mobile);
                console.log('  品牌:', navigator.userAgentData.brands);
                
                if (navigator.userAgentData.platform === targetPlatform) {{
                    console.log('🎉 Client Hints 修改成功!');
                    window.__CLIENT_HINTS_SUCCESS = true;
                }} else {{
                    console.log('❌ Client Hints 修改失败');
                    window.__CLIENT_HINTS_SUCCESS = false;
                }}
            }} else {{
                console.log('❌ navigator.userAgentData 不可用');
                window.__CLIENT_HINTS_SUCCESS = false;
            }}
        }}, 500);
        
    }})();
    """
    
    print("✅ 注入脚本已准备")
    
    # 使用临时目录
    temp_dir = tempfile.mkdtemp(prefix='client_hints_simple_')
    co.set_user_data_path(temp_dir)
    
    web_page = None
    try:
        print("\n🚀 启动浏览器...")
        web_page = WebPage(chromium_options=co)
        print("✅ 浏览器启动成功")
        
        # 立即注入脚本
        print("\n💉 注入Client Hints修改脚本...")
        web_page.run_js(injection_script)
        print("✅ 脚本注入完成")
        
        # 等待生效
        time.sleep(2)
        
        # 测试1: JavaScript API验证
        print("\n🧪 测试1: JavaScript API验证...")
        try:
            js_result = web_page.run_js("""
                return {
                    available: !!navigator.userAgentData,
                    platform: navigator.userAgentData ? navigator.userAgentData.platform : null,
                    mobile: navigator.userAgentData ? navigator.userAgentData.mobile : null,
                    success: window.__CLIENT_HINTS_SUCCESS || false
                };
            """)
            
            print(f"   可用性: {js_result.get('available')}")
            print(f"   平台: {js_result.get('platform')}")
            print(f"   移动设备: {js_result.get('mobile')}")
            print(f"   修改成功: {js_result.get('success')}")
            
            if js_result.get('platform') == target_platform:
                print("🎉 JavaScript API测试成功!")
            else:
                print(f"⚠️  JavaScript API测试失败: 期望{target_platform}, 实际{js_result.get('platform')}")
                
        except Exception as e:
            print(f"❌ JavaScript验证出错: {e}")
        
        # 测试2: HTTP请求头验证
        print("\n🧪 测试2: 访问httpbin.org验证HTTP请求头...")
        web_page.get('https://httpbin.org/headers')
        time.sleep(3)
        
        print("\n📋 请检查httpbin.org页面中的请求头:")
        print("1. 查找 'Sec-Ch-Ua-Platform' 头部")
        print("2. 确认是否显示为 'Windows' 而不是 'macOS'")
        print("3. 检查其他Client Hints头部是否正确")
        
        input("\n按回车键继续测试uutool.cn...")
        
        # 测试3: uutool综合测试
        print("\n🧪 测试3: 访问uutool.cn进行综合检测...")
        web_page.get('https://uutool.cn/browser/')
        time.sleep(3)
        
        print("\n📋 请在uutool.cn页面检查:")
        print("1. Client Hints部分的平台信息")
        print("2. 用户代理信息是否显示为Windows")
        print("3. 整体指纹信息是否符合预期")
        
        print("\n🔍 技术对比总结:")
        print("✅ 比特指纹浏览器: 内核级修改，100%成功率")
        print("🔧 我们的方案: JavaScript注入，在大多数情况下有效")
        print("💡 差距原因: 网站可以检测JavaScript修改，但无法检测内核修改")
        
        input("\n测试完成，按回车键关闭浏览器...")
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if web_page:
            try:
                web_page.quit()
                print("🔒 浏览器已关闭")
            except:
                pass
        
        # 清理临时目录
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print(f"🗑️ 临时目录已清理")
            except:
                pass
        
        print("\n" + "="*60)
        print("🎉 Client Hints 技术原理对比测试完成")
        print("="*60)

if __name__ == '__main__':
    simple_client_hints_test()