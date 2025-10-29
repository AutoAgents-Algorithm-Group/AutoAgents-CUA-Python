import os
import urllib.request
import random
import pydub
import speech_recognition
import time
from typing import Optional
from DrissionPage import ChromiumPage, ChromiumOptions
from ..logging import logger, set_stage
from ...models import Stage


class GoogleRecaptchaSolver:
    """A class to solve Google reCAPTCHA challenges using audio recognition."""

    # Constants
    TEMP_DIR = os.getenv("TEMP") if os.name == "nt" else "/tmp"
    TIMEOUT_STANDARD = 7
    TIMEOUT_SHORT = 1
    TIMEOUT_DETECTION = 0.05

    def __init__(self, driver: ChromiumPage) -> None:
        """Initialize the solver with a ChromiumPage driver.

        Args:
            driver: ChromiumPage instance for browser interaction
        """
        self.driver = driver

    def solveCaptcha(self) -> None:
        """Attempt to solve the reCAPTCHA challenge.

        Raises:
            Exception: If captcha solving fails or bot is detected
        """
        log = set_stage(Stage.CAPTCHA)
        log.info("开始处理 Google reCAPTCHA 音频验证码")
        
        try:
            # Handle main reCAPTCHA iframe
            log.info("步骤1: 定位 reCAPTCHA iframe...")
            self.driver.wait.ele_displayed(
                "@title=reCAPTCHA", timeout=self.TIMEOUT_STANDARD
            )
            time.sleep(0.1)
            iframe_inner = self.driver("@title=reCAPTCHA")
            log.success("✅ 找到 reCAPTCHA iframe")

            # Click the checkbox
            log.info("步骤2: 点击 'I'm not a robot' 复选框...")
            iframe_inner.wait.ele_displayed(
                ".rc-anchor-content", timeout=self.TIMEOUT_STANDARD
            )
            iframe_inner(".rc-anchor-content", timeout=self.TIMEOUT_SHORT).click()
            log.success("✅ 已点击复选框")

            # Check if solved by just clicking
            if self.is_solved():
                log.success("🎉 验证码已通过，无需音频验证")
                return

            # Handle audio challenge
            log.info("步骤3: 启动音频验证...")
            iframe = self.driver("xpath://iframe[contains(@title, 'recaptcha')]")
            iframe.wait.ele_displayed(
                "#recaptcha-audio-button", timeout=self.TIMEOUT_STANDARD
            )
            iframe("#recaptcha-audio-button", timeout=self.TIMEOUT_SHORT).click()
            time.sleep(0.3)
            log.success("✅ 已点击音频按钮")

            if self.is_detected():
                log.error("❌ 检测到机器人行为")
                raise Exception("Captcha detected bot behavior")

            # Download and process audio
            log.info("步骤4: 获取音频源...")
            iframe.wait.ele_displayed("#audio-source", timeout=self.TIMEOUT_STANDARD)
            src = iframe("#audio-source").attrs["src"]
            log.success(f"✅ 获取音频源: {src}")

            log.info("步骤5: 处理音频验证...")
            text_response = self._process_audio_challenge(src)
            log.success(f"✅ 音频识别结果: {text_response}")
            
            log.info("步骤6: 提交验证结果...")
            iframe("#audio-response").input(text_response.lower())
            iframe("#recaptcha-verify-button").click()
            time.sleep(0.4)

            if not self.is_solved():
                log.error("❌ 验证码验证失败")
                raise Exception("Failed to solve the captcha")
            
            log.success("🎉 reCAPTCHA 音频验证成功！")

        except Exception as e:
            log.error(f"❌ reCAPTCHA 处理失败: {e}")
            log.exception("异常详情")
            raise Exception(f"Audio challenge failed: {str(e)}")

    def _process_audio_challenge(self, audio_url: str) -> str:
        """Process the audio challenge and return the recognized text.

        Args:
            audio_url: URL of the audio file to process

        Returns:
            str: Recognized text from the audio file
        """
        log = set_stage(Stage.CAPTCHA)
        mp3_path = os.path.join(self.TEMP_DIR, f"{random.randrange(1,1000)}.mp3")
        wav_path = os.path.join(self.TEMP_DIR, f"{random.randrange(1,1000)}.wav")

        try:
            log.info(f"正在下载音频文件: {audio_url}")
            urllib.request.urlretrieve(audio_url, mp3_path)
            log.success(f"✅ 音频文件已下载: {mp3_path}")
            
            log.info("正在转换音频格式...")
            sound = pydub.AudioSegment.from_mp3(mp3_path)
            sound.export(wav_path, format="wav")
            log.success(f"✅ 音频格式转换完成: {wav_path}")

            log.info("正在识别音频内容...")
            recognizer = speech_recognition.Recognizer()
            with speech_recognition.AudioFile(wav_path) as source:
                audio = recognizer.record(source)

            result = recognizer.recognize_google(audio)
            log.success(f"✅ 音频识别成功: {result}")
            return result

        except speech_recognition.UnknownValueError:
            log.error("❌ 无法识别音频内容")
            raise Exception("无法识别音频内容")
        except speech_recognition.RequestError as e:
            log.error(f"❌ 语音识别服务错误: {e}")
            raise Exception(f"语音识别服务错误: {e}")
        except Exception as e:
            log.error(f"❌ 音频处理失败: {e}")
            log.exception("音频处理异常详情")
            raise Exception(f"音频处理失败: {e}")
        finally:
            # 清理临时文件
            for path in (mp3_path, wav_path):
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        log.debug(f"已删除临时文件: {path}")
                    except OSError as e:
                        log.warning(f"删除临时文件失败: {path}, 错误: {e}")

    def is_solved(self) -> bool:
        """Check if the captcha has been solved successfully."""
        log = set_stage(Stage.CAPTCHA)
        try:
            result = (
                "style"
                in self.driver.ele(
                    ".recaptcha-checkbox-checkmark", timeout=self.TIMEOUT_SHORT
                ).attrs
            )
            if result:
                log.success("✅ 验证码已通过")
            else:
                log.info("验证码尚未通过")
            return result
        except Exception as e:
            log.debug(f"检查验证码状态失败: {e}")
            return False

    def is_detected(self) -> bool:
        """Check if the bot has been detected."""
        log = set_stage(Stage.CAPTCHA)
        try:
            result = (
                self.driver.ele("Try again later", timeout=self.TIMEOUT_DETECTION)
                .states()
                .is_displayed
            )
            if result:
                log.error("❌ 检测到机器人行为")
            return result
        except Exception:
            return False

    def get_token(self) -> Optional[str]:
        """Get the reCAPTCHA token if available."""
        log = set_stage(Stage.CAPTCHA)
        try:
            token = self.driver.ele("#recaptcha-token").attrs["value"]
            if token:
                log.success(f"✅ 获取到 reCAPTCHA token: {token[:20]}...")
            return token
        except Exception as e:
            log.debug(f"获取 reCAPTCHA token 失败: {e}")
            return None

    