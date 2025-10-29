import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.autoagents_web.utils.captcha_solver.google import GoogleRecaptchaSolver

from DrissionPage import ChromiumPage, ChromiumOptions
import time

def solve_google_recaptcha_v2_audio(url="https://www.google.com/recaptcha/api2/demo", chrome_arguments=None,driver=None):
        """
        识别 reCAPTCHA 音频验证码
        
        Args:
            url: 音频验证码的 URL
            chrome_arguments: Chrome 浏览器启动参数，默认为 None 时使用预设参数
            ChromiumPage: 浏览器实例
        
        returns:
            ChromiumPage: 浏览器实例
            
        """
        # 默认 Chrome 启动参数
        if chrome_arguments is None:
            chrome_arguments = [
                "-no-first-run",
                "-force-color-profile=srgb",
                "-metrics-recording-only",
                "-password-store=basic",
                "-use-mock-keychain",
                "-export-tagged-pdf",
                "-no-default-browser-check",
                "-disable-background-mode",
                "-enable-features=NetworkService,NetworkServiceInProcess",
                "-disable-features=FlashDeprecationWarning",
                "-deny-permission-prompts",
                "-disable-gpu",
                "-accept-lang=en-US",
                "--disable-usage-stats",
                "--disable-crash-reporter",
                "--no-sandbox"
            ]
        
        
        options = ChromiumOptions()
        for argument in chrome_arguments:
            options.set_argument(argument)
        if driver == None:   # 如果没有实例就新建，有则使用传入的实例
            driver = ChromiumPage(addr_or_opts=options)
        
        recaptchaSolver = GoogleRecaptchaSolver(driver)

        driver.get(url)

        t0 = time.time()
        try:
            recaptchaSolver.solveCaptcha()
            print(f"Time to solve the captcha: {time.time()-t0:.2f} seconds")
            
            # 尝试点击提交按钮
            submit_button = driver.ele("#recaptcha-demo-submit", timeout=5)
            if submit_button:
                submit_button.click()
                print("已点击提交按钮")
            else:
                print("未找到提交按钮")
            
        except Exception as e:
            print(f"验证码处理失败: {e}")
            print("这可能是由于以下原因：")
            print("1. 网络连接问题")
            print("2. 音频质量不好")
            print("3. Google 语音识别服务暂时不可用")
            print("4. 验证码类型不支持音频识别")
            
            # 即使失败也返回驱动实例，让用户可以手动处理
            return driver
        
        # 返回已经通过人机验证的实例
        return driver 


  
    
if __name__ == '__main__':
     solve_google_recaptcha_v2_audio()