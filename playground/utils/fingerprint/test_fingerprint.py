"""
浏览器指纹测试脚本 - 测试指纹修改功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils import (
    WebOperator, 
    BrowserFingerprint, 
    FingerprintPool,
    ConfigLoader,
    logger
)


# 指纹检测网站
FINGERPRINT_TEST_SITES = {
    'fingerprintjs': 'https://uutool.cn/browser/',
    'browserleaks_canvas': 'https://browserleaks.com/canvas',
    'browserleaks_webgl': 'https://browserleaks.com/webgl',
    'browserleaks_fonts': 'https://browserleaks.com/fonts',
    'pixelscan': 'https://pixelscan.net/',
    'creepjs': 'https://abrahamjuliot.github.io/creepjs/',
    'deviceinfo': 'https://www.deviceinfo.me/',
    'whoer': 'https://whoer.net/',
}


def test_preset_fingerprint():
    """测试预设指纹"""
    logger.info("=" * 60)
    logger.info("测试 1: 使用预设指纹 (Windows Chrome)")
    logger.info("=" * 60)
    
    # 使用预设指纹
    web = WebOperator(headless=False, fingerprint_config='linux_chrome')
    
    # 显示当前指纹信息
    fingerprint = web.get_fingerprint_info()
    logger.info(f"指纹名称: {fingerprint.get('name')}")
    logger.info(f"User-Agent: {fingerprint.get('user_agent')[:50]}...")
    logger.info(f"平台: {fingerprint.get('platform')}")
    logger.info(f"屏幕: {fingerprint.get('screen')}")
    
    # 访问检测网站
    logger.info("\n正在访问指纹检测网站...")
    web.navigate(FINGERPRINT_TEST_SITES['fingerprintjs'])
    
    input("\n按回车键继续测试 Canvas 指纹...")
    web.navigate(FINGERPRINT_TEST_SITES['browserleaks_canvas'])
    
    input("\n按回车键继续测试 WebGL 指纹...")
    web.navigate(FINGERPRINT_TEST_SITES['browserleaks_webgl'])
    
    input("\n按回车键关闭浏览器...")
    web.close()
    logger.success("测试 1 完成！\n")


def test_random_fingerprint():
    """测试随机指纹"""
    logger.info("=" * 60)
    logger.info("测试 2: 使用随机生成的指纹")
    logger.info("=" * 60)
    
    # 生成随机指纹
    fingerprint = BrowserFingerprint.generate_random_fingerprint(
        platform_pool=['windows_chrome', 'mac_chrome', 'windows_edge'],
        add_noise=True
    )
    
    logger.info(f"随机生成的指纹:")
    logger.info(f"  - 名称: {fingerprint.get('name')}")
    logger.info(f"  - 平台: {fingerprint.get('platform')}")
    logger.info(f"  - 屏幕: {fingerprint.get('screen')}")
    logger.info(f"  - CPU 核心数: {fingerprint.get('hardware_concurrency')}")
    logger.info(f"  - 内存: {fingerprint.get('device_memory')} GB")
    
    # 使用随机指纹
    web = WebOperator(headless=False, fingerprint_config=fingerprint)
    
    # 访问检测网站
    web.navigate(FINGERPRINT_TEST_SITES['whoer'])
    
    input("\n按回车键关闭浏览器...")
    web.close()
    logger.success("测试 2 完成！\n")


def test_config_fingerprint():
    """测试从配置文件加载指纹"""
    logger.info("=" * 60)
    logger.info("测试 3: 从配置文件加载指纹")
    logger.info("=" * 60)
    
    # 从配置文件加载
    config = ConfigLoader()
    fingerprint_config = config.get_browser_fingerprint_config()
    
    if fingerprint_config is None:
        logger.warning("配置文件中未启用指纹功能")
        return
    
    logger.info(f"从配置加载的指纹类型: {type(fingerprint_config).__name__}")
    
    # 使用配置文件中的指纹
    web = WebOperator(headless=False, fingerprint_config=fingerprint_config)
    
    # 访问检测网站
    web.navigate(FINGERPRINT_TEST_SITES['pixelscan'])
    
    input("\n按回车键关闭浏览器...")
    web.close()
    logger.success("测试 3 完成！\n")


def test_fingerprint_pool():
    """测试指纹池"""
    logger.info("=" * 60)
    logger.info("测试 4: 使用指纹池")
    logger.info("=" * 60)
    
    # 创建指纹池（10个指纹）
    pool = FingerprintPool(pool_size=5, platform_pool=['windows_chrome', 'mac_chrome'])
    logger.info(f"指纹池大小: {pool.size()}")
    
    # 从池中获取随机指纹
    for i in range(3):
        fingerprint = pool.get_next()
        logger.info(f"\n指纹 {i+1}: {fingerprint.get('name')}")
        logger.info(f"  - 平台: {fingerprint.get('platform')}")
        logger.info(f"  - 屏幕: {fingerprint.get('screen')['width']}x{fingerprint.get('screen')['height']}")
        
        web = WebOperator(headless=False, fingerprint_config=fingerprint)
        web.navigate(FINGERPRINT_TEST_SITES['fingerprintjs'])
        
        input(f"\n按回车键测试下一个指纹 ({i+1}/3)...")
        web.close()
    
    logger.success("测试 4 完成！\n")


def test_comparison():
    """对比测试：无指纹 vs 有指纹"""
    logger.info("=" * 60)
    logger.info("测试 5: 对比测试（无指纹 vs 有指纹）")
    logger.info("=" * 60)
    
    # 测试 1: 不使用指纹
    logger.info("\n[1] 不使用指纹修改...")
    web1 = WebOperator(headless=False, fingerprint_config=None)
    web1.navigate(FINGERPRINT_TEST_SITES['creepjs'])
    
    input("\n观察结果，然后按回车键继续...")
    web1.close()
    
    # 测试 2: 使用指纹
    logger.info("\n[2] 使用指纹修改...")
    web2 = WebOperator(headless=False, fingerprint_config='mac_safari')
    web2.navigate(FINGERPRINT_TEST_SITES['creepjs'])
    
    input("\n观察两次结果的差异，然后按回车键关闭...")
    web2.close()
    
    logger.success("测试 5 完成！\n")


def test_all_presets():
    """测试所有预设指纹"""
    logger.info("=" * 60)
    logger.info("测试 6: 测试所有预设指纹")
    logger.info("=" * 60)
    
    presets = BrowserFingerprint.list_presets()
    logger.info(f"可用的预设: {presets}")
    
    for preset_name in presets:
        logger.info(f"\n正在测试预设: {preset_name}")
        
        fingerprint = BrowserFingerprint.get_preset(preset_name)
        logger.info(f"  - 名称: {fingerprint.get('name')}")
        logger.info(f"  - User-Agent: {fingerprint.get('user_agent')[:60]}...")
        
        web = WebOperator(headless=False, fingerprint_config=preset_name)
        web.navigate(FINGERPRINT_TEST_SITES['deviceinfo'])
        
        input(f"\n按回车键测试下一个预设...")
        web.close()
    
    logger.success("测试 6 完成！\n")


def main():
    """主测试函数"""
    logger.info("🎭 浏览器指纹修改功能测试")
    logger.info("=" * 60)
    
    tests = {
        '1': ('测试预设指纹 (Windows Chrome)', test_preset_fingerprint),
        '2': ('测试随机指纹生成', test_random_fingerprint),
        '3': ('测试从配置文件加载', test_config_fingerprint),
        '4': ('测试指纹池', test_fingerprint_pool),
        '5': ('对比测试（无指纹 vs 有指纹）', test_comparison),
        '6': ('测试所有预设指纹', test_all_presets),
        '0': ('运行所有测试', None),
    }
    
    print("\n请选择测试项:")
    for key, (desc, _) in tests.items():
        print(f"  {key}. {desc}")
    
    choice = input("\n请输入选项 (1-6, 0=全部): ").strip()
    
    if choice == '0':
        # 运行所有测试
        for key in ['1', '2', '3', '4', '5', '6']:
            tests[key][1]()
            if key != '6':
                input("\n按回车键继续下一个测试...")
    elif choice in tests and choice != '0':
        tests[choice][1]()
    else:
        logger.error("无效的选项！")
        return
    
    logger.success("\n" + "=" * 60)
    logger.success("所有测试完成！")
    logger.success("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n\n用户中断测试")
    except Exception as e:
        logger.error(f"\n\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

