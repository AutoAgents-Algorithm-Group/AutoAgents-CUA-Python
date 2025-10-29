from openai import OpenAI
import re
from ..logging import logger, set_stage
from ...models import Stage
from ..image_converter import encode_image
from time import sleep
import random
import os

class CaptchaAgent:
    def __init__(self, 
                api_key: str = "sk-YzEnX4MC8gTeOQ1C97LCMiInyighBQI9bDPhNUyiK5X7v6gu", 
                base_url: str = "https://api.tu-zi.com/v1",
                model: str = "gemini-2.5-pro",
                ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        
        # 初始化输出目录
        self._init_output_dir()

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
    
    def _init_output_dir(self):
        """初始化输出目录"""
        # 获取当前文件所在目录（backend/src/utils/captcha_solver）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建 playground/outputs 目录路径
        self.output_dir = os.path.join(current_dir, '..', '..', '..', 'playground', 'outputs')
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _get_output_path(self, filename):
        """
        获取输出文件的完整路径
        
        Args:
            filename: 文件名
            
        Returns:
            str: 完整路径
        """
        return os.path.join(self.output_dir, filename)
    
    

    def recognize_captcha(self, captcha_img_path: str):
        log = set_stage(Stage.CAPTCHA)
        # 编码验证码图片
        image_data = encode_image(captcha_img_path)

        # 构建提示词
        prompt = (
            "这是一个图像验证码。图片顶部有一个目标物品的示例图标，下方是一个3x3的九宫格，包含9张图片。\n"
            "请仔细观察顶部的目标物品是什么，然后在下方的9张图片中找出所有包含该目标物品的图片。\n\n"
            "坐标系统说明：\n"
            "- 整个图片左上角为(0,0)，右下角为(1000,1000)\n"
            "- 九宫格排列为3行3列，从左到右、从上到下\n"
            "- 每个格子的中心点坐标大约为：\n"
            "  第1行：(167,250), (500,250), (833,250)\n"
            "  第2行：(167,500), (500,500), (833,500)\n"
            "  第3行：(167,750), (500,750), (833,750)\n\n"
            "请返回所有包含目标物品的图片的中心坐标。\n"
            "输出格式：[(x1,y1),(x2,y2),...]，坐标为整数，只输出坐标本身，不要任何其他内容！\n"
            "如果没有找到匹配的图片，返回空列表[]。\n"
            "示例：[(167,250),(833,500)]"
        )


        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"  # 修复：去掉逗号后的空格
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,  # 增加 token 限制
                temperature=0.2   # 降低随机性
            )  
            # 获取回答
            answer = response.choices[0].message.content
            log.success(f"模型回答: {answer}")

        except Exception as e:
            log.error(f"调用 API 失败: {e}")
            log.exception("API 调用异常详情")
            answer = ""

        return answer

    # def parse_coordinates(self, answer):
    #     """
    #     解析坐标字符串
        
    #     Args:
    #         answer: 模型返回的坐标字符串，格式如 "[(x1,y1),(x2,y2)]"
            
    #     Returns:
    #         list: 坐标列表 [(x1, y1), (x2, y2), ...] 或空列表
    #     """
    #     # 解析坐标
    #     pattern = r'\[\(\d+,\s*\d+\)(?:,\s*\(\d+,\s*\d+\))*\]'
    #     matches = re.findall(pattern, answer)

    #     coordinate_lists = []
    #     for match in matches:
    #         try:
    #             cleaned = match.replace(' ', '')
    #             coord_list = eval(cleaned)
    #             if isinstance(coord_list, list):
    #                 coordinate_lists.append(coord_list)
    #         except:
    #             continue

    #     if coordinate_lists:
    #         result_list = coordinate_lists[-1]
    #         logger.success(f"解析出的坐标: {result_list}")
    #         logger.info(f"共找到 {len(result_list)} 个匹配的图片")
            
    #         # 打印每个坐标对应的位置
    #         positions = {
    #             (167, 250): "第1行第1个", (500, 250): "第1行第2个", (833, 250): "第1行第3个",
    #             (167, 500): "第2行第1个", (500, 500): "第2行第2个", (833, 500): "第2行第3个",
    #             (167, 750): "第3行第1个", (500, 750): "第3行第2个", (833, 750): "第3行第3个"
    #         }
            
    #         logger.info("匹配的图片位置：")
    #         for i, coord in enumerate(result_list, 1):
    #             position = positions.get(tuple(coord), "未知位置")
    #             logger.info(f"  {i}. 坐标 {coord} -> {position}")
            
    #         return result_list
    #     else:
    #         logger.warning("未能解析出有效坐标")
    #         logger.debug(f"原始回答: {answer}")
    #         return []

    def click_captcha_coordinates(self, page, captcha_info, coordinates, convert_from_1000=True):
        """
        根据坐标点击验证码
        
        Args:
            page: DrissionPage 页面对象
            captcha_info: 验证码信息字典（包含位置和尺寸）
                格式: {
                    'location': (x, y),  # 位置元组
                    'width': width,      # 宽度
                    'height': height     # 高度
                }
            coordinates: 坐标列表 [(x1, y1), (x2, y2), ...]
            convert_from_1000: 是否从 1000x1000 比例转换（默认 True）
            
        Returns:
            bool: 是否成功点击
        """
        from time import sleep
        
        try:
            if not coordinates:
                logger.warning("没有坐标可以点击")
                return False
            
            width = captcha_info['width']
            height = captcha_info['height']
            location = captcha_info['location']  # (x, y) tuple
            
            logger.info(f"开始点击验证码，共 {len(coordinates)} 个坐标点")
            logger.info(f"验证码位置: {location}, 尺寸: {width}x{height}")
            
            for i, point in enumerate(coordinates, 1):
                x, y = point
                
                # 如果坐标是基于 1000x1000 的比例，需要转换
                if convert_from_1000:
                    # 转换为相对于元素的实际坐标
                    x = (width / 1000) * x
                    y = (height / 1000) * y
                
                # 计算绝对坐标（相对于页面）
                abs_x = location[0] + x
                abs_y = location[1] + y
                
                logger.debug(f"[{i}] 点击坐标: 原始{point} -> 相对({x:.1f}, {y:.1f}) -> 绝对({abs_x:.1f}, {abs_y:.1f})")
                
                # 使用 actions.move_to().click() 方法
                page.actions.move_to((abs_x, abs_y)).click()
                logger.success(f"[{i}] 点击成功")
                
                sleep(0.5)  # 每次点击后短暂等待
            
            logger.success("所有坐标点击完成")
            
            # 点击确认按钮（如果有）
            try:
                sleep(1)
                commit_button = page.ele('t:div@@class=geetest_commit_tip')
                if commit_button:
                    commit_button.click()
                    logger.success("已点击确认按钮")
            except:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"点击验证码失败: {e}")
            logger.exception("点击验证码异常详情")
            return False
    
    def solve_captcha(self, page, captcha_selector='t:div@@class=geetest_panel_next', 
                      save_path=None, timeout=10, max_retries=3):
        """
        完整的验证码处理流程（等待、识别、点击、验证），支持自动重试
        
        Args:
            page: DrissionPage 页面对象
            captcha_selector: 验证码面板定位器
            save_path: 验证码截图保存路径（默认为 playground/outputs/captcha.png）
            timeout: 等待超时时间（秒）
            max_retries: 最大重试次数
            
        Returns:
            bool: 是否成功处理验证码
        """
        from time import sleep
        
        log = set_stage(Stage.CAPTCHA)
        
        # 如果没有指定保存路径，使用默认路径
        if save_path is None:
            save_path = self._get_output_path('captcha.png')
        elif not os.path.isabs(save_path):
            # 如果是相对路径，转换为输出目录下的路径
            save_path = self._get_output_path(save_path)
        
        try:
            log.info(f"开始验证码处理（最多尝试 {max_retries} 次）")
            
            # 1. 等待验证码出现
            log.info("等待验证码出现...")
            page.wait.ele_displayed(captcha_selector, timeout=timeout)
            sleep(5)  # 额外等待确保完全加载
            
            # 尝试多次识别和点击
            for attempt in range(1, max_retries + 1):
                log.info(f"第 {attempt}/{max_retries} 次尝试")
                
                try:
                    # 2. 获取验证码元素信息
                    captcha_panel = page.ele(captcha_selector)
                    if not captcha_panel:
                        log.warning("未找到验证码面板")
                        if attempt < max_retries:
                            log.info("等待验证码刷新...")
                            sleep(2)
                            continue
                        return False
                    
                    location = captcha_panel.rect.location
                    size = captcha_panel.rect.size
                    
                    captcha_info = {
                        'location': location,
                        'width': size[0],
                        'height': size[1]
                    }
                    
                    log.success(f"验证码信息: 位置{location}, 尺寸{size}")
                    
                    # 3. 截取验证码图片
                    captcha_panel.get_screenshot(save_path)
                    log.success(f"验证码截图已保存: {save_path}")
                    
                    # 4. 识别验证码
                    log.info("识别验证码...")
                    answer = self.recognize_captcha(save_path)
                    
                    # 5. 解析坐标
                    coordinates = self.parse_coordinates(answer)
                    
                    if not coordinates:
                        log.warning("未能解析出坐标")
                        if attempt < max_retries:
                            log.info("准备重试...")
                            sleep(2)
                            continue
                        return False
                    
                    # 6. 点击验证码坐标
                    success = self.click_captcha_coordinates(
                        page=page,
                        captcha_info=captcha_info,
                        coordinates=coordinates,
                        convert_from_1000=True
                    )
                    
                    if not success:
                        log.warning("坐标点击失败")
                        if attempt < max_retries:
                            log.info("准备重试...")
                            sleep(2)
                            continue
                        return False
                    
                    # 7. 等待验证结果
                    sleep(3)
                    
                    # 8. 检查验证码面板是否还存在
                    captcha_panel_after = page.ele(captcha_selector, timeout=2)
                    
                    if captcha_panel_after:
                        # 验证码面板还在，说明验证失败，需要重试
                        log.warning(f"验证码验证失败，面板仍然存在")
                        if attempt < max_retries:
                            log.info("验证码已刷新，准备重新识别...")
                            sleep(2)
                            continue
                        else:
                            log.error(f"已达到最大重试次数 {max_retries}")
                            return False
                    else:
                        # 验证码面板消失，说明验证成功
                        log.success("✅ 验证码处理完成！")
                        return True
                        
                except Exception as e:
                    log.warning(f"第 {attempt} 次尝试出错: {e}")
                    if attempt < max_retries:
                        log.info("准备重试...")
                        sleep(2)
                        continue
                    else:
                        raise
            
            # 如果所有尝试都失败了
            log.error(f"验证码处理失败，已尝试 {max_retries} 次")
            return False
                
        except Exception as e:
            log.error(f"验证码处理失败: {e}")
            log.exception("验证码处理异常详情")
            return False

    #### --------------------------------------
    # 遗弃的处理谷歌验证码相关方法
    def recognize_recaptcha(self, captcha_img_path: str):
        """识别 reCAPTCHA 验证码图片"""
        log = set_stage(Stage.CAPTCHA)
        # 编码验证码图片
        image_data = encode_image(captcha_img_path)

        # 构建提示词
        prompt = (
            "这是一个 Google reCAPTCHA 图像验证码。图片顶部有一个目标物品的示例图标，下方是一个3x3的九宫格，包含9张图片。\n"
            "请仔细观察顶部的目标物品是什么，然后在下方的9张图片中找出所有包含该目标物品的图片。\n\n"
            "坐标系统说明：\n"
            "- 整个图片左上角为(0,0)，右下角为(1000,1000)\n"
            "- 九宫格排列为3行3列，从左到右、从上到下\n"
            "- 每个格子的中心点坐标大约为：\n"
            "  第1行：(167,250), (500,250), (833,250)\n"
            "  第2行：(167,500), (500,500), (833,500)\n"
            "  第3行：(167,750), (500,750), (833,750)\n\n"
            "请返回所有包含目标物品的图片的中心坐标。\n"
            "输出格式：[(x1,y1),(x2,y2),...]，坐标为整数，只输出坐标本身，不要任何其他内容！\n"
            "如果没有找到匹配的图片，返回空列表[]。\n"
            "示例：[(167,250),(833,500)]"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.2
            )  
            # 获取回答
            answer = response.choices[0].message.content
            log.success(f"模型回答: {answer}")

        except Exception as e:
            log.error(f"调用 API 失败: {e}")
            log.exception("API 调用异常详情")
            answer = ""

        return answer
    
    def parse_coordinates(self, answer):
        """
        解析坐标字符串
        
        Args:
            answer: 模型返回的坐标字符串，格式如 "[(x1,y1),(x2,y2)]"
            
        Returns:
            list: 坐标列表 [(x1, y1), (x2, y2), ...] 或空列表
        """
        logger.info(f"原始回答: {answer}")
        
        # 方法1: 尝试解析完整的坐标格式
        pattern = r'\[\(\d+,\s*\d+\)(?:,\s*\(\d+,\s*\d+\))*\]'
        matches = re.findall(pattern, answer)
        
        if matches:
            try:
                cleaned = matches[0].replace(' ', '')
                coord_list = eval(cleaned)
                if isinstance(coord_list, list):
                    logger.success(f"成功解析坐标: {coord_list}")
                    return coord_list
            except Exception as e:
                logger.warning(f"完整格式解析失败: {e}")
        
        # 方法2: 尝试修复不完整的坐标格式
        # 查找所有 (x,y) 格式的坐标
        coord_pattern = r'\((\d+),\s*(\d+)\)'
        coord_matches = re.findall(coord_pattern, answer)
        
        if coord_matches:
            try:
                # 将字符串坐标转换为整数元组
                coordinates = [(int(x), int(y)) for x, y in coord_matches]
                logger.success(f"修复后解析坐标: {coordinates}")
                return coordinates
            except Exception as e:
                logger.warning(f"修复格式解析失败: {e}")
        
        # 方法3: 尝试从截断的字符串中提取坐标
        # 查找所有数字对
        number_pairs = re.findall(r'\((\d+),(\d+)', answer)
        if number_pairs:
            try:
                coordinates = [(int(x), int(y)) for x, y in number_pairs]
                logger.success(f"从截断字符串解析坐标: {coordinates}")
                return coordinates
            except Exception as e:
                logger.warning(f"截断字符串解析失败: {e}")
        
        logger.warning("未能解析出有效坐标")
        return []
    
    def recognize_recaptcha_4x4(self, captcha_img_path: str):
        """识别 4x4 reCAPTCHA 验证码图片"""
        log = set_stage(Stage.CAPTCHA)
        # 编码验证码图片
        image_data = encode_image(captcha_img_path)

        # 构建 4x4 专用提示词
        prompt = (
            "这是一个 Google reCAPTCHA 4x4 图像验证码。图片顶部有一个目标物品的示例图标，下方是一个4x4的十六宫格，包含16张图片。\n"
            "请仔细观察顶部的目标物品是什么，然后在下方的16张图片中找出所有包含该目标物品的图片。\n\n"
            "坐标系统说明：\n"
            "- 整个图片左上角为(0,0)，右下角为(1000,1000)\n"
            "- 十六宫格排列为4行4列，从左到右、从上到下\n"
            "- 每个格子的中心点坐标大约为：\n"
            "  第1行：(125,200), (375,200), (625,200), (875,200)\n"
            "  第2行：(125,400), (375,400), (625,400), (875,400)\n"
            "  第3行：(125,600), (375,600), (625,600), (875,600)\n"
            "  第4行：(125,800), (375,800), (625,800), (875,800)\n\n"
            "请返回所有包含目标物品的图片的中心坐标。\n"
            "输出格式：[(x1,y1),(x2,y2),...]，坐标为整数，只输出坐标本身，不要任何其他内容！\n"
            "如果没有找到匹配的图片，返回空列表[]。\n"
            "示例：[(125,200),(875,400)]"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.2
            )  
            # 获取回答
            answer = response.choices[0].message.content
            log.success(f"模型回答: {answer}")

        except Exception as e:
            log.error(f"调用 API 失败: {e}")
            log.exception("API 调用异常详情")
            answer = ""

        return answer

    def solve_recaptcha(self, max_retries=5):
        """处理 reCAPTCHA 验证码"""
        log = set_stage(Stage.CAPTCHA)
        log.info("开始处理 reCAPTCHA...")
        
        try:
            # 1. 切换到 reCAPTCHA iframe
            log.info("步骤1: 定位 reCAPTCHA checkbox...")
            recaptcha_iframe = self.page.ele('css:iframe[title*="reCAPTCHA"]', timeout=5)
            if not recaptcha_iframe:
                log.error("未找到 reCAPTCHA iframe")
                return False
            
            # 切换到 iframe
            self.page.get_frame(recaptcha_iframe)
            sleep(0.3)
            
            # 2. 点击 "I'm not a robot" 复选框
            log.info("步骤2: 点击 'I'm not a robot' 复选框...")
            checkbox = self.page.ele('css:.recaptcha-checkbox-border', timeout=5)
            if checkbox:
                checkbox.click()
                log.success("✅ 已点击 reCAPTCHA 复选框")
                sleep(0.3)
            else:
                log.error("未找到复选框")
                return False
            
            # 切回主文档
            self.page.get_frame('main')
            sleep(0.1)
            
            # 3. 检查是否出现图片验证挑战
            log.info("步骤3: 检查是否出现图片验证挑战...")
            
            # 等待一段时间，让验证挑战有时间出现
            sleep(0.1)
            
            # 尝试多种方式检测挑战 iframe
            challenge_iframe = None
            
            # 方式1: 检测挑战 iframe
            challenge_iframe = self.page.ele('css:iframe[title*="recaptcha challenge"]', timeout=2)
            
            # 方式2: 如果没找到，尝试其他可能的标题
            if not challenge_iframe:
                challenge_iframe = self.page.ele('css:iframe[title*="挑战"]', timeout=2)
            
            # 方式3: 检测验证码容器是否存在
            if not challenge_iframe:
                challenge_container = self.page.ele('css:.rc-imageselect-challenge', timeout=2)
                if challenge_container:
                    log.info("检测到验证码容器，但未找到 iframe，可能挑战已直接显示")
                    # 检测验证码模式并处理
                    return self._detect_and_solve_challenge_mode(challenge_container, max_retries)
            
            if not challenge_iframe:
                # 再等待一下，有些情况下挑战出现较慢
                log.info("等待验证挑战出现...")
                sleep(2)
                challenge_iframe = self.page.ele('css:iframe[title*="recaptcha challenge"]', timeout=3)
            
            if not challenge_iframe:
                log.success("✅ 无需图片验证，reCAPTCHA 已通过！")
                return True
            
            # 4. 处理图片验证挑战
            log.info("步骤4: 检测到图片验证挑战，开始处理...")
            return self._solve_image_challenge_with_mode_detection(challenge_iframe, max_retries)
            
        except Exception as e:
            log.error(f"处理 reCAPTCHA 失败: {e}")
            log.exception("reCAPTCHA 处理异常详情")
            return False
    
    def _solve_image_challenge(self, challenge_iframe, max_retries=5):
        """处理图片验证挑战"""
        log = set_stage(Stage.CAPTCHA)
        
        try:
            # 切换到挑战 iframe
            self.page.get_frame(challenge_iframe)
            sleep(1)
            
            for attempt in range(1, max_retries + 1):
                log.info(f"第 {attempt}/{max_retries} 次尝试识别图片验证码...")
                
                # 截取验证码图片
                captcha_path = self._get_output_path(f'captcha_google_{attempt}.png')
                challenge_container = self.page.ele('css:.rc-imageselect-challenge', timeout=5)
                
                if not challenge_container:
                    log.warning("未找到验证码图片容器")
                    sleep(1)
                    continue
                
                # 截图
                try:
                    if not challenge_container.states.is_displayed:
                        log.warning(f"验证码容器在第 {attempt} 次尝试时不可见")
                        if attempt < max_retries:
                            sleep(2)
                            continue
                        return False
                    
                    challenge_container.get_screenshot(captcha_path)
                    log.success(f"验证码截图已保存: {captcha_path}")
                except Exception as e:
                    log.warning(f"第 {attempt} 次尝试截图失败: {e}")
                    if attempt < max_retries:
                        log.info("等待验证码刷新...")
                        sleep(2)
                        continue
                    return False
                
                # 识别验证码
                log.info("调用 AI 识别验证码...")
                answer = self.recognize_recaptcha(captcha_path)
                
                if not answer:
                    log.warning("AI 识别失败")
                    if attempt < max_retries:
                        sleep(2)
                        continue
                    return False
                
                # 解析坐标 - 转换为格子 ID
                coordinates = self.parse_coordinates(answer)
                
                if not coordinates:
                    log.warning("未能解析出坐标")
                    if attempt < max_retries:
                        sleep(2)
                        continue
                    return False
                
                # 将坐标转换为格子 ID (0-8)
                tile_ids = self._convert_coordinates_to_tile_ids(coordinates)
                
                if not tile_ids:
                    log.warning("未能转换出有效的格子 ID")
                    if attempt < max_retries:
                        sleep(2)
                        continue
                    return False
                
                # 点击对应的格子
                log.info(f"点击格子 ID: {tile_ids}")
                success = self._click_tiles(tile_ids)
                
                if not success:
                    log.warning("点击格子失败")
                    if attempt < max_retries:
                        sleep(2)
                        continue
                    return False
                
                # 点击验证按钮
                sleep(1)
                verify_button = self.page.ele('css:#recaptcha-verify-button', timeout=3)
                if verify_button:
                    verify_button.click()
                    log.success("✅ 已点击验证按钮")
                    sleep(1)
                
                # 检查是否还有挑战
                new_challenge = self.page.ele('css:.rc-imageselect-challenge', timeout=2)
                if not new_challenge:
                    log.success("✅ 图片验证通过！")
                    self.page.get_frame('main')
                    return True
                else:
                    log.warning("验证失败，准备重试...")
                    sleep(1)
            
            log.error(f"图片验证失败，已尝试 {max_retries} 次")
            self.page.get_frame('main')
            return False
            
        except Exception as e:
            log.error(f"图片验证挑战处理失败: {e}")
            log.exception("图片验证异常详情")
            self.page.get_frame('main')
            return False
    
    def _convert_coordinates_to_tile_ids(self, coordinates):
        """
        将坐标转换为格子 ID
        
        Args:
            coordinates: 坐标列表 [(x1, y1), (x2, y2), ...]
            
        Returns:
            list: 格子 ID 列表 [0, 1, 2, ...]
        """
        # 3x3 网格的坐标映射
        # 基于 1000x1000 坐标系
        coord_to_id = {
            (167, 200): 0, (500, 200): 1, (833, 200): 2,  # 第1行
            (167, 500): 3, (500, 500): 4, (833, 500): 5,  # 第2行  
            (167, 800): 6, (500, 800): 7, (833, 800): 8   # 第3行
        }
        
        tile_ids = []
        for coord in coordinates:
            x, y = coord
            # 寻找最接近的坐标
            min_distance = float('inf')
            closest_id = None
            
            for (cx, cy), tile_id in coord_to_id.items():
                distance = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    closest_id = tile_id
            
            if closest_id is not None and min_distance < 100:  # 容差100像素
                tile_ids.append(closest_id)
                logger.info(f"坐标 {coord} -> 格子 ID {closest_id}")
        
        return list(set(tile_ids))  # 去重
    
    def _click_tiles(self, tile_ids):
        """
        点击指定的格子
        
        Args:
            tile_ids: 格子 ID 列表 [0, 1, 2, ...]
            
        Returns:
            bool: 是否成功
        """
        try:
            for tile_id in tile_ids:
                # 查找对应的格子元素
                
                tile_element = self.page.ele(f'css:td[id="{tile_id}"]', timeout=3)
                if tile_element:
                    tile_element.click()
                    logger.success(f"✅ 已点击格子 {tile_id}")
                    sleep(0.15+random.random()*0.3)  # 短暂等待
                else:
                    logger.warning(f"未找到格子 {tile_id}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"点击格子失败: {e}")
            return False
    
    def _detect_challenge_mode(self, challenge_container):
        """
        检测验证码模式：3x3 独立物品模式 或 4x4 分割图片模式
        
        Args:
            challenge_container: 验证码容器元素
            
        Returns:
            str: '3x3' 或 '4x4'
        """
        try:
            # 使用 page_extractor 分析页面结构
            log = set_stage(Stage.CAPTCHA)
            log.info("使用 PageExtractor 分析验证码结构...")
            
            # 查找表格结构
            table_33 = challenge_container.ele('css:.rc-imageselect-table-33', timeout=1)
            table_44 = challenge_container.ele('css:.rc-imageselect-table-44', timeout=1)
            
            if table_33:
                log.info("✅ 检测到 3x3 模式：独立物品识别模式")
                return '3x3'
            elif table_44:
                log.info("✅ 检测到 4x4 模式：分割图片识别模式")
                return '4x4'
            else:
                # 通过格子数量判断
                tiles = challenge_container.eles('css:.rc-imageselect-tile')
                tile_count = len(tiles)
                
                if tile_count == 9:
                    log.info("✅ 通过格子数量检测到 3x3 模式")
                    return '3x3'
                elif tile_count == 16:
                    log.info("✅ 通过格子数量检测到 4x4 模式")
                    return '4x4'
                else:
                    log.warning(f"未知模式，格子数量: {tile_count}")
                    return '3x3'  # 默认使用 3x3 模式
                    
        except Exception as e:
            log.error(f"检测验证码模式失败: {e}")
            return '3x3'  # 默认使用 3x3 模式
    
    def _detect_and_solve_challenge_mode(self, challenge_container, max_retries=5):
        """检测验证码模式并选择相应的处理方法"""
        log = set_stage(Stage.CAPTCHA)
        
        # 检测模式
        mode = self._detect_challenge_mode(challenge_container)
        
        if mode == '3x3':
            log.info("使用 3x3 独立物品识别模式处理...")
            return self._solve_image_challenge_direct(challenge_container, max_retries)
        elif mode == '4x4':
            log.info("使用 4x4 分割图片识别模式处理...")
            return self._solve_image_challenge_4x4(challenge_container, max_retries)
        else:
            log.warning("未知模式，使用默认 3x3 模式")
            return self._solve_image_challenge_direct(challenge_container, max_retries)
    
    def _solve_image_challenge_with_mode_detection(self, challenge_iframe, max_retries=5):
        """iframe 模式下的验证码处理（带模式检测）"""
        log = set_stage(Stage.CAPTCHA)
        
        try:
            # 切换到挑战 iframe
            self.page.get_frame(challenge_iframe)
            sleep(2)
            
            # 检测验证码容器
            challenge_container = self.page.ele('css:.rc-imageselect-challenge', timeout=5)
            if not challenge_container:
                log.warning("未找到验证码图片容器")
                self.page.get_frame('main')
                return False
            
            # 检测模式并处理
            mode = self._detect_challenge_mode(challenge_container)
            
            if mode == '3x3':
                log.info("iframe 模式：使用 3x3 独立物品识别模式处理...")
                return self._solve_image_challenge_iframe_3x3(challenge_container, max_retries)
            elif mode == '4x4':
                log.info("iframe 模式：使用 4x4 分割图片识别模式处理...")
                return self._solve_image_challenge_iframe_4x4(challenge_container, max_retries)
            else:
                log.warning("iframe 模式：未知模式，使用默认 3x3 模式")
                return self._solve_image_challenge_iframe_3x3(challenge_container, max_retries)
                
        except Exception as e:
            log.error(f"iframe 模式验证码处理失败: {e}")
            log.exception("iframe 模式验证码异常详情")
            self.page.get_frame('main')
            return False
    
    def _solve_image_challenge_4x4(self, challenge_container, max_retries=5):
        """处理 4x4 分割图片模式"""
        log = set_stage(Stage.CAPTCHA)
        
        try:
            for attempt in range(1, max_retries + 1):
                log.info(f"第 {attempt}/{max_retries} 次尝试识别 4x4 分割图片验证码...")
                
                # 截取验证码图片
                captcha_path = self._get_output_path(f'captcha_google_4x4_{attempt}.png')
                
                # 检查元素是否仍然存在且可见
                try:
                    if not challenge_container.states.is_displayed:
                        log.warning(f"验证码容器在第 {attempt} 次尝试时不可见")
                        if attempt < max_retries:
                            sleep(2)
                            continue
                        return False
                    
                    # 尝试获取截图
                    challenge_container.get_screenshot(captcha_path)
                    log.success(f"验证码截图已保存: {captcha_path}")
                except Exception as e:
                    log.warning(f"第 {attempt} 次尝试截图失败: {e}")
                    if attempt < max_retries:
                        log.info("等待验证码刷新...")
                        sleep(2)
                        continue
                    return False
                
                # 识别验证码（使用 4x4 专用提示词）
                log.info("调用 AI 识别 4x4 分割图片验证码...")
                answer = self.recognize_recaptcha_4x4(captcha_path)
                
                if not answer:
                    log.warning("AI 识别失败")
                    if attempt < max_retries:
                        sleep(2)
                        continue
                    return False
                
                # 解析坐标
                coordinates = self.parse_coordinates(answer)
                
                if not coordinates:
                    log.warning("未能解析出坐标")
                    if attempt < max_retries:
                        sleep(2)
                        continue
                    return False
                
                # 将坐标转换为格子 ID (0-15)
                tile_ids = self._convert_coordinates_to_tile_ids_4x4(coordinates)
                
                if not tile_ids:
                    log.warning("未能转换出有效的格子 ID")
                    if attempt < max_retries:
                        sleep(2)
                        continue
                    return False
                
                # 点击对应的格子
                log.info(f"点击格子 ID: {tile_ids}")
                success = self._click_tiles_4x4(tile_ids)
                
                if not success:
                    log.warning("点击格子失败")
                    if attempt < max_retries:
                        sleep(2)
                        continue
                    return False
                
                # 点击验证按钮
                sleep(1)
                verify_button = self.page.ele('css:#recaptcha-verify-button', timeout=3)
                if verify_button:
                    verify_button.click()
                    log.success("✅ 已点击验证按钮")
                    sleep(3)
                
                # 检查是否还有挑战
                new_challenge = self.page.ele('css:.rc-imageselect-challenge', timeout=2)
                if not new_challenge:
                    log.success("✅ 4x4 图片验证通过！")
                    return True
                else:
                    log.warning("验证失败，准备重试...")
                    sleep(2)
            
            log.error(f"4x4 图片验证失败，已尝试 {max_retries} 次")
            return False
            
        except Exception as e:
            log.error(f"4x4 图片验证处理失败: {e}")
            log.exception("4x4 图片验证异常详情")
            return False
    
    def _convert_coordinates_to_tile_ids_4x4(self, coordinates):
        """
        将坐标转换为 4x4 格子 ID
        
        Args:
            coordinates: 坐标列表 [(x1, y1), (x2, y2), ...]
            
        Returns:
            list: 格子 ID 列表 [0, 1, 2, ..., 15]
        """
        # 4x4 网格的坐标映射
        # 基于 1000x1000 坐标系
        coord_to_id = {
            (125, 175): 0, (375, 175): 1, (625, 175): 2, (875, 175): 3,   # 第1行
            (125, 425): 4, (375, 425): 5, (625, 425): 6, (875, 425): 7,   # 第2行
            (125, 675): 8, (375, 675): 9, (625, 675): 10, (875, 675): 11,  # 第3行
            (125, 925): 12, (375, 925): 13, (625, 925): 14, (875, 925): 15 # 第4行
        }
        
        tile_ids = []
        for coord in coordinates:
            x, y = coord
            # 寻找最接近的坐标
            min_distance = float('inf')
            closest_id = None
            
            for (cx, cy), tile_id in coord_to_id.items():
                distance = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    closest_id = tile_id
            
            if closest_id is not None and min_distance < 100:  # 容差100像素
                tile_ids.append(closest_id)
                logger.info(f"坐标 {coord} -> 格子 ID {closest_id}")
        
        return list(set(tile_ids))  # 去重
    
    def _click_tiles_4x4(self, tile_ids):
        """
        点击指定的 4x4 格子
        
        Args:
            tile_ids: 格子 ID 列表 [0, 1, 2, ..., 15]
            
        Returns:
            bool: 是否成功
        """
        try:
            for tile_id in tile_ids:
                # 查找对应的格子元素
                tile_element = self.page.ele(f'css:td[id="{tile_id}"]', timeout=3)
                if tile_element:
                    tile_element.click()
                    logger.success(f"✅ 已点击 4x4 格子 {tile_id}")
                    sleep(0.5)  # 短暂等待
                else:
                    logger.warning(f"未找到 4x4 格子 {tile_id}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"点击 4x4 格子失败: {e}")
            return False
    
    def _solve_image_challenge_iframe_3x3(self, challenge_container, max_retries=3):
        """iframe 模式下的 3x3 处理"""
        return self._solve_image_challenge_direct(challenge_container, max_retries)
    
    def _solve_image_challenge_iframe_4x4(self, challenge_container, max_retries=3):
        """iframe 模式下的 4x4 处理"""
        return self._solve_image_challenge_4x4(challenge_container, max_retries)
    
    def _solve_image_challenge_direct(self, challenge_container, max_retries=5):
        """直接处理验证码容器（不在 iframe 中）"""
        log = set_stage(Stage.CAPTCHA)
        
        try:
            for attempt in range(1, max_retries + 1):
                log.info(f"第 {attempt}/{max_retries} 次尝试识别图片验证码（直接模式）...")
                
                # 截取验证码图片
                sleep(0.3)
                captcha_path = self._get_output_path(f'captcha_google_direct_{attempt}.png')
                
                # 检查元素是否仍然存在且可见
                try:
                    if not challenge_container.states.is_displayed:
                        log.warning(f"验证码容器在第 {attempt} 次尝试时不可见")
                        if attempt < max_retries:
                            sleep(2)
                            continue
                        return False
                    
                    # 尝试获取截图
                    challenge_container.get_screenshot(captcha_path)
                    log.success(f"验证码截图已保存: {captcha_path}")
                except Exception as e:
                    log.warning(f"第 {attempt} 次尝试截图失败: {e}")
                    if attempt < max_retries:
                        log.info("等待验证码刷新...")
                        sleep(2)
                        continue
                    return False
                
                # 识别验证码
                log.info("调用 AI 识别验证码...")
                answer = self.recognize_recaptcha(captcha_path)
                
                if not answer:
                    log.warning("AI 识别失败")
                    if attempt < max_retries:
                        sleep(0.3)
                        continue
                    return False
                
                # 解析坐标
                coordinates = self.parse_coordinates(answer)
                
                if not coordinates:
                    log.warning("未能解析出坐标")
                    if attempt < max_retries:
                        sleep(0.3)
                        continue
                    return False
                
                # 将坐标转换为格子 ID (0-8)
                tile_ids = self._convert_coordinates_to_tile_ids(coordinates)
                
                if not tile_ids:
                    log.warning("未能转换出有效的格子 ID")
                    if attempt < max_retries:
                        sleep(0.3)
                        continue
                    return False
                
                # 点击对应的格子
                log.info(f"点击格子 ID: {tile_ids}")
                success = self._click_tiles(tile_ids)
                
                if not success:
                    log.warning("点击格子失败")
                    if attempt < max_retries:
                        sleep(0.3)
                        continue
                    return False
                
                # 点击验证按钮
                sleep(1)
                verify_button = self.page.ele('css:#recaptcha-verify-button', timeout=3)
                if verify_button:
                    verify_button.click()
                    log.success("✅ 已点击验证按钮")
                    sleep(3)
                
                # 检查是否还有挑战
                new_challenge = self.page.ele('css:.rc-imageselect-challenge', timeout=2)
                if not new_challenge:
                    log.success("✅ 图片验证通过！")
                    return True
                else:
                    log.warning("验证失败，准备重试...")
                    sleep(2)
            
            log.error(f"图片验证失败，已尝试 {max_retries} 次")
            return False
            
        except Exception as e:
            log.error(f"直接模式图片验证处理失败: {e}")
            log.exception("直接模式图片验证异常详情")
            return False