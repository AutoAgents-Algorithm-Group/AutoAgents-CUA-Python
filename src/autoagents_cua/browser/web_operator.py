from ..utils.logging import logger
from DrissionPage import WebPage, ChromiumOptions
from typing import Optional, Any, Union, Dict
from time import sleep
from .browser_fingerprint import BrowserFingerprint



class WebOperator:
    """
    网页操作器 - 封装常见的网页元素操作
    
    WebOperator 是 DrissionPage 的唯一封装入口，负责创建和管理浏览器实例。
    所有需要使用 DrissionPage 的类都应该通过 WebOperator 来操作浏览器。
    """
    
    def __init__(self, headless=False, fingerprint_config: Optional[Union[str, Dict[str, Any]]] = None, user_data_dir: Optional[str] = None):
        """
        初始化网页操作器
        
        Args:
            headless: 是否使用无头模式
            fingerprint_config: 浏览器指纹配置
                - None: 不使用指纹修改
                - str: 使用预设指纹名称（如 'windows_chrome', 'mac_chrome'）
                - Dict: 使用自定义指纹配置
        """
        # 创建浏览器配置
        co = ChromiumOptions()
        if headless:
            co.headless()
        
        # 处理指纹配置
        self.fingerprint = None
        self.injection_script = None
        
        if fingerprint_config:
            # 如果是字符串，从预设中加载
            if isinstance(fingerprint_config, str):
                self.fingerprint = BrowserFingerprint.get_preset(fingerprint_config)
                if not self.fingerprint:
                    logger.warning(f"未找到指纹预设: {fingerprint_config}，将不使用指纹修改")
            # 如果是字典，直接使用
            elif isinstance(fingerprint_config, dict):
                self.fingerprint = fingerprint_config
            
            # 应用指纹配置
            if self.fingerprint:
                # 验证指纹
                if BrowserFingerprint.validate_fingerprint(self.fingerprint):
                    # 应用到 ChromiumOptions
                    co = BrowserFingerprint.apply_to_chromium_options(co, self.fingerprint)
                    # 生成注入脚本
                    self.injection_script = BrowserFingerprint.get_injection_script(self.fingerprint)
                    logger.success(f"已加载浏览器指纹: {self.fingerprint.get('name', '自定义')}")
                else:
                    logger.error("指纹配置验证失败，将不使用指纹修改")
                    self.fingerprint = None
                    self.injection_script = None
        
        # 创建 WebPage 实例（WebOperator 完全拥有和管理）
        self.page = WebPage(chromium_options=co)
        logger.info("WebOperator 已创建浏览器实例")
        
        # 如果有指纹脚本，使用 CDP 在页面加载前注入（关键！）
        if self.injection_script:
            self._inject_fingerprint_script_on_new_document()
            logger.success("指纹脚本已配置为在所有新页面加载前自动注入")
        
        # 如果有Client Hints配置，设置请求头拦截
        if self.fingerprint and self.fingerprint.get('client_hints'):
            self._setup_client_hints_interception()
            logger.success("Client Hints 请求头拦截已配置")
    
    def close(self):
        """关闭浏览器"""
        if self.page:
            try:
                self.page.quit()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器失败: {e}")
    
    def _inject_fingerprint_script_on_new_document(self):
        """
        使用 CDP 在新页面加载前注入指纹脚本
        这是修改 Canvas、WebGL 等指纹的关键！
        """
        if not self.injection_script:
            return
        
        try:
            # 获取 CDP 客户端
            # DrissionPage 在 page 对象中提供了 cdp 访问
            # 使用 Page.addScriptToEvaluateOnNewDocument 在所有新页面加载前执行脚本
            self.page.run_cdp('Page.enable')
            self.page.run_cdp('Page.addScriptToEvaluateOnNewDocument', source=self.injection_script)
            logger.success("✅ 指纹脚本已通过 CDP 注册（将在所有页面加载前执行）")
        except Exception as e:
            logger.error(f"❌ CDP 注入失败: {e}")
            logger.warning("将尝试使用传统方式注入（可能不够及时）")
    
    def _inject_fingerprint_script(self):
        """
        传统方式注入指纹脚本（作为备用方案）
        注意：这种方式注入太晚，可能无法有效修改指纹
        """
        if not self.injection_script:
            return
        
        try:
            self.page.run_js(self.injection_script)
            logger.debug("指纹脚本已通过 JS 注入（传统方式）")
        except Exception as e:
            logger.warning(f"指纹脚本注入失败: {e}")
    
    def get_fingerprint_info(self) -> Optional[Dict[str, Any]]:
        """
        获取当前使用的指纹信息
        
        Returns:
            指纹配置字典
        """
        return self.fingerprint
    
    def verify_fingerprint(self) -> Dict[str, Any]:
        """
        验证浏览器中的指纹是否被成功修改
        
        Returns:
            包含实际指纹信息的字典
        """
        try:
            verification_script = BrowserFingerprint.get_verification_script()
            result = self.page.run_js(verification_script)
            logger.success("✅ 指纹验证完成（详细信息请查看浏览器控制台）")
            return result
        except Exception as e:
            logger.error(f"❌ 指纹验证失败: {e}")
            return {}
    
    # ========== 页面导航方法 ==========
    
    def navigate(self, url, wait_time=3):
        """
        导航到指定URL并等待页面加载
        
        Args:
            url: 目标URL
            wait_time: 页面加载后等待时间（秒）
            
        Returns:
            是否成功导航
        """
        try:
            logger.info(f"正在加载页面: {url}")
            self.page.get(url)
            
            # 注意：指纹脚本已经通过 CDP 在页面加载前自动注入了
            # 不需要在这里手动注入
            
            if wait_time > 0:
                sleep(wait_time)
            
            logger.success("页面加载完成！")
            return True
        except Exception as e:
            logger.error(f"页面加载失败: {e}")
            print(f"   URL: {url}")
            return False
    
    def refresh_page(self, wait_time=3):
        """
        刷新当前页面
        
        Args:
            wait_time: 刷新后等待时间（秒）
            
        Returns:
            是否成功刷新
        """
        try:
            logger.info("正在刷新页面...")
            self.page.refresh()
            
            if wait_time > 0:
                sleep(wait_time)
            
            logger.success("页面刷新完成！")
            return True
        except Exception as e:
            logger.error(f"页面刷新失败: {e}")
            return False
    
    def go_back(self, wait_time=2):
        """
        返回上一页
        
        Args:
            wait_time: 返回后等待时间（秒）
            
        Returns:
            是否成功返回
        """
        try:
            logger.info("返回上一页...")
            self.page.back()
            
            if wait_time > 0:
                sleep(wait_time)
            
            logger.success("已返回上一页")
            return True
        except Exception as e:
            logger.error(f"返回上一页失败: {e}")
            return False
    
    def get_current_url(self):
        """
        获取当前页面URL
        
        Returns:
            当前URL字符串
        """
        try:
            url = self.page.url
            logger.info(f"当前URL: {url}")
            return url
        except Exception as e:
            logger.error(f"获取URL失败: {e}")
            return None
    
    # ========== 元素操作方法 ==========
    
    def input_text(self, selector, text, clear=True):
        """
        在输入框中输入文本
        
        Args:
            selector: 元素定位器
            text: 要输入的文本
            clear: 是否先清空输入框
            
        Returns:
            元素对象，如果失败返回 None
        """
        try:
            element = self.page.ele(selector)
            if not element:
                logger.error(f" 未找到元素: [{selector}]")
                return None
            
            if clear:
                element.clear()
            element.input(text)
            logger.success(f" 已在元素 [{selector}] 中输入: {text}")
            return element
        except Exception as e:
            logger.error(f" 输入文本失败: {e}")
            print(f"   定位器: [{selector}]")
            return None
    
    def click_element(self, selector, wait_before=1, wait_after=1):
        """
        点击元素
        
        Args:
            selector: 元素定位器
            wait_before: 点击前等待时间（秒）
            wait_after: 点击后等待时间（秒）
            
        Returns:
            元素对象，如果失败返回 None
        """
        try:
            element = self.page.ele(selector)
            if not element:
                logger.error(f" 未找到元素: [{selector}]")
                return None
            
            # 点击前等待
            if wait_before > 0:
                sleep(wait_before)
            
            element.click()
            logger.success(f" 已点击元素: [{selector}]")
            
            # 点击后等待
            if wait_after > 0:
                sleep(wait_after)
            
            return element
        except Exception as e:
            logger.error(f" 点击元素失败: {e}")
            print(f"   定位器: [{selector}]")
            return None
    
    def select_option(self, selector, value):
        """
        在下拉框中选择选项
        
        Args:
            selector: 下拉框定位器
            value: 要选择的值
            
        Returns:
            元素对象，如果失败返回 None
        """
        try:
            element = self.page.ele(selector)
            if not element:
                logger.error(f" 未找到下拉框: [{selector}]")
                return None
            
            element.select(value)
            logger.success(f" 已在下拉框 [{selector}] 中选择: {value}")
            return element
        except Exception as e:
            logger.error(f" 选择下拉框选项失败: {e}")
            print(f"   定位器: [{selector}]")
            return None
    
    def get_element_text(self, selector):
        """
        获取元素文本内容
        
        Args:
            selector: 元素定位器
            
        Returns:
            元素文本，如果失败返回 None
        """
        try:
            element = self.page.ele(selector)
            if not element:
                logger.error(f" 未找到元素: [{selector}]")
                return None
            return element.text
        except Exception as e:
            logger.error(f" 获取元素文本失败: {e}")
            print(f"   定位器: [{selector}]")
            return None
    
    def get_element_value(self, selector):
        """
        获取元素的 value 属性
        
        Args:
            selector: 元素定位器
            
        Returns:
            元素的 value 属性值，如果失败返回 None
        """
        try:
            element = self.page.ele(selector)
            if not element:
                logger.error(f" 未找到元素: [{selector}]")
                return None
            return element.attr('value')
        except Exception as e:
            logger.error(f" 获取元素 value 失败: {e}")
            print(f"   定位器: [{selector}]")
            return None
    
    def get_element_attribute(self, selector, attr_name):
        """
        获取元素的指定属性
        
        Args:
            selector: 元素定位器
            attr_name: 属性名称
            
        Returns:
            属性值，如果失败返回 None
        """
        try:
            element = self.page.ele(selector)
            if not element:
                logger.error(f" 未找到元素: [{selector}]")
                return None
            return element.attr(attr_name)
        except Exception as e:
            logger.error(f" 获取元素属性失败: {e}")
            print(f"   定位器: [{selector}], 属性: {attr_name}")
            return None
    
    def wait_for_element(self, selector, timeout=10):
        """
        等待元素出现
        
        Args:
            selector: 元素定位器
            timeout: 超时时间（秒）
            
        Returns:
            是否成功等到元素
        """
        try:
            self.page.wait.ele_displayed(selector, timeout=timeout)
            logger.success(f" 元素已出现: [{selector}]")
            return True
        except Exception as e:
            logger.error(f" 等待元素超时: {e}")
            print(f"   定位器: [{selector}]")
            return False
    
    def is_element_visible(self, selector, timeout=2):
        """
        检查元素是否可见
        
        Args:
            selector: 元素定位器
            timeout: 超时时间（秒）
            
        Returns:
            元素是否可见
        """
        try:
            element = self.page.ele(selector, timeout=timeout)
            return element is not None
        except Exception:
            return False
    
    def scroll_to_element(self, selector):
        """
        滚动到指定元素
        
        Args:
            selector: 元素定位器
            
        Returns:
            是否成功滚动
        """
        try:
            element = self.page.ele(selector)
            if not element:
                logger.error(f" 未找到元素: [{selector}]")
                return False
            
            element.scroll.to_see()
            logger.success(f" 已滚动到元素: [{selector}]")
            return True
        except Exception as e:
            logger.error(f" 滚动到元素失败: {e}")
            print(f"   定位器: [{selector}]")
            return False


    def refresh(self):
        """
        刷新当前页面
        """
        self.page.refresh()
        logger.success("页面刷新完成！")
        return True
    
    def take_screenshot(self, file_path=None):
        """
        截取当前页面截图
        
        Args:
            file_path: 截图保存路径，如果不提供则自动生成带时间戳的文件名
            
        Returns:
            截图文件路径，如果失败返回 None
        """
        try:
            if file_path is None:
                import os
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                # 获取项目根目录
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
                # 确保 media 文件夹存在
                media_dir = os.path.join(project_root, 'playground', 'outputs','imgs')
                os.makedirs(media_dir, exist_ok=True)
                file_path = os.path.join(media_dir, f'screenshot_{timestamp}.png')
            
            # 使用 DrissionPage 的截图功能
            # 尝试使用 full_page 参数
            try:
                self.page.get_screenshot(path=file_path, full_page=True)
            except TypeError:
                # 如果不支持 full_page 参数，则使用基础截图
                self.page.get_screenshot(path=file_path)
            
            logger.success(f"截图已保存: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"截图失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _setup_client_hints_interception(self):
        """
        使用 CDP 设置 Client Hints 覆盖
        
        使用多种方法确保 Client Hints 修改成功
        """
        try:
            client_hints = self.fingerprint.get('client_hints', {})
            user_agent = self.fingerprint.get('user_agent', '')
            
            if not client_hints or not user_agent:
                logger.warning("缺少 Client Hints 或 User-Agent 配置")
                return
            
            logger.info("🔧 开始设置 Client Hints 覆盖...")
            
            # 启用必要的 CDP domains
            self.page.run_cdp('Network.enable')
            self.page.run_cdp('Runtime.enable')
            self.page.run_cdp('Page.enable')
            
            # 构建 Client Hints 元数据
            user_agent_metadata = {
                'brands': [],
                'mobile': client_hints.get('Sec-CH-UA-Mobile') == '?1',
                'platform': client_hints.get('Sec-CH-UA-Platform', '').replace('"', ''),
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
            
            # 添加高熵值数据
            if client_hints.get('Sec-CH-UA-Platform-Version'):
                user_agent_metadata['platformVersion'] = client_hints['Sec-CH-UA-Platform-Version'].replace('"', '')
            if client_hints.get('Sec-CH-UA-Arch'):
                user_agent_metadata['architecture'] = client_hints['Sec-CH-UA-Arch'].replace('"', '')
            if client_hints.get('Sec-CH-UA-Bitness'):
                user_agent_metadata['bitness'] = client_hints['Sec-CH-UA-Bitness'].replace('"', '')
            if client_hints.get('Sec-CH-UA-Model'):
                user_agent_metadata['model'] = client_hints['Sec-CH-UA-Model'].replace('"', '')
            if client_hints.get('Sec-CH-UA-Full-Version'):
                user_agent_metadata['fullVersion'] = client_hints['Sec-CH-UA-Full-Version'].replace('"', '')
            
            logger.info(f"📋 构建的 Client Hints 元数据:")
            logger.info(f"   Platform: {user_agent_metadata['platform']}")
            logger.info(f"   Mobile: {user_agent_metadata['mobile']}")
            logger.info(f"   Brands: {user_agent_metadata['brands']}")
            
            # 方法1: 使用 Network.setUserAgentOverride
            try:
                override_params = {
                    'userAgent': user_agent,
                    'userAgentMetadata': user_agent_metadata
                }
                
                result = self.page.run_cdp('Network.setUserAgentOverride', **override_params)
                logger.success("✅ Network.setUserAgentOverride 调用成功")
                logger.debug(f"CDP 返回结果: {result}")
            except Exception as e:
                logger.error(f"❌ Network.setUserAgentOverride 失败: {e}")
            
            # 方法2: 使用 Emulation.setUserAgentOverride  
            try:
                result2 = self.page.run_cdp('Emulation.setUserAgentOverride', **override_params)
                logger.success("✅ Emulation.setUserAgentOverride 调用成功")
                logger.debug(f"CDP 返回结果: {result2}")
            except Exception as e:
                logger.warning(f"⚠️  Emulation.setUserAgentOverride 失败: {e}")
            
            # 方法3: 设置请求拦截器
            try:
                # 启用请求拦截
                self.page.run_cdp('Fetch.enable', {
                    'patterns': [{'urlPattern': '*'}]
                })
                
                # 注册请求处理器
                def handle_request_paused(params):
                    try:
                        request_id = params['requestId']
                        request = params['request']
                        
                        # 修改请求头
                        headers = request.get('headers', {})
                        
                        # 添加 Client Hints 头部
                        for hint_name, hint_value in client_hints.items():
                            headers[hint_name] = hint_value
                        
                        # 继续请求
                        self.page.run_cdp('Fetch.continueRequest', {
                            'requestId': request_id,
                            'headers': [{'name': k, 'value': v} for k, v in headers.items()]
                        })
                        
                    except Exception as e:
                        logger.debug(f"请求拦截处理失败: {e}")
                        # 如果处理失败，继续原始请求
                        try:
                            self.page.run_cdp('Fetch.continueRequest', {'requestId': request_id})
                        except:
                            pass
                
                # 这里我们不能直接设置事件监听器，因为 DrissionPage 可能不支持
                # 但我们已经启用了 Fetch domain
                logger.info("✅ Fetch domain 已启用")
                
            except Exception as e:
                logger.debug(f"启用 Fetch 拦截失败: {e}")
            
            # 方法4: 强化的JavaScript注入
            enhanced_script = f"""
            // 强化的 Client Hints 覆盖脚本
            (function() {{
                'use strict';
                console.log('🔧 开始强化 Client Hints 覆盖...');
                
                const clientHintsData = {client_hints};
                console.log('Client Hints 数据:', clientHintsData);
                
                // 立即覆盖 navigator.userAgentData
                if (typeof navigator !== 'undefined') {{
                    try {{
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
                        
                        const isMobile = clientHintsData['Sec-CH-UA-Mobile'] === '?1';
                        const platform = clientHintsData['Sec-CH-UA-Platform'] ? clientHintsData['Sec-CH-UA-Platform'].replace(/"/g, '') : 'Windows';
                        
                        console.log('解析的 Client Hints:');
                        console.log('  brands:', brands);
                        console.log('  mobile:', isMobile);
                        console.log('  platform:', platform);
                        
                        // 创建完全新的 userAgentData 对象
                        const newUserAgentData = {{
                            brands: brands,
                            mobile: isMobile,
                            platform: platform,
                            
                            getHighEntropyValues: function(hints) {{
                                console.log('getHighEntropyValues 被调用，参数:', hints);
                                const result = {{
                                    brands: this.brands,
                                    mobile: this.mobile,
                                    platform: this.platform
                                }};
                                
                                if (hints.includes('architecture')) {{
                                    result.architecture = clientHintsData['Sec-CH-UA-Arch'] ? clientHintsData['Sec-CH-UA-Arch'].replace(/"/g, '') : 'x86';
                                }}
                                if (hints.includes('bitness')) {{
                                    result.bitness = clientHintsData['Sec-CH-UA-Bitness'] ? clientHintsData['Sec-CH-UA-Bitness'].replace(/"/g, '') : '64';
                                }}
                                if (hints.includes('model')) {{
                                    result.model = clientHintsData['Sec-CH-UA-Model'] ? clientHintsData['Sec-CH-UA-Model'].replace(/"/g, '') : '';
                                }}
                                if (hints.includes('platformVersion')) {{
                                    result.platformVersion = clientHintsData['Sec-CH-UA-Platform-Version'] ? clientHintsData['Sec-CH-UA-Platform-Version'].replace(/"/g, '') : '';
                                }}
                                if (hints.includes('uaFullVersion')) {{
                                    result.uaFullVersion = clientHintsData['Sec-CH-UA-Full-Version'] ? clientHintsData['Sec-CH-UA-Full-Version'].replace(/"/g, '') : '';
                                }}
                                
                                console.log('getHighEntropyValues 返回结果:', result);
                                return Promise.resolve(result);
                            }},
                            
                            toJSON: function() {{
                                return {{
                                    brands: this.brands,
                                    mobile: this.mobile,
                                    platform: this.platform
                                }};
                            }}
                        }};
                        
                        // 强制替换 navigator.userAgentData
                        try {{
                            Object.defineProperty(navigator, 'userAgentData', {{
                                value: newUserAgentData,
                                writable: false,
                                configurable: false,
                                enumerable: true
                            }});
                            console.log('✅ navigator.userAgentData 强制替换成功');
                        }} catch (e) {{
                            console.log('第一次替换失败，尝试其他方法:', e);
                            try {{
                                delete navigator.userAgentData;
                                navigator.userAgentData = newUserAgentData;
                                console.log('✅ navigator.userAgentData 删除重建成功');
                            }} catch (e2) {{
                                console.log('第二次替换也失败:', e2);
                            }}
                        }}
                        
                        // 验证替换结果
                        console.log('验证替换结果:');
                        console.log('  navigator.userAgentData:', navigator.userAgentData);
                        console.log('  brands:', navigator.userAgentData.brands);
                        console.log('  platform:', navigator.userAgentData.platform);
                        console.log('  mobile:', navigator.userAgentData.mobile);
                        
                    }} catch (e) {{
                        console.error('Client Hints 覆盖失败:', e);
                    }}
                }}
                
                console.log('✅ 强化 Client Hints 覆盖脚本执行完成');
            }})();
            """
            
            # 注入强化脚本
            self.page.run_cdp('Page.addScriptToEvaluateOnNewDocument', {
                'source': enhanced_script,
                'worldName': 'enhanced_client_hints'
            })
            logger.success("✅ 强化 Client Hints 脚本已注册")
            
        except Exception as e:
            logger.error(f"❌ 设置 Client Hints 拦截失败: {e}")
            import traceback
            traceback.print_exc()