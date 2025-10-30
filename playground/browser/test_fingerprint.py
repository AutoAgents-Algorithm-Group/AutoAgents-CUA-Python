import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagents_cua.utils import logger
from src.autoagents_cua.browser import WebOperator
from src.autoagents_cua.browser import BrowserFingerprint
from src.autoagents_cua.browser import FingerprintPool


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
    
    # 使用预设指纹 - 修正为Windows Chrome
    web = WebOperator(headless=False, fingerprint_config='windows_chrome')
    
    # 显示当前指纹信息
    fingerprint = web.get_fingerprint_info()
    logger.info(f"指纹名称: {fingerprint.get('name')}")
    logger.info(f"User-Agent: {fingerprint.get('user_agent')[:50]}...")
    logger.info(f"平台: {fingerprint.get('platform')}")
    logger.info(f"屏幕: {fingerprint.get('screen')}")
    
    # 显示Client Hints配置
    client_hints = fingerprint.get('client_hints', {})
    if client_hints:
        logger.info("\n🎯 Client Hints 配置:")
        logger.info(f"  Sec-CH-UA-Platform: {client_hints.get('Sec-CH-UA-Platform')}")
        logger.info(f"  Sec-CH-UA-Mobile: {client_hints.get('Sec-CH-UA-Mobile')}")
        logger.info(f"  Sec-CH-UA: {client_hints.get('Sec-CH-UA')[:50]}...")
    
    # 执行指纹验证
    logger.info("\n🔍 验证指纹修改效果...")
    verification_result = web.verify_fingerprint()
    if verification_result and verification_result.get('clientHints'):
        ch = verification_result['clientHints']
        if ch.get('available'):
            logger.success("✅ Client Hints 修改成功!")
            logger.info(f"  Platform: {ch.get('platform')}")
            logger.info(f"  Mobile: {ch.get('mobile')}")
            logger.info(f"  Brands: {ch.get('brands')}")
        else:
            logger.warning("⚠️  Client Hints 不可用")
    
    # 访问检测网站
    logger.info("\n🌐 正在访问指纹检测网站...")
    web.navigate(FINGERPRINT_TEST_SITES['fingerprintjs'])
    
    input("\n📊 查看Client Hints检测结果，按回车键继续测试 Canvas 指纹...")
    web.navigate(FINGERPRINT_TEST_SITES['browserleaks_canvas'])
    
    input("\n🎨 查看Canvas指纹，按回车键继续测试 WebGL 指纹...")
    web.navigate(FINGERPRINT_TEST_SITES['browserleaks_webgl'])
    
    input("\n🖥️  查看WebGL指纹，按回车键关闭浏览器...")
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
    """测试自定义指纹配置 - SDK 模式"""
    logger.info("=" * 60)
    logger.info("测试 3: 使用自定义指纹配置（SDK 模式）")
    logger.info("=" * 60)
    
    # 自定义指纹配置（直接传入字典）
    fingerprint_config = BrowserFingerprint.get_preset('windows_chrome')
    
    logger.info(f"使用指纹配置: {fingerprint_config.get('name')}")
    
    # 使用自定义指纹
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


def test_client_hints_focus():
    """专门测试Client Hints修复效果"""
    logger.info("=" * 60)
    logger.info("测试 6: Client Hints 修复效果专项测试")
    logger.info("=" * 60)
    
    # 使用Windows Chrome测试Client Hints
    web = WebOperator(headless=False, fingerprint_config='windows_chrome')
    
    # 显示预期配置
    fingerprint = web.get_fingerprint_info()
    client_hints = fingerprint.get('client_hints', {})
    
    logger.info("📋 预期的 Client Hints 配置:")
    for key, value in client_hints.items():
        logger.info(f"  {key}: {value}")
    
    # 执行详细验证
    logger.info("\n🔍 执行详细验证...")
    verification_result = web.verify_fingerprint()
    
    if verification_result:
        ch = verification_result.get('clientHints', {})
        if ch.get('available'):
            logger.success("✅ navigator.userAgentData 可用")
            logger.info(f"  实际 Platform: {ch.get('platform')}")
            logger.info(f"  实际 Mobile: {ch.get('mobile')}")
            logger.info(f"  实际 Brands: {ch.get('brands')}")
            
            # 对比预期值
            expected_platform = client_hints.get('Sec-CH-UA-Platform', '').replace('"', '')
            actual_platform = ch.get('platform', '')
            
            if expected_platform.lower() == actual_platform.lower():
                logger.success("✅ Platform 匹配成功!")
            else:
                logger.warning(f"⚠️  Platform 不匹配: 预期 '{expected_platform}' vs 实际 '{actual_platform}'")
        else:
            logger.error("❌ Client Hints 修改失败")
    
    # 测试不同网站的检测效果
    test_sites = [
        ('uutool.cn', FINGERPRINT_TEST_SITES['fingerprintjs']),
        ('httpbin.org', 'https://httpbin.org/headers'),
        ('whatismybrowser', 'https://www.whatismybrowser.com/')
    ]
    
    for site_name, url in test_sites:
        logger.info(f"\n🌐 测试网站: {site_name}")
        try:
            web.navigate(url)
            input(f"查看 {site_name} 的 Client Hints 检测结果，按回车键继续...")
        except Exception as e:
            logger.warning(f"访问 {site_name} 失败: {e}")
    
    web.close()
    logger.success("测试 6 完成！\n")


def test_all_presets():
    """测试所有预设指纹"""
    logger.info("=" * 60)
    logger.info("测试 7: 测试所有预设指纹")
    logger.info("=" * 60)
    
    presets = BrowserFingerprint.list_presets()
    logger.info(f"可用的预设: {presets}")
    
    for preset_name in presets:
        logger.info(f"\n正在测试预设: {preset_name}")
        
        fingerprint = BrowserFingerprint.get_preset(preset_name)
        logger.info(f"  - 名称: {fingerprint.get('name')}")
        logger.info(f"  - User-Agent: {fingerprint.get('user_agent')[:60]}...")
        
        # 显示Client Hints配置
        client_hints = fingerprint.get('client_hints', {})
        if client_hints:
            logger.info(f"  - Client Hints Platform: {client_hints.get('Sec-CH-UA-Platform')}")
        
        web = WebOperator(headless=False, fingerprint_config=preset_name)
        web.navigate(FINGERPRINT_TEST_SITES['deviceinfo'])
        
        input(f"\n按回车键测试下一个预设...")
        web.close()
    
    logger.success("测试 7 完成！\n")


def main():
    """主测试函数 - SDK 模式"""
    logger.info("🎭 浏览器指纹修改功能测试 - SDK 模式")
    logger.info("=" * 60)
    
    tests = {
        '1': ('测试预设指纹 (Windows Chrome)', test_preset_fingerprint),
        '2': ('测试随机指纹生成', test_random_fingerprint),
        '3': ('测试自定义指纹配置', test_config_fingerprint),
        '4': ('测试指纹池', test_fingerprint_pool),
        '5': ('对比测试（无指纹 vs 有指纹）', test_comparison),
        '6': ('🎯 Client Hints 修复效果专项测试', test_client_hints_focus),
        '7': ('测试所有预设指纹', test_all_presets),
        '0': ('运行所有测试', None),
    }
    
    print("\n请选择测试项:")
    for key, (desc, _) in tests.items():
        print(f"  {key}. {desc}")
    
    print("\n💡 推荐:")
    print("  - 选择 6 来专门测试 Client Hints 修复效果")
    print("  - 选择 1 来测试完整的指纹修改功能")
    
    choice = input("\n请输入选项 (1-7, 0=全部): ").strip()
    
    if choice == '0':
        # 运行所有测试
        for key in ['1', '2', '3', '4', '5', '6', '7']:
            tests[key][1]()
            if key != '7':
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

