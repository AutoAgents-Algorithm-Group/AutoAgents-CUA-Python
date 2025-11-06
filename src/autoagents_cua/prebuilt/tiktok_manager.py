#!/usr/bin/env python3
"""
TikTok Manager - TikTok

MobileDevice TikTok
"""

import time
from typing import Dict, Tuple, List, Optional

from ..agent.mobile_agent import MobileDevice
from ..utils.logging import logger


class TikTokManager:
    """TikTok- TikTok"""
    
    # TikTok
    PACKAGE_NAME = "com.zhiliaoapp.musically"
    
    def __init__(self, device_address: str = "127.0.0.1:5555"):
        """
        TikTok
        
        Args:
            device_address: 
        """
        self.device = MobileDevice(device_address)
    
    @property
    def is_connected(self) -> bool:
        """"""
        return self.device.is_connected
    
    def start_app(self) -> bool:
        """TikTok"""
        return self.device.start_app(self.PACKAGE_NAME)
    
    def stop_app(self) -> bool:
        """TikTok"""
        return self.device.stop_app(self.PACKAGE_NAME)
 
    def handle_popups(self) -> bool:
        """"""
        try:
            logger.info("...")
            handled_any = False
            
            # 
            privacy_buttons = ["", "", "", ""]
            for button_text in privacy_buttons:
                if self.device.click_element(text=button_text, timeout=2):
                    logger.info(f": '{button_text}'")
                    time.sleep(2)
                    handled_any = True
                    break
            
            # ""
            knowledge_buttons = ["", "", ""]
            for button_text in knowledge_buttons:
                if self.device.click_element(text=button_text, timeout=2):
                    logger.info(f": '{button_text}'")
                    time.sleep(2)
                    handled_any = True
                    break
            
            # 
            other_buttons = ["", "", "", ""]
            for button_text in other_buttons:
                if self.device.click_element(text=button_text, timeout=1):
                    logger.info(f": '{button_text}'")
                    time.sleep(1)
                    handled_any = True
                    break
            
            if not handled_any:
                logger.info("")
            
            return True
        
        except Exception as e:
            logger.error(f": {e}")
            return False
 
    def handle_video_rating_popup(self) -> bool:
        """''"""
        try:
            # 
            rating_popup_texts = [
                "",
                "",
                "",
                ""
            ]
            
            popup_found = False
            for popup_text in rating_popup_texts:
                if self.device.find_element(text_contains=popup_text, timeout=1):
                    logger.info(f": {popup_text}")
                    popup_found = True
                    break
            
            if not popup_found:
                return False  # 
            
            # ""
            neutral_options = [
                "",
                "",
                "",
                ""
            ]
            
            option_clicked = False
            for option_text in neutral_options:
                if self.device.click_element(text=option_text, timeout=2):
                    logger.info(f": '{option_text}'")
                    option_clicked = True
                    time.sleep(1)
                    break
                elif self.device.click_element(text_contains=option_text, timeout=2):
                    logger.info(f": '{option_text}'")
                    option_clicked = True
                    time.sleep(1)
                    break
            
            if not option_clicked:
                logger.warning("''...")
                # 
                text_views = self.device.device(className="android.widget.TextView", clickable=True)
                if text_views.count > 2:
                    middle_index = text_views.count // 2
                    try:
                        middle_option = text_views[middle_index]
                        if middle_option.exists:
                            middle_option.click()
                            logger.info("")
                            option_clicked = True
                            time.sleep(1)
                    except:
                        pass
            
            # 
            if option_clicked:
                submit_buttons = ["", "", "", "OK"]
                for submit_text in submit_buttons:
                    if self.device.click_element(text=submit_text, timeout=2):
                        logger.info(f": '{submit_text}'")
                        time.sleep(1)
                        break
                
                logger.info("")
                return True
            else:
                logger.error("")
                return False
        
        except Exception as e:
            logger.error(f": {e}")
            return False
 
    def check_login_required(self) -> bool:
        """"""
        try:
            logger.info("...")
            
            # 
            login_indicators = [
                " TikTok",
                "//",
                "Facebook ",
                "Google ",
                "",
                "/"
            ]
            
            for indicator in login_indicators:
                if self.device.find_element(text_contains=indicator, timeout=2):
                    logger.warning(f": {indicator}")
                    return True
            
            logger.info("")
            return False
        
        except Exception as e:
            logger.error(f": {e}")
            return False
 
    def is_video_page(self) -> bool:
        """"""
        try:
            # 
            video_indicators = ["", "", "LIVE", "STEM", "", ""]
            
            indicator_count = 0
            for indicator in video_indicators:
                if self.device.find_element(text=indicator, timeout=1):
                    indicator_count += 1
            
            # 2
            return indicator_count >= 2
        
        except Exception as e:
            logger.error(f": {e}")
            return False
 
    def is_live_room(self) -> bool:
        """"""
        try:
            # 
            live_indicators = [
                "", "", "LIVE",
                "", "", ""
            ]
            
            for indicator in live_indicators:
                if self.device.find_element(text=indicator, timeout=1):
                    logger.info(f": {indicator}")
                    return True
            
            # UI
            live_ui_indicators = [
                "com.zhiliaoapp.musically:id/live_room",
                "com.zhiliaoapp.musically:id/live_indicator",
                "com.zhiliaoapp.musically:id/live_badge"
            ]
            
            for resource_id in live_ui_indicators:
                if self.device.find_element(resource_id=resource_id, timeout=1):
                    logger.info(f"UI: {resource_id}")
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f": {e}")
            return False
 
    def get_current_video_info(self) -> Dict:
        """"""
        try:
            info = {}
            
            # 
            try:
                text_views = self.device.device(className="android.widget.TextView")
                visible_texts = []
                for tv in text_views:
                    if tv.exists:
                        text = tv.get_text()
                        if text and len(text.strip()) > 0:
                            visible_texts.append(text.strip())
                
                info['texts'] = visible_texts[:10]  # 10
            except:
                info['texts'] = []
            
            # 
            info['screenshot_hash'] = self.device.get_screenshot_hash()
            
            return info
        
        except Exception as e:
            logger.error(f": {e}")
            return {}
 
    def scroll_to_next_video(self, force_level: str = "strong") -> bool:
        """
        
        
        Args:
            force_level: ("light", "medium", "strong", "ultra")
        """
        try:
            logger.info(f"{force_level}...")
            
            # 
            before_info = self.get_current_video_info()
            logger.debug(f": {before_info.get('screenshot_hash', 'N/A')}")
            
            # 
            force_params = {
                "light": (0.65, 0.35, 0.4, 1),
                "medium": (0.75, 0.25, 0.3, 1),
                "strong": (0.8, 0.15, 0.2, 1),
                "ultra": (0.85, 0.1, 0.15, 1)
            }
            start_ratio, end_ratio, duration, repeat_count = force_params.get(
                force_level, force_params["strong"]
            )
            
            # 
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
                f"{force_level}: ({center_x}, {start_y}) "
                f"({center_x}, {end_y}), {repeat_count}"
            )
            
            # 
            time.sleep(2)
            
            # 
            after_info = self.get_current_video_info()
            logger.debug(f": {after_info.get('screenshot_hash', 'N/A')}")
            
            # 
            video_changed = self._check_video_changed(before_info, after_info)
            
            if video_changed:
                logger.info("")
                
                # 
                time.sleep(1)
                self.handle_video_rating_popup()
                
                return True
            else:
                logger.warning("")
                return False
        
        except Exception as e:
            logger.error(f": {e}")
            return False
 
    def _check_video_changed(self, before_info: Dict, after_info: Dict) -> bool:
        """"""
        try:
            # 1: 
            before_hash = before_info.get('screenshot_hash')
            after_hash = after_info.get('screenshot_hash')
            if before_hash and after_hash and before_hash != after_hash:
                logger.debug("")
                return True
            
            # 2: 
            before_texts = set(before_info.get('texts', []))
            after_texts = set(after_info.get('texts', []))
            
            if len(before_texts) > 0 and len(after_texts) > 0:
                common_texts = before_texts.intersection(after_texts)
                total_texts = before_texts.union(after_texts)
                
                if len(total_texts) > 0:
                    similarity = len(common_texts) / len(total_texts)
                    logger.debug(f": {similarity:.2f}")
                    if similarity < 0.5:  # 50%
                        logger.debug("")
                        return True
            
            return False
        
        except Exception as e:
            logger.error(f": {e}")
            return False
 
    def click_creator_avatar(self) -> bool:
        """"""
        try:
            logger.info("...")
            
            # ImageView
            image_views = self.device.device(className="android.widget.ImageView")
            if image_views.exists:
                logger.debug(f" {len(image_views)} ImageView")
                
                # ImageView
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
                                
                                # 
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
                                        f": ({img_center_x}, {img_center_y}) "
                                        f"({img_width}x{img_height})"
                                    )
                                    img.click()
                                    logger.info("")
                                    return True
                        
                        except Exception as e:
                            logger.debug(f"ImageView {i} : {e}")
                            continue
            else:
                logger.error("ImageView")
            
            return False
        
        except Exception as e:
            logger.error(f": {e}")
            return False
 
    def click_message_button(self) -> bool:
        """"""
        try:
            logger.info("...")
            time.sleep(2)  # 
            
            # 1: ""
            if self.device.click_element(text="", timeout=5):
                logger.info("''")
                return True
            elif self.device.click_element(text_contains="", timeout=3):
                logger.info("''")
                return True
            
            # 2: resourceId
            possible_message_ids = [
                "com.zhiliaoapp.musically:id/message",
                "com.zhiliaoapp.musically:id/message_btn",
                "com.zhiliaoapp.musically:id/chat_button",
                "com.zhiliaoapp.musically:id/dm_button"
            ]
            
            for resource_id in possible_message_ids:
                if self.device.click_element(resource_id=resource_id, timeout=2):
                    logger.info(f"resourceId: {resource_id}")
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f": {e}")
            return False
 
    def click_back_button(self) -> bool:
        """ImageView"""
        try:
            logger.info("...")
            
            # ImageView
            image_views = self.device.device(className="android.widget.ImageView")
            if image_views.exists:
                logger.debug(f" {len(image_views)} ImageView")
                
                # ImageView
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
                                
                                # 
                                is_left_side = img_center_x < self.device.screen_width * 0.25
                                is_top_area = img_center_y < self.device.screen_height * 0.15
                                is_button_size = 20 < img_width < 100 and 20 < img_height < 100
                                is_square_like = abs(img_width - img_height) < 40
                                is_not_status_bar = img_center_y > self.device.screen_height * 0.05
                                
                                if (is_left_side and is_top_area and is_button_size 
                                    and is_square_like and is_not_status_bar):
                                    logger.debug(
                                        f": ({img_center_x}, {img_center_y}) "
                                        f"({img_width}x{img_height})"
                                    )
                                    img.click()
                                    logger.info("")
                                    time.sleep(1)
                                    return True
                        
                        except Exception as e:
                            logger.debug(f"ImageView {i} : {e}")
                            continue
            
            # 1: resourceId
            logger.warning("ImageView...")
            possible_back_ids = [
                "com.zhiliaoapp.musically:id/back",
                "com.zhiliaoapp.musically:id/back_btn",
                "com.zhiliaoapp.musically:id/navigation_back",
                "com.zhiliaoapp.musically:id/toolbar_back",
                "android:id/home"
            ]
            
            for resource_id in possible_back_ids:
                if self.device.click_element(resource_id=resource_id, timeout=1):
                    logger.info(f"resourceId: {resource_id}")
                    time.sleep(1)
                    return True
            
            # 2: 
            back_x = int(self.device.screen_width * 0.08)
            back_y = int(self.device.screen_height * 0.08)
            self.device.click(back_x, back_y)
            logger.info(f": ({back_x}, {back_y})")
            time.sleep(1)
            return True
        
        except Exception as e:
            logger.error(f": {e}")
            return False
 
    def test_multiple_scrolls(
        self, 
        scroll_count: int = 3, 
        force_level: str = "strong"
    ) -> Tuple[int, int]:
        """"""
        logger.info(f"{scroll_count} (: {force_level})...")
        
        successful_scrolls = 0
        
        for i in range(scroll_count):
            logger.info(f"--- {i+1} ---")
            
            if self.scroll_to_next_video(force_level=force_level):
                successful_scrolls += 1
                logger.info(f"{i+1} ")
            else:
                logger.warning(f"{i+1} ")
            
            # 
            time.sleep(1)
        
        logger.info(f": {successful_scrolls}/{scroll_count} ")
        return successful_scrolls, scroll_count
 
    def run_cycle_operation(self) -> Dict[str, bool]:
        """
        -> -> -> -> 
        
        Returns:
            Dict: 
                - success: 
                - is_live_room: 
        """
        try:
            logger.info("...")
            
            # 
            if self.is_live_room():
                logger.info("")
                if self.scroll_to_next_video(force_level="ultra"):
                    logger.info("")
                    return {'success': True, 'is_live_room': True}
                else:
                    logger.warning("")
                    return {'success': False, 'is_live_room': True}
            
            # 1: 
            logger.info("1 ...")
            if not self.click_creator_avatar():
                logger.error("")
                return {'success': False, 'is_live_room': False}
            
            time.sleep(2)
            
            # 2: 
            logger.info("2 ...")
            if not self.click_message_button():
                logger.error("...")
                self.click_back_button()
                return {'success': False, 'is_live_room': False}
            
            time.sleep(2)
            
            # 3: 
            logger.info("3 ...")
            if not self.click_back_button():
                logger.warning("")
            
            time.sleep(1)
            
            # 4: 
            logger.info("4 ...")
            if not self.click_back_button():
                logger.warning("")
            
            time.sleep(2)
            
            # 5: 
            logger.info("5 ...")
            if not self.scroll_to_next_video(force_level="ultra"):
                logger.warning("")
            
            time.sleep(1)
            
            logger.info("")
            return {'success': True, 'is_live_room': False}
        
        except Exception as e:
            logger.error(f": {e}")
            return {'success': False, 'is_live_room': False}
 
    def run_continuous_cycle(
        self, 
        cycle_count: int = 10, 
        max_errors: int = 3
    ) -> Dict[str, int]:
        """
        
        
        Args:
            cycle_count: -1
            max_errors: 
        
        Returns:
            Dict: 
        """
        logger.info(f"(: {cycle_count if cycle_count > 0 else ''} )")
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
                
                logger.info(f"--- {cycle_num} ---")
                
                # 
                result = self.run_cycle_operation()
                
                if result['success']:
                    stats['successful_cycles'] += 1
                    stats['consecutive_errors'] = 0  # 
                    
                    if result['is_live_room']:
                        stats['live_rooms_skipped'] += 1
                        logger.info(f"{cycle_num} ()")
                    else:
                        logger.info(f"{cycle_num} ")
                else:
                    stats['failed_cycles'] += 1
                    stats['consecutive_errors'] += 1
                    
                    if result['is_live_room']:
                        logger.error(f"{cycle_num} ()")
                    else:
                        logger.error(f"{cycle_num} ")
                
                # 
                if stats['consecutive_errors'] >= max_errors:
                    logger.warning(f"{max_errors} ")
                    break
                
                # 
                success_rate = (stats['successful_cycles'] / stats['total_cycles']) * 100
                live_room_info = (
                    f", : {stats['live_rooms_skipped']}" 
                    if stats['live_rooms_skipped'] > 0 else ""
                )
                logger.info(
                    f": {stats['successful_cycles']}/{stats['total_cycles']} "
                    f"({success_rate:.1f}%){live_room_info}"
                )
                
                # 
                if cycle_count > 0 and cycle_num >= cycle_count:
                    logger.info(f" {cycle_count}")
                    break
                
                # 
                time.sleep(2)
        
        except KeyboardInterrupt:
            logger.info("")
        except Exception as e:
            logger.error(f": {e}")
        
        # 
        self.print_cycle_stats(stats)
        return stats
 
    def print_cycle_stats(self, stats: Dict[str, int]) -> None:
        """"""
        print("\n" + "=" * 60)
        print("")
        print("=" * 60)
        
        total = stats['total_cycles']
        successful = stats['successful_cycles']
        failed = stats['failed_cycles']
        live_rooms = stats.get('live_rooms_skipped', 0)
        
        if total > 0:
            success_rate = (successful / total) * 100
            live_room_rate = (live_rooms / total) * 100 if total > 0 else 0
            
            print(f": {total}")
            print(f": {successful}")
            print(f": {failed}")
            print(f": {live_rooms} ({live_room_rate:.1f}%)")
            print(f": {success_rate:.1f}%")
            
            if live_rooms > 0:
                print(f" {live_rooms} ")
            
            if success_rate >= 80:
                print(" ")
            elif success_rate >= 60:
                print(" ")
            else:
                print(" ")
        else:
            print("")
        
        print("=" * 60)

