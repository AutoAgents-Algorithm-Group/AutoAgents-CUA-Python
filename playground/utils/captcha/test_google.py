from DrissionPage import ChromiumPage, ChromiumOptions
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.captcha_solver.google import GoogleRecaptchaSolver
import time

CHROME_ARGUMENTS = [
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
for argument in CHROME_ARGUMENTS:
    options.set_argument(argument)
    
driver = ChromiumPage(addr_or_opts=options)
recaptchaSolver = GoogleRecaptchaSolver(driver)

driver.get("https://www.google.com/recaptcha/api2/demo")

t0 = time.time()
recaptchaSolver.solveCaptcha()
print(f"Time to solve the captcha: {time.time()-t0:.2f} seconds")

driver.ele("#recaptcha-demo-submit").click()

# driver.close()

