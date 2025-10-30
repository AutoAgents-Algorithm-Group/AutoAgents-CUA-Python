from ..utils.logging import logger
from typing import Dict, Any, Optional, List
import random
import json



class BrowserFingerprint:
    """
    浏览器指纹管理器
    
    提供以下功能：
    1. 预设指纹模板（Windows/Mac/Linux）
    2. 随机指纹生成
    3. 自定义指纹配置
    4. 应用到 ChromiumOptions
    5. JavaScript 注入脚本生成
    """
    
    # ========== 真实浏览器指纹预设 ==========
    PRESETS = {
        'windows_chrome': {
            'name': 'Windows Chrome 131',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'platform': 'Win32',
            'screen': {
                'width': 1920,
                'height': 1080,
                'depth': 24,
                'avail_width': 1920,
                'avail_height': 1040  # 减去任务栏
            },
            'timezone': 'America/New_York',
            'language': 'en-US',
            'languages': ['en-US', 'en'],
            'webgl_vendor': 'Google Inc. (NVIDIA)',
            'webgl_renderer': 'ANGLE (NVIDIA GeForce GTX 1060 6GB Direct3D11 vs_5_0 ps_5_0)',
            'hardware_concurrency': 8,
            'device_memory': 16,
            'max_touch_points': 0,
            'canvas_noise': random.randint(0, 10),
            'audio_noise': round(random.random() * 0.01, 6)
        },
        
        'mac_chrome': {
            'name': 'Mac Chrome 131',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'platform': 'MacIntel',
            'screen': {
                'width': 1440,
                'height': 900,
                'depth': 24,
                'avail_width': 1440,
                'avail_height': 877  # 减去顶栏
            },
            'timezone': 'America/Los_Angeles',
            'language': 'en-US',
            'languages': ['en-US', 'en'],
            'webgl_vendor': 'Intel Inc.',
            'webgl_renderer': 'Intel Iris Pro OpenGL Engine',
            'hardware_concurrency': 4,
            'device_memory': 8,
            'max_touch_points': 0,
            'canvas_noise': random.randint(0, 10),
            'audio_noise': round(random.random() * 0.01, 6)
        },
        
        'linux_chrome': {
            'name': 'Linux Chrome 131',
            'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'platform': 'Linux x86_64',
            'screen': {
                'width': 1920,
                'height': 1080,
                'depth': 24,
                'avail_width': 1920,
                'avail_height': 1080
            },
            'timezone': 'Europe/London',
            'language': 'en-GB',
            'languages': ['en-GB', 'en'],
            'webgl_vendor': 'Intel Open Source Technology Center',
            'webgl_renderer': 'Mesa DRI Intel(R) HD Graphics 620 (Kaby Lake GT2)',
            'hardware_concurrency': 4,
            'device_memory': 8,
            'max_touch_points': 0,
            'canvas_noise': random.randint(0, 10),
            'audio_noise': round(random.random() * 0.01, 6)
        },
        
        'mac_safari': {
            'name': 'Mac Safari 17',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'platform': 'MacIntel',
            'screen': {
                'width': 1680,
                'height': 1050,
                'depth': 24,
                'avail_width': 1680,
                'avail_height': 1027
            },
            'timezone': 'America/Los_Angeles',
            'language': 'en-US',
            'languages': ['en-US', 'en'],
            'webgl_vendor': 'Apple Inc.',
            'webgl_renderer': 'Apple M1',
            'hardware_concurrency': 8,
            'device_memory': 16,
            'max_touch_points': 0,
            'canvas_noise': random.randint(0, 10),
            'audio_noise': round(random.random() * 0.01, 6)
        },
        
        'windows_edge': {
            'name': 'Windows Edge 131',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
            'platform': 'Win32',
            'screen': {
                'width': 2560,
                'height': 1440,
                'depth': 24,
                'avail_width': 2560,
                'avail_height': 1400
            },
            'timezone': 'America/New_York',
            'language': 'en-US',
            'languages': ['en-US', 'en'],
            'webgl_vendor': 'Google Inc. (AMD)',
            'webgl_renderer': 'ANGLE (AMD Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0)',
            'hardware_concurrency': 16,
            'device_memory': 16,
            'max_touch_points': 0,
            'canvas_noise': random.randint(0, 10),
            'audio_noise': round(random.random() * 0.01, 6)
        }
    }
    
    # ========== 常见屏幕分辨率 ==========
    COMMON_RESOLUTIONS = [
        {'width': 1920, 'height': 1080, 'depth': 24},
        {'width': 1366, 'height': 768, 'depth': 24},
        {'width': 1440, 'height': 900, 'depth': 24},
        {'width': 1536, 'height': 864, 'depth': 24},
        {'width': 1600, 'height': 900, 'depth': 24},
        {'width': 2560, 'height': 1440, 'depth': 24},
        {'width': 1680, 'height': 1050, 'depth': 24},
    ]
    
    # ========== 时区列表 ==========
    COMMON_TIMEZONES = [
        'America/New_York',
        'America/Los_Angeles',
        'America/Chicago',
        'Europe/London',
        'Europe/Paris',
        'Asia/Shanghai',
        'Asia/Tokyo',
        'Australia/Sydney'
    ]
    
    @staticmethod
    def get_preset(preset_name: str) -> Optional[Dict[str, Any]]:
        """
        获取预设指纹
        
        Args:
            preset_name: 预设名称 (windows_chrome, mac_chrome, linux_chrome, mac_safari, windows_edge)
            
        Returns:
            指纹配置字典，如果预设不存在返回 None
        """
        preset = BrowserFingerprint.PRESETS.get(preset_name)
        if preset:
            # 返回副本，避免修改原始预设
            return preset.copy()
        return None
    
    @staticmethod
    def list_presets() -> List[str]:
        """
        列出所有可用的预设
        
        Returns:
            预设名称列表
        """
        return list(BrowserFingerprint.PRESETS.keys())
    
    @staticmethod
    def generate_random_fingerprint(platform_pool: Optional[List[str]] = None, add_noise: bool = True) -> Dict[str, Any]:
        """
        生成随机浏览器指纹
        
        Args:
            platform_pool: 平台池，默认包含所有预设
            add_noise: 是否添加随机噪点
            
        Returns:
            随机生成的指纹配置
        """
        # 从平台池中随机选择
        if platform_pool is None:
            platform_pool = list(BrowserFingerprint.PRESETS.keys())
        
        preset_name = random.choice(platform_pool)
        fingerprint = BrowserFingerprint.PRESETS[preset_name].copy()
        
        # 添加随机性
        if add_noise:
            # 随机调整屏幕分辨率（从常见分辨率中选择）
            fingerprint['screen'] = random.choice(BrowserFingerprint.COMMON_RESOLUTIONS).copy()
            
            # 随机时区
            fingerprint['timezone'] = random.choice(BrowserFingerprint.COMMON_TIMEZONES)
            
            # 随机 Canvas 和 Audio 噪点
            fingerprint['canvas_noise'] = random.randint(0, 100)
            fingerprint['audio_noise'] = round(random.random() * 0.01, 6)
            
            # 随机 CPU 核心数（2-16）
            fingerprint['hardware_concurrency'] = random.choice([2, 4, 6, 8, 12, 16])
            
            # 随机内存（4, 8, 16, 32 GB）
            fingerprint['device_memory'] = random.choice([4, 8, 16, 32])
        
        logger.info(f"生成随机指纹: {fingerprint.get('name', '未命名')}")
        return fingerprint
    
    @staticmethod
    def validate_fingerprint(fingerprint: Dict[str, Any]) -> bool:
        """
        验证指纹配置的一致性和合法性
        
        Args:
            fingerprint: 指纹配置字典
            
        Returns:
            是否通过验证
        """
        try:
            # 检查必需字段
            required_fields = ['user_agent', 'platform', 'screen', 'timezone', 'language']
            for field in required_fields:
                if field not in fingerprint:
                    logger.error(f"指纹缺少必需字段: {field}")
                    return False
            
            # 检查平台与 User-Agent 的一致性
            platform = fingerprint.get('platform', '')
            user_agent = fingerprint.get('user_agent', '')
            
            if platform == 'MacIntel' and 'Macintosh' not in user_agent:
                logger.warning("平台为 Mac 但 User-Agent 不匹配")
                return False
            
            if platform == 'Win32' and 'Windows' not in user_agent:
                logger.warning("平台为 Windows 但 User-Agent 不匹配")
                return False
            
            if 'Linux' in platform and 'Linux' not in user_agent:
                logger.warning("平台为 Linux 但 User-Agent 不匹配")
                return False
            
            # 检查屏幕分辨率
            screen = fingerprint.get('screen', {})
            if screen.get('width', 0) < 800 or screen.get('height', 0) < 600:
                logger.warning("屏幕分辨率过小")
                return False
            
            logger.success("指纹配置验证通过")
            return True
            
        except Exception as e:
            logger.error(f"指纹验证失败: {e}")
            return False
    
    @staticmethod
    def apply_to_chromium_options(co, fingerprint: Dict[str, Any]):
        """
        将指纹配置应用到 ChromiumOptions
        
        Args:
            co: ChromiumOptions 实例
            fingerprint: 指纹配置字典
            
        Returns:
            配置后的 ChromiumOptions 实例
        """
        try:
            # 1. User-Agent
            user_agent = fingerprint.get('user_agent')
            if user_agent:
                co.set_user_agent(user_agent)  # 修复：使用 set_user_agent 而不是 set_argument
                logger.info(f"设置 User-Agent: {user_agent[:50]}...")
            
            # 2. 屏幕分辨率
            screen = fingerprint.get('screen', {})
            width = screen.get('width', 1920)
            height = screen.get('height', 1080)
            co.set_argument(f'--window-size={width},{height}')
            logger.info(f"设置窗口大小: {width}x{height}")
            
            # 3. 语言
            language = fingerprint.get('language', 'en-US')
            co.set_argument(f'--lang={language}')
            logger.info(f"设置语言: {language}")
            
            # 4. 隐藏自动化特征
            co.set_argument('--disable-blink-features=AutomationControlled')
            
            # 5. 禁用 WebRTC（防止真实 IP 泄露）
            co.set_pref('webrtc.ip_handling_policy', 'disable_non_proxied_udp')
            co.set_pref('webrtc.multiple_routes_enabled', False)
            co.set_pref('webrtc.nonproxied_udp_enabled', False)
            
            # 6. 移除自动化标识
            co.set_pref('excludeSwitches', ['enable-automation'])
            co.set_pref('useAutomationExtension', False)
            
            # 7. 禁用密码保存提示
            co.set_pref('credentials_enable_service', False)
            co.set_pref('profile.password_manager_enabled', False)
            
            # 8. 其他反检测设置
            co.set_argument('--disable-dev-shm-usage')
            co.set_argument('--no-first-run')
            co.set_argument('--no-default-browser-check')
            
            # 9. 自动端口配置（避免端口冲突）
            co.auto_port()
            logger.info("已启用自动端口管理")
            
            logger.success("指纹配置已应用到 ChromiumOptions")
            return co
            
        except Exception as e:
            logger.error(f"应用指纹配置失败: {e}")
            return co
    
    @staticmethod
    def get_injection_script(fingerprint: Dict[str, Any]) -> str:
        """
        生成需要注入页面的 JavaScript 代码
        
        Args:
            fingerprint: 指纹配置字典
            
        Returns:
            JavaScript 代码字符串
        """
        webgl_vendor = fingerprint.get('webgl_vendor', 'Intel Inc.')
        webgl_renderer = fingerprint.get('webgl_renderer', 'Intel Iris OpenGL Engine')
        platform = fingerprint.get('platform', 'Win32')
        hardware_concurrency = fingerprint.get('hardware_concurrency', 4)
        device_memory = fingerprint.get('device_memory', 8)
        max_touch_points = fingerprint.get('max_touch_points', 0)
        languages = fingerprint.get('languages', ['en-US', 'en'])
        canvas_noise = fingerprint.get('canvas_noise', 0)
        
        screen = fingerprint.get('screen', {})
        screen_width = screen.get('width', 1920)
        screen_height = screen.get('height', 1080)
        screen_depth = screen.get('depth', 24)
        avail_width = screen.get('avail_width', screen_width)
        avail_height = screen.get('avail_height', screen_height - 40)
        
        script = f"""
// ========== 浏览器指纹修改脚本 ==========
(function() {{
    'use strict';
    
    // 1. WebGL 指纹修改
    try {{
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            // VENDOR: 7936
            if (parameter === 7936) {{
                return '{webgl_vendor}';
            }}
            // RENDERER: 7937
            if (parameter === 7937) {{
                return '{webgl_renderer}';
            }}
            // UNMASKED_VENDOR_WEBGL: 37445
            if (parameter === 37445) {{
                return '{webgl_vendor}';
            }}
            // UNMASKED_RENDERER_WEBGL: 37446
            if (parameter === 37446) {{
                return '{webgl_renderer}';
            }}
            return getParameter.apply(this, arguments);
        }};
        
        // WebGL2 支持
        if (typeof WebGL2RenderingContext !== 'undefined') {{
            const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
            WebGL2RenderingContext.prototype.getParameter = function(parameter) {{
                if (parameter === 7936) return '{webgl_vendor}';
                if (parameter === 7937) return '{webgl_renderer}';
                if (parameter === 37445) return '{webgl_vendor}';
                if (parameter === 37446) return '{webgl_renderer}';
                return getParameter2.apply(this, arguments);
            }};
        }}
    }} catch (e) {{
        console.warn('WebGL 指纹修改失败:', e);
    }}
    
    // 2. Navigator 对象修改
    try {{
        // Platform
        Object.defineProperty(navigator, 'platform', {{
            get: function() {{ return '{platform}'; }}
        }});
        
        // Hardware Concurrency (CPU 核心数)
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: function() {{ return {hardware_concurrency}; }}
        }});
        
        // Device Memory (设备内存 GB)
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: function() {{ return {device_memory}; }}
        }});
        
        // Max Touch Points
        Object.defineProperty(navigator, 'maxTouchPoints', {{
            get: function() {{ return {max_touch_points}; }}
        }});
        
        // Languages
        Object.defineProperty(navigator, 'languages', {{
            get: function() {{ return {json.dumps(languages)}; }}
        }});
        
        // 删除 webdriver 标识
        Object.defineProperty(navigator, 'webdriver', {{
            get: function() {{ return undefined; }}
        }});
        
        // Plugins (返回空数组，避免暴露无插件特征)
        Object.defineProperty(navigator, 'plugins', {{
            get: function() {{
                return [
                    {{
                        0: {{type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"}},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    }}
                ];
            }}
        }});
    }} catch (e) {{
        console.warn('Navigator 对象修改失败:', e);
    }}
    
    // 3. Screen 对象修改
    try {{
        Object.defineProperty(window.screen, 'width', {{
            get: function() {{ return {screen_width}; }}
        }});
        
        Object.defineProperty(window.screen, 'height', {{
            get: function() {{ return {screen_height}; }}
        }});
        
        Object.defineProperty(window.screen, 'availWidth', {{
            get: function() {{ return {avail_width}; }}
        }});
        
        Object.defineProperty(window.screen, 'availHeight', {{
            get: function() {{ return {avail_height}; }}
        }});
        
        Object.defineProperty(window.screen, 'colorDepth', {{
            get: function() {{ return {screen_depth}; }}
        }});
        
        Object.defineProperty(window.screen, 'pixelDepth', {{
            get: function() {{ return {screen_depth}; }}
        }});
    }} catch (e) {{
        console.warn('Screen 对象修改失败:', e);
    }}
    
    // 4. Canvas 指纹添加噪点
    try {{
        const toDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {{
            const context = this.getContext('2d');
            if (context) {{
                const imageData = context.getImageData(0, 0, this.width, this.height);
                const noise = {canvas_noise};
                
                // 添加随机噪点
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    imageData.data[i] = Math.min(255, imageData.data[i] + Math.floor(Math.random() * noise));
                    imageData.data[i + 1] = Math.min(255, imageData.data[i + 1] + Math.floor(Math.random() * noise));
                    imageData.data[i + 2] = Math.min(255, imageData.data[i + 2] + Math.floor(Math.random() * noise));
                }}
                
                context.putImageData(imageData, 0, 0);
            }}
            return toDataURL.apply(this, arguments);
        }};
        
        const toBlob = HTMLCanvasElement.prototype.toBlob;
        HTMLCanvasElement.prototype.toBlob = function(callback, type, quality) {{
            const context = this.getContext('2d');
            if (context) {{
                const imageData = context.getImageData(0, 0, this.width, this.height);
                const noise = {canvas_noise};
                
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    imageData.data[i] = Math.min(255, imageData.data[i] + Math.floor(Math.random() * noise));
                    imageData.data[i + 1] = Math.min(255, imageData.data[i + 1] + Math.floor(Math.random() * noise));
                    imageData.data[i + 2] = Math.min(255, imageData.data[i + 2] + Math.floor(Math.random() * noise));
                }}
                
                context.putImageData(imageData, 0, 0);
            }}
            return toBlob.apply(this, [callback, type, quality]);
        }};
    }} catch (e) {{
        console.warn('Canvas 指纹修改失败:', e);
    }}
    
    // 5. AudioContext 指纹修改（添加噪点）
    try {{
        const audioContext = window.AudioContext || window.webkitAudioContext;
        if (audioContext) {{
            const originalCreateAnalyser = audioContext.prototype.createAnalyser;
            audioContext.prototype.createAnalyser = function() {{
                const analyser = originalCreateAnalyser.apply(this, arguments);
                const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;
                const originalGetByteFrequencyData = analyser.getByteFrequencyData;
                
                // 为频率数据添加微小噪点
                analyser.getFloatFrequencyData = function(array) {{
                    originalGetFloatFrequencyData.apply(this, arguments);
                    for (let i = 0; i < array.length; i++) {{
                        array[i] += (Math.random() - 0.5) * 0.01;
                    }}
                }};
                
                analyser.getByteFrequencyData = function(array) {{
                    originalGetByteFrequencyData.apply(this, arguments);
                    for (let i = 0; i < array.length; i++) {{
                        array[i] += Math.floor((Math.random() - 0.5) * 2);
                    }}
                }};
                
                return analyser;
            }};
            
            // 修改 OscillatorNode
            const originalCreateOscillator = audioContext.prototype.createOscillator;
            audioContext.prototype.createOscillator = function() {{
                const oscillator = originalCreateOscillator.apply(this, arguments);
                const originalStart = oscillator.start;
                oscillator.start = function(when) {{
                    // 添加微小的时间偏移
                    const offset = (Math.random() - 0.5) * 0.000001;
                    return originalStart.apply(this, [when ? when + offset : offset]);
                }};
                return oscillator;
            }};
        }}
    }} catch (e) {{
        console.warn('AudioContext 指纹修改失败:', e);
    }}
    
    // 6. Fonts 指纹修改（欺骗字体检测）
    try {{
        // 覆盖 measureText 添加微小变化
        const originalMeasureText = CanvasRenderingContext2D.prototype.measureText;
        CanvasRenderingContext2D.prototype.measureText = function(text) {{
            const metrics = originalMeasureText.apply(this, arguments);
            // 添加微小的宽度偏移（0.1-0.3px）
            const offset = Math.random() * 0.2 + 0.1;
            Object.defineProperty(metrics, 'width', {{
                get: function() {{
                    return this._width || (this._width = metrics.width + offset);
                }},
                configurable: true
            }});
            return metrics;
        }};
        
        // 伪造常见字体存在
        const commonFonts = [
            'Arial', 'Arial Black', 'Arial Narrow', 'Arial Rounded MT Bold',
            'Calibri', 'Cambria', 'Cambria Math', 'Candara',
            'Comic Sans MS', 'Consolas', 'Constantia', 'Corbel',
            'Courier New', 'Georgia', 'Helvetica', 'Impact',
            'Lucida Console', 'Lucida Sans Unicode', 'Microsoft Sans Serif',
            'Palatino Linotype', 'Segoe UI', 'Symbol', 'Tahoma',
            'Times New Roman', 'Trebuchet MS', 'Verdana', 'Webdings', 'Wingdings'
        ];
        
        // 拦截字体检测
        const originalFontFamily = Object.getOwnPropertyDescriptor(CSSStyleDeclaration.prototype, 'fontFamily');
        if (originalFontFamily && originalFontFamily.set) {{
            const originalSet = originalFontFamily.set;
            Object.defineProperty(CSSStyleDeclaration.prototype, 'fontFamily', {{
                set: function(value) {{
                    // 如果设置的字体在常见字体列表中，允许通过
                    return originalSet.apply(this, arguments);
                }},
                get: originalFontFamily.get
            }});
        }}
    }} catch (e) {{
        console.warn('Fonts 指纹修改失败:', e);
    }}
    
    // 7. 移除 Chrome 自动化特征
    try {{
        delete navigator.__proto__.webdriver;
        
        // 覆盖 Chrome 对象
        if (window.chrome) {{
            Object.defineProperty(window, 'chrome', {{
                get: function() {{
                    return {{
                        runtime: {{}},
                        loadTimes: function() {{}},
                        csi: function() {{}},
                        app: {{}}
                    }};
                }}
            }});
        }}
    }} catch (e) {{
        console.warn('移除自动化特征失败:', e);
    }}
    
    console.log('✅ 浏览器指纹修改脚本已注入 (WebGL + Canvas + Navigator + Audio + Fonts)');
}})();
"""
        return script
    
    @staticmethod
    def get_verification_script() -> str:
        """
        生成用于验证指纹是否被成功修改的 JavaScript 脚本
        
        Returns:
            验证脚本字符串
        """
        script = """
// ========== 指纹验证脚本 ==========
(function() {
    console.log('\\n========== 浏览器指纹信息 ==========');
    
    // 1. Navigator 信息
    console.log('\\n[Navigator 信息]');
    console.log('  - User-Agent:', navigator.userAgent);
    console.log('  - Platform:', navigator.platform);
    console.log('  - Hardware Concurrency:', navigator.hardwareConcurrency);
    console.log('  - Device Memory:', navigator.deviceMemory, 'GB');
    console.log('  - Max Touch Points:', navigator.maxTouchPoints);
    console.log('  - Languages:', navigator.languages);
    console.log('  - Webdriver:', navigator.webdriver);
    
    // 2. Screen 信息
    console.log('\\n[Screen 信息]');
    console.log('  - Width:', screen.width);
    console.log('  - Height:', screen.height);
    console.log('  - Avail Width:', screen.availWidth);
    console.log('  - Avail Height:', screen.availHeight);
    console.log('  - Color Depth:', screen.colorDepth);
    console.log('  - Pixel Depth:', screen.pixelDepth);
    
    // 3. WebGL 信息
    console.log('\\n[WebGL 信息]');
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        if (gl) {
            const vendor = gl.getParameter(gl.VENDOR);
            const renderer = gl.getParameter(gl.RENDERER);
            console.log('  - Vendor:', vendor);
            console.log('  - Renderer:', renderer);
        } else {
            console.log('  - WebGL 不可用');
        }
    } catch (e) {
        console.log('  - WebGL 检测失败:', e.message);
    }
    
    // 4. Canvas 指纹（简化版）
    console.log('\\n[Canvas 指纹]');
    try {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = 200;
        canvas.height = 50;
        ctx.textBaseline = 'top';
        ctx.font = '14px Arial';
        ctx.fillStyle = '#f60';
        ctx.fillRect(125, 1, 62, 20);
        ctx.fillStyle = '#069';
        ctx.fillText('Test 123', 2, 15);
        const dataURL = canvas.toDataURL();
        const hash = dataURL.substring(dataURL.length - 50);
        console.log('  - Canvas Hash (last 50 chars):', hash);
    } catch (e) {
        console.log('  - Canvas 检测失败:', e.message);
    }
    
    // 5. Plugins
    console.log('\\n[Plugins]');
    console.log('  - Count:', navigator.plugins.length);
    if (navigator.plugins.length > 0) {
        console.log('  - Plugins:', Array.from(navigator.plugins).map(p => p.name));
    }
    
    // 6. Chrome 对象
    console.log('\\n[Chrome 对象]');
    console.log('  - window.chrome exists:', typeof window.chrome !== 'undefined');
    if (window.chrome) {
        console.log('  - chrome.runtime:', typeof chrome.runtime);
        console.log('  - chrome.loadTimes:', typeof chrome.loadTimes);
    }
    
    // 7. Audio 指纹
    console.log('\\n[Audio 指纹]');
    try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
            console.log('  - AudioContext 可用: true');
            const ctx = new AudioContext();
            const analyser = ctx.createAnalyser();
            const oscillator = ctx.createOscillator();
            console.log('  - AudioContext 已修改（已添加噪点）');
            ctx.close();
        } else {
            console.log('  - AudioContext 不可用');
        }
    } catch (e) {
        console.log('  - Audio 检测失败:', e.message);
    }
    
    // 8. Fonts 指纹
    console.log('\\n[Fonts 指纹]');
    try {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        ctx.font = '14px Arial';
        const metrics = ctx.measureText('test');
        console.log('  - measureText 已修改（已添加随机偏移）');
        console.log('  - 测试文本宽度:', metrics.width.toFixed(2), 'px');
    } catch (e) {
        console.log('  - Fonts 检测失败:', e.message);
    }
    
    console.log('\\n========== 验证完成 ==========\\n');
    
    // 返回结果对象
    return {
        navigator: {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            hardwareConcurrency: navigator.hardwareConcurrency,
            deviceMemory: navigator.deviceMemory,
            maxTouchPoints: navigator.maxTouchPoints,
            languages: navigator.languages,
            webdriver: navigator.webdriver
        },
        screen: {
            width: screen.width,
            height: screen.height,
            availWidth: screen.availWidth,
            availHeight: screen.availHeight,
            colorDepth: screen.colorDepth
        },
        webgl: (function() {
            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                return gl ? {
                    vendor: gl.getParameter(gl.VENDOR),
                    renderer: gl.getParameter(gl.RENDERER)
                } : null;
            } catch (e) {
                return null;
            }
        })()
    };
})();
"""
        return script


class FingerprintManager:
    """指纹持久化管理器"""
    
    @staticmethod
    def save_fingerprint(fingerprint: Dict[str, Any], filepath: str):
        """
        保存指纹到文件
        
        Args:
            fingerprint: 指纹配置
            filepath: 保存路径
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(fingerprint, f, indent=2, ensure_ascii=False)
            logger.success(f"指纹已保存到: {filepath}")
        except Exception as e:
            logger.error(f"保存指纹失败: {e}")
    
    @staticmethod
    def load_fingerprint(filepath: str) -> Optional[Dict[str, Any]]:
        """
        从文件加载指纹
        
        Args:
            filepath: 文件路径
            
        Returns:
            指纹配置字典
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                fingerprint = json.load(f)
            logger.success(f"指纹已从文件加载: {filepath}")
            return fingerprint
        except Exception as e:
            logger.error(f"加载指纹失败: {e}")
            return None


class FingerprintPool:
    """指纹池 - 管理多个指纹配置"""
    
    def __init__(self, pool_size: int = 10, platform_pool: Optional[List[str]] = None):
        """
        初始化指纹池
        
        Args:
            pool_size: 池大小
            platform_pool: 平台池
        """
        self.pool: List[Dict[str, Any]] = []
        self.current_index = 0
        self._generate_pool(pool_size, platform_pool)
    
    def _generate_pool(self, size: int, platform_pool: Optional[List[str]] = None):
        """生成指纹池"""
        logger.info(f"正在生成指纹池，大小: {size}")
        for i in range(size):
            fingerprint = BrowserFingerprint.generate_random_fingerprint(platform_pool, add_noise=True)
            fingerprint['pool_index'] = i
            self.pool.append(fingerprint)
        logger.success(f"指纹池生成完成，共 {len(self.pool)} 个指纹")
    
    def get_random(self) -> Dict[str, Any]:
        """从池中随机获取一个指纹"""
        return random.choice(self.pool)
    
    def get_next(self) -> Dict[str, Any]:
        """按顺序获取下一个指纹"""
        fingerprint = self.pool[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.pool)
        return fingerprint
    
    def get_by_index(self, index: int) -> Dict[str, Any]:
        """获取特定索引的指纹"""
        return self.pool[index % len(self.pool)]
    
    def size(self) -> int:
        """获取池大小"""
        return len(self.pool)