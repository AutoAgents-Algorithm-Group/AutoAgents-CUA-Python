#!/usr/bin/env python3
"""
TikTok Manager - TikTok应用自动化管理器

基于 MobileDevice 的高层封装，提供TikTok特定的操作功能。
"""

import time
from typing import Dict, Tuple, List, Optional

from ..agent.mobile_agent import MobileDevice
from ..utils.logging import logger


class TikTokManager:
    """TikTok应用管理器 - 封装TikTok特定的自动化操作"""
    
    # TikTok应用包名
    PACKAGE_NAME = "com.zhiliaoapp.musically"
    
    def __init__(self, device_address: str = "127.0.0.1:5555"):
        """
        初始化TikTok管理器
        
        Args:
            device_address: 设备地址，默认为本地模拟器
        """
        self.device = MobileDevice(device_address)
    
    @property
    def is_connected(self) -> bool:
        """设备是否已连接"""
        return self.device.is_connected
    
    def start_app(self) -> bool:
        """启动TikTok应用"""
        return self.device.start_app(self.PACKAGE_NAME)
    
    def stop_app(self) -> bool:
        """停止TikTok应用"""
        return self.device.stop_app(self.PACKAGE_NAME)
    
    def handle_popups(self) -> bool:
        """处理各种弹窗"""
        try:
            logger.info("检查并处理弹窗...")
            handled_any = False
            
            # 处理隐私政策弹窗
            privacy_buttons = ["同意并继续", "同意", "继续", "确定"]
            for button_text in privacy_buttons:
                if self.device.click_element(text=button_text, timeout=2):
                    logger.info(f"处理隐私政策弹窗: 点击了'{button_text}'")
                    time.sleep(2)
                    handled_any = True
                    break
            
            # 处理"知道了"弹窗
            knowledge_buttons = ["知道了", "了解", "我知道了"]
            for button_text in knowledge_buttons:
                if self.device.click_element(text=button_text, timeout=2):
                    logger.info(f"处理信息弹窗: 点击了'{button_text}'")
                    time.sleep(2)
                    handled_any = True
                    break
            
            # 处理其他可能的弹窗
            other_buttons = ["关闭", "跳过", "稍后", "取消"]
            for button_text in other_buttons:
                if self.device.click_element(text=button_text, timeout=1):
                    logger.info(f"处理其他弹窗: 点击了'{button_text}'")
                    time.sleep(1)
                    handled_any = True
                    break
            
            if not handled_any:
                logger.info("未发现弹窗")
            
            return True
            
        except Exception as e:
            logger.error(f"处理弹窗时出错: {e}")
            return False
    
    def handle_video_rating_popup(self) -> bool:
        """处理视频评价弹窗，选择'不喜欢也不反感'选项"""
        try:
            # 检查是否存在评价弹窗
            rating_popup_texts = [
                "如何评价刚刚观看过的视频",
                "如何评价刚刚观看过的视频？",
                "评价视频",
                "对这个视频的感受"
            ]
            
            popup_found = False
            for popup_text in rating_popup_texts:
                if self.device.find_element(text_contains=popup_text, timeout=1):
                    logger.info(f"发现视频评价弹窗: {popup_text}")
                    popup_found = True
                    break
            
            if not popup_found:
                return False  # 没有发现评价弹窗
            
            # 查找并点击"不喜欢也不反感"选项
            neutral_options = [
                "不喜欢也不反感",
                "一般",
                "无感",
                "不好也不坏"
            ]
            
            option_clicked = False
            for option_text in neutral_options:
                if self.device.click_element(text=option_text, timeout=2):
                    logger.info(f"已选择评价选项: '{option_text}'")
                    option_clicked = True
                    time.sleep(1)
                    break
                elif self.device.click_element(text_contains=option_text, timeout=2):
                    logger.info(f"已选择评价选项: '{option_text}'")
                    option_clicked = True
                    time.sleep(1)
                    break
            
            if not option_clicked:
                logger.warning("未找到'不喜欢也不反感'选项，尝试点击中间选项...")
                # 如果找不到具体文本，尝试点击可能的中间位置
                text_views = self.device.device(className="android.widget.TextView", clickable=True)
                if text_views.count > 2:
                    middle_index = text_views.count // 2
                    try:
                        middle_option = text_views[middle_index]
                        if middle_option.exists:
                            middle_option.click()
                            logger.info("已点击中间选项作为备选")
                            option_clicked = True
                            time.sleep(1)
                    except:
                        pass
            
            # 查找并点击提交按钮
            if option_clicked:
                submit_buttons = ["提交", "确定", "完成", "OK"]
                for submit_text in submit_buttons:
                    if self.device.click_element(text=submit_text, timeout=2):
                        logger.info(f"已提交评价: 点击了'{submit_text}'")
                        time.sleep(1)
                        break
                
                logger.info("视频评价弹窗处理完成")
                return True
            else:
                logger.error("未能选择评价选项")
                return False
                
        except Exception as e:
            logger.error(f"处理视频评价弹窗时出错: {e}")
            return False
    
    def check_login_required(self) -> bool:
        """检查是否需要登录"""
        try:
            logger.info("检查登录状态...")
            
            # 检查是否在登录页面
            login_indicators = [
                "登录 TikTok",
                "使用手机号码/电子邮箱/用户名登录",
                "使用 Facebook 登录",
                "使用 Google 登录",
                "手机号码",
                "邮箱/用户名"
            ]
            
            for indicator in login_indicators:
                if self.device.find_element(text_contains=indicator, timeout=2):
                    logger.warning(f"发现登录页面: {indicator}")
                    return True
            
            logger.info("已登录状态")
            return False
            
        except Exception as e:
            logger.error(f"检查登录状态时出错: {e}")
            return False
    
    def is_video_page(self) -> bool:
        """检查是否在视频页面"""
        try:
            # 检查视频页面的特征元素
            video_indicators = ["推荐", "关注", "LIVE", "STEM", "探索", "商城"]
            
            indicator_count = 0
            for indicator in video_indicators:
                if self.device.find_element(text=indicator, timeout=1):
                    indicator_count += 1
            
            # 如果找到2个或以上指示器，认为在视频页面
            return indicator_count >= 2
            
        except Exception as e:
            logger.error(f"检查视频页面时出错: {e}")
            return False
    
    def is_live_room(self) -> bool:
        """检测是否在直播间"""
        try:
            # 检查直播间的特征元素
            live_indicators = [
                "直播中", "点击进入直播间", "LIVE",
                "直播", "观看直播", "进入直播间"
            ]
            
            for indicator in live_indicators:
                if self.device.find_element(text=indicator, timeout=1):
                    logger.info(f"检测到直播间标识: {indicator}")
                    return True
            
            # 检查直播间特有的UI元素
            live_ui_indicators = [
                "com.zhiliaoapp.musically:id/live_room",
                "com.zhiliaoapp.musically:id/live_indicator",
                "com.zhiliaoapp.musically:id/live_badge"
            ]
            
            for resource_id in live_ui_indicators:
                if self.device.find_element(resource_id=resource_id, timeout=1):
                    logger.info(f"检测到直播间UI元素: {resource_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"检测直播间时出错: {e}")
            return False
    
    def get_current_video_info(self) -> Dict:
        """获取当前视频的信息用于对比"""
        try:
            info = {}
            
            # 尝试获取当前可见的文本信息
            try:
                text_views = self.device.device(className="android.widget.TextView")
                visible_texts = []
                for tv in text_views:
                    if tv.exists:
                        text = tv.get_text()
                        if text and len(text.strip()) > 0:
                            visible_texts.append(text.strip())
                
                info['texts'] = visible_texts[:10]  # 只保留前10个文本
            except:
                info['texts'] = []
            
            # 获取屏幕截图的哈希值
            info['screenshot_hash'] = self.device.get_screenshot_hash()
            
            return info
            
        except Exception as e:
            logger.error(f"获取视频信息时出错: {e}")
            return {}
    
    def scroll_to_next_video(self, force_level: str = "strong") -> bool:
        """
        使用滚轮向下滚动切换到下一个视频
        
        Args:
            force_level: 滑动力度级别 ("light", "medium", "strong", "ultra")
        """
        try:
            logger.info(f"使用{force_level}力度滚动切换视频...")
            
            # 获取滚动前的视频信息
            before_info = self.get_current_video_info()
            logger.debug(f"滚动前视频信息: {before_info.get('screenshot_hash', 'N/A')}")
            
            # 根据力度级别设置参数
            force_params = {
                "light": (0.65, 0.35, 0.4, 1),
                "medium": (0.75, 0.25, 0.3, 1),
                "strong": (0.8, 0.15, 0.2, 1),
                "ultra": (0.85, 0.1, 0.15, 1)
            }
            start_ratio, end_ratio, duration, repeat_count = force_params.get(
                force_level, force_params["strong"]
            )
            
            # 执行滑动
            screen_width = self.device.screen_width
            screen_height = self.device.screen_height
            center_x = screen_width // 2
            start_y = int(screen_height * start_ratio)
            end_y = int(screen_height * end_ratio)
            
            for i in range(repeat_count):
                self.device.swipe(center_x, start_y, center_x, end_y, duration=duration)
                if repeat_count > 1:
                    time.sleep(0.1)
            
            logger.debug(
                f"执行{force_level}力度滑动: ({center_x}, {start_y}) → "
                f"({center_x}, {end_y}), 重复{repeat_count}次"
            )
            
            # 等待视频加载
            time.sleep(2)
            
            # 获取滚动后的视频信息
            after_info = self.get_current_video_info()
            logger.debug(f"滚动后视频信息: {after_info.get('screenshot_hash', 'N/A')}")
            
            # 检查是否切换了视频
            video_changed = self._check_video_changed(before_info, after_info)
            
            if video_changed:
                logger.info("成功切换到下一个视频！")
                
                # 检查并处理视频评价弹窗
                time.sleep(1)
                self.handle_video_rating_popup()
                
                return True
            else:
                logger.warning("可能没有切换到新视频")
                return False
                
        except Exception as e:
            logger.error(f"滚动操作失败: {e}")
            return False
    
    def _check_video_changed(self, before_info: Dict, after_info: Dict) -> bool:
        """检查视频是否发生了变化"""
        try:
            # 方法1: 比较截图哈希
            before_hash = before_info.get('screenshot_hash')
            after_hash = after_info.get('screenshot_hash')
            if before_hash and after_hash and before_hash != after_hash:
                logger.debug("检测到视频内容变化（截图哈希不同）")
                return True
            
            # 方法2: 比较可见文本
            before_texts = set(before_info.get('texts', []))
            after_texts = set(after_info.get('texts', []))
            
            if len(before_texts) > 0 and len(after_texts) > 0:
                common_texts = before_texts.intersection(after_texts)
                total_texts = before_texts.union(after_texts)
                
                if len(total_texts) > 0:
                    similarity = len(common_texts) / len(total_texts)
                    logger.debug(f"文本相似度: {similarity:.2f}")
                    if similarity < 0.5:  # 相似度低于50%认为是不同视频
                        logger.debug("检测到视频内容变化（文本差异显著）")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查视频变化时出错: {e}")
            return False
    
    def click_creator_avatar(self) -> bool:
        """点击创作者头像"""
        try:
            logger.info("开始查找创作者头像...")
            
            # 通过ImageView位置分析查找头像
            image_views = self.device.device(className="android.widget.ImageView")
            if image_views.exists:
                logger.debug(f"找到 {len(image_views)} 个ImageView元素")
                
                # 查找右侧的ImageView（头像通常在右侧）
                for i, img in enumerate(image_views):
                    if img.exists:
                        try:
                            bounds = img.info.get('bounds', {})
                            if bounds:
                                img_left = bounds.get('left', 0)
                                img_right = bounds.get('right', 0)
                                img_top = bounds.get('top', 0)
                                img_bottom = bounds.get('bottom', 0)
                                img_center_x = (img_left + img_right) // 2
                                img_center_y = (img_top + img_bottom) // 2
                                img_width = img_right - img_left
                                img_height = img_bottom - img_top
                                
                                # 判断是否在右侧区域且大小合适
                                is_right_side = img_center_x > self.device.screen_width * 0.75
                                is_middle_vertical = (
                                    self.device.screen_height * 0.3 < img_center_y 
                                    < self.device.screen_height * 0.85
                                )
                                is_avatar_size = 40 < img_width < 150 and 40 < img_height < 150
                                is_square_like = abs(img_width - img_height) < 30
                                
                                if (is_right_side and is_middle_vertical 
                                    and is_avatar_size and is_square_like):
                                    logger.debug(
                                        f"找到头像候选: 位置({img_center_x}, {img_center_y}) "
                                        f"大小({img_width}x{img_height})"
                                    )
                                    img.click()
                                    logger.info("已点击创作者头像")
                                    return True
                                
                        except Exception as e:
                            logger.debug(f"分析ImageView {i} 时出错: {e}")
                            continue
            else:
                logger.error("未找到ImageView元素")
            
            return False
            
        except Exception as e:
            logger.error(f"点击创作者头像时出错: {e}")
            return False
    
    def click_message_button(self) -> bool:
        """点击消息按钮"""
        try:
            logger.info("开始查找消息按钮...")
            time.sleep(2)  # 等待页面加载
            
            # 方法1: 通过文本查找"消息"按钮
            if self.device.click_element(text="消息", timeout=5):
                logger.info("通过文本找到并点击了'消息'按钮")
                return True
            elif self.device.click_element(text_contains="消息", timeout=3):
                logger.info("通过包含文本找到并点击了'消息'按钮")
                return True
            
            # 方法2: 通过可能的resourceId查找
            possible_message_ids = [
                "com.zhiliaoapp.musically:id/message",
                "com.zhiliaoapp.musically:id/message_btn",
                "com.zhiliaoapp.musically:id/chat_button",
                "com.zhiliaoapp.musically:id/dm_button"
            ]
            
            for resource_id in possible_message_ids:
                if self.device.click_element(resource_id=resource_id, timeout=2):
                    logger.info(f"通过resourceId找到并点击了消息按钮: {resource_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"点击消息按钮时出错: {e}")
            return False
    
    def click_back_button(self) -> bool:
        """通过ImageView元素点击左上角返回按钮"""
        try:
            logger.info("点击左上角返回按钮...")
            
            # 通过ImageView位置分析查找返回按钮
            image_views = self.device.device(className="android.widget.ImageView")
            if image_views.exists:
                logger.debug(f"找到 {len(image_views)} 个ImageView元素")
                
                # 查找左上角的ImageView（返回按钮通常在左上角）
                for i, img in enumerate(image_views):
                    if img.exists:
                        try:
                            bounds = img.info.get('bounds', {})
                            if bounds:
                                img_left = bounds.get('left', 0)
                                img_right = bounds.get('right', 0)
                                img_top = bounds.get('top', 0)
                                img_bottom = bounds.get('bottom', 0)
                                img_center_x = (img_left + img_right) // 2
                                img_center_y = (img_top + img_bottom) // 2
                                img_width = img_right - img_left
                                img_height = img_bottom - img_top
                                
                                # 判断是否在左上角区域且大小合适
                                is_left_side = img_center_x < self.device.screen_width * 0.25
                                is_top_area = img_center_y < self.device.screen_height * 0.15
                                is_button_size = 20 < img_width < 100 and 20 < img_height < 100
                                is_square_like = abs(img_width - img_height) < 40
                                is_not_status_bar = img_center_y > self.device.screen_height * 0.05
                                
                                if (is_left_side and is_top_area and is_button_size 
                                    and is_square_like and is_not_status_bar):
                                    logger.debug(
                                        f"找到返回按钮候选: 位置({img_center_x}, {img_center_y}) "
                                        f"大小({img_width}x{img_height})"
                                    )
                                    img.click()
                                    logger.info("已点击返回按钮")
                                    time.sleep(1)
                                    return True
                                
                        except Exception as e:
                            logger.debug(f"分析ImageView {i} 时出错: {e}")
                            continue
            
            # 备选方案1: 通过常见的返回按钮resourceId查找
            logger.warning("ImageView方法未找到返回按钮，尝试备选方案...")
            possible_back_ids = [
                "com.zhiliaoapp.musically:id/back",
                "com.zhiliaoapp.musically:id/back_btn",
                "com.zhiliaoapp.musically:id/navigation_back",
                "com.zhiliaoapp.musically:id/toolbar_back",
                "android:id/home"
            ]
            
            for resource_id in possible_back_ids:
                if self.device.click_element(resource_id=resource_id, timeout=1):
                    logger.info(f"通过resourceId找到并点击了返回按钮: {resource_id}")
                    time.sleep(1)
                    return True
            
            # 备选方案2: 直接点击左上角位置
            back_x = int(self.device.screen_width * 0.08)
            back_y = int(self.device.screen_height * 0.08)
            self.device.click(back_x, back_y)
            logger.info(f"直接点击左上角位置: ({back_x}, {back_y})")
            time.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"点击返回按钮时出错: {e}")
            return False
    
    def test_multiple_scrolls(
        self, 
        scroll_count: int = 3, 
        force_level: str = "strong"
    ) -> Tuple[int, int]:
        """测试多次滚动"""
        logger.info(f"开始测试连续滚动 {scroll_count} 次 (力度: {force_level})...")
        
        successful_scrolls = 0
        
        for i in range(scroll_count):
            logger.info(f"--- 第 {i+1} 次滚动 ---")
            
            if self.scroll_to_next_video(force_level=force_level):
                successful_scrolls += 1
                logger.info(f"第 {i+1} 次滚动成功")
            else:
                logger.warning(f"第 {i+1} 次滚动失败")
            
            # 每次滚动后等待一下
            time.sleep(1)
        
        logger.info(f"滚动测试结果: {successful_scrolls}/{scroll_count} 次成功")
        return successful_scrolls, scroll_count
    
    def run_cycle_operation(self) -> Dict[str, bool]:
        """
        执行一次完整的循环操作：点击头像 -> 点击私信 -> 返回 -> 返回 -> 向下滚轮
        
        Returns:
            Dict: 包含执行结果的字典
                - success: 操作是否成功
                - is_live_room: 是否跳过了直播间
        """
        try:
            logger.info("执行一次循环操作...")
            
            # 首先检测是否是直播间
            if self.is_live_room():
                logger.info("检测到直播间，直接跳过此视频")
                if self.scroll_to_next_video(force_level="ultra"):
                    logger.info("已跳过直播间")
                    return {'success': True, 'is_live_room': True}
                else:
                    logger.warning("跳过直播间时滑动失败")
                    return {'success': False, 'is_live_room': True}
            
            # 步骤1: 点击头像
            logger.info("1️⃣ 点击创作者头像...")
            if not self.click_creator_avatar():
                logger.error("点击头像失败，跳过此次循环")
                return {'success': False, 'is_live_room': False}
            
            time.sleep(2)
            
            # 步骤2: 点击私信
            logger.info("2️⃣ 点击私信按钮...")
            if not self.click_message_button():
                logger.error("点击私信失败，尝试返回...")
                self.click_back_button()
                return {'success': False, 'is_live_room': False}
            
            time.sleep(2)
            
            # 步骤3: 第一次返回（从聊天页面返回到个人主页）
            logger.info("3️⃣ 第一次返回...")
            if not self.click_back_button():
                logger.warning("第一次返回可能失败")
            
            time.sleep(1)
            
            # 步骤4: 第二次返回（从个人主页返回到视频页面）
            logger.info("4️⃣ 第二次返回...")
            if not self.click_back_button():
                logger.warning("第二次返回可能失败")
            
            time.sleep(2)
            
            # 步骤5: 向下滚轮切换视频（使用强力滑动）
            logger.info("5️⃣ 向下滚轮切换视频...")
            if not self.scroll_to_next_video(force_level="ultra"):
                logger.warning("滚轮切换视频可能失败")
            
            time.sleep(1)
            
            logger.info("一次循环操作完成")
            return {'success': True, 'is_live_room': False}
            
        except Exception as e:
            logger.error(f"循环操作过程中出错: {e}")
            return {'success': False, 'is_live_room': False}
    
    def run_continuous_cycle(
        self, 
        cycle_count: int = 10, 
        max_errors: int = 3
    ) -> Dict[str, int]:
        """
        持续运行循环操作
        
        Args:
            cycle_count: 要执行的循环次数，-1表示无限循环
            max_errors: 最大连续错误次数，超过则停止
        
        Returns:
            Dict: 包含成功次数、失败次数、总次数的统计
        """
        logger.info(f"开始持续循环操作 (目标: {cycle_count if cycle_count > 0 else '无限'} 次)")
        logger.info("=" * 60)
        
        stats = {
            'successful_cycles': 0,
            'failed_cycles': 0,
            'total_cycles': 0,
            'consecutive_errors': 0,
            'live_rooms_skipped': 0
        }
        
        try:
            cycle_num = 0
            while True:
                cycle_num += 1
                stats['total_cycles'] = cycle_num
                
                logger.info(f"--- 第 {cycle_num} 次循环 ---")
                
                # 执行一次循环操作
                result = self.run_cycle_operation()
                
                if result['success']:
                    stats['successful_cycles'] += 1
                    stats['consecutive_errors'] = 0  # 重置连续错误计数
                    
                    if result['is_live_room']:
                        stats['live_rooms_skipped'] += 1
                        logger.info(f"第 {cycle_num} 次循环成功 (跳过直播间)")
                    else:
                        logger.info(f"第 {cycle_num} 次循环成功")
                else:
                    stats['failed_cycles'] += 1
                    stats['consecutive_errors'] += 1
                    
                    if result['is_live_room']:
                        logger.error(f"第 {cycle_num} 次循环失败 (直播间滑动失败)")
                    else:
                        logger.error(f"第 {cycle_num} 次循环失败")
                    
                    # 检查连续错误次数
                    if stats['consecutive_errors'] >= max_errors:
                        logger.warning(f"连续 {max_errors} 次错误，停止循环")
                        break
                
                # 打印当前统计
                success_rate = (stats['successful_cycles'] / stats['total_cycles']) * 100
                live_room_info = (
                    f", 跳过直播间: {stats['live_rooms_skipped']}" 
                    if stats['live_rooms_skipped'] > 0 else ""
                )
                logger.info(
                    f"当前成功率: {stats['successful_cycles']}/{stats['total_cycles']} "
                    f"({success_rate:.1f}%){live_room_info}"
                )
                
                # 检查是否达到目标次数
                if cycle_count > 0 and cycle_num >= cycle_count:
                    logger.info(f"达到目标次数 {cycle_count}，循环结束")
                    break
                
                # 循环间隔等待
                time.sleep(2)
                
        except KeyboardInterrupt:
            logger.info("用户中断循环")
        except Exception as e:
            logger.error(f"循环过程中发生意外错误: {e}")
        
        # 打印最终统计
        self.print_cycle_stats(stats)
        return stats
    
    def print_cycle_stats(self, stats: Dict[str, int]) -> None:
        """打印循环统计信息"""
        print("\n" + "=" * 60)
        print("📊 循环操作统计")
        print("=" * 60)
        
        total = stats['total_cycles']
        successful = stats['successful_cycles']
        failed = stats['failed_cycles']
        live_rooms = stats.get('live_rooms_skipped', 0)
        
        if total > 0:
            success_rate = (successful / total) * 100
            live_room_rate = (live_rooms / total) * 100 if total > 0 else 0
            
            print(f"总循环次数: {total}")
            print(f"成功次数: {successful}")
            print(f"失败次数: {failed}")
            print(f"直播间跳过: {live_rooms} ({live_room_rate:.1f}%)")
            print(f"成功率: {success_rate:.1f}%")
            
            if live_rooms > 0:
                print(f"📺 遇到 {live_rooms} 个直播间，已自动跳过")
            
            if success_rate >= 80:
                print("🎉 循环表现优秀！")
            elif success_rate >= 60:
                print("👍 循环表现良好")
            else:
                print("⚠️  循环表现需要改进")
        else:
            print("未执行任何循环")
        
        print("=" * 60)

