#!/usr/bin/env python3
"""
Client Hints 最终测试脚本
直接测试修改后的 Client Hints 效果
"""

import os
import sys
import time
import json

# 确保项目根目录在sys.path中
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.autoagents_cua.utils import logger
from src.autoagents_cua.browser import WebOperator, BrowserFingerprint

def test_client_hints_final():
    """最终 Client Hints 测试"""
    logger.info("=" * 60)
    logger.info("🎯 Client Hints 最终效果测试")
    logger.info("=" * 60)
    
    web = None
    try:
        # 1. 获取预设指纹
        fingerprint = BrowserFingerprint.get_preset('windows_chrome')
        if not fingerprint:
            logger.error("❌ 无法获取 windows_chrome 预设指纹")
            return
        
        client_hints = fingerprint.get('client_hints', {})
        logger.info("🔧 目标 Client Hints 配置:")
        for key, value in client_hints.items():
            logger.info(f"   {key}: {value}")
        
        # 2. 启动浏览器
        logger.info("\n🚀 启动浏览器 (WebOperator)...")
        web = WebOperator(headless=False, fingerprint_config=fingerprint)
        logger.success("✅ 浏览器启动成功")
        
        # 3. 等待初始化完成
        logger.info("⏱️  等待 Client Hints 设置生效...")
        time.sleep(3)
        
        # 4. 直接访问httpbin测试HTTP头
        logger.info("\n🌐 访问 httpbin.org/headers 检查HTTP头...")
        web.navigate('https://httpbin.org/headers')
        time.sleep(3)
        
        # 5. 执行JavaScript验证
        logger.info("\n🔍 执行 JavaScript Client Hints 验证...")
        js_check_script = """
        (function() {
            const result = {
                available: !!navigator.userAgentData,
                platform: navigator.userAgentData ? navigator.userAgentData.platform : 'N/A',
                mobile: navigator.userAgentData ? navigator.userAgentData.mobile : 'N/A',
                brands: navigator.userAgentData ? navigator.userAgentData.brands : 'N/A'
            };
            
            console.log('🔍 Client Hints JavaScript 验证:', result);
            return result;
        })();
        """
        
        try:
            js_result = web.page.run_script(js_check_script)
            logger.info("📋 JavaScript Client Hints 结果:")
            logger.info(f"   可用: {js_result.get('available')}")
            logger.info(f"   平台: {js_result.get('platform')}")
            logger.info(f"   移动设备: {js_result.get('mobile')}")
            logger.info(f"   品牌: {js_result.get('brands')}")
            
            # 检查平台是否正确
            expected_platform = client_hints.get('Sec-CH-UA-Platform', '"Windows"').strip('"')
            actual_platform = js_result.get('platform', '')
            if actual_platform.lower() == expected_platform.lower():
                logger.success(f"✅ JavaScript API 平台验证成功: {actual_platform}")
            else:
                logger.warning(f"⚠️  JavaScript API 平台不匹配: 期望 {expected_platform}, 实际 {actual_platform}")
        except Exception as e:
            logger.error(f"❌ JavaScript 验证失败: {e}")
        
        # 6. 提示用户查看结果
        print("\n" + "="*60)
        print("📋 请在浏览器中查看以下内容:")
        print("1. httpbin.org 页面中的 'Sec-Ch-Ua-Platform' 头部")
        print("2. 检查是否显示为 'Windows' 而不是 'macOS'")
        print("3. 查看浏览器控制台的 Client Hints 相关日志")
        print("="*60)
        
        # 7. 等待用户确认
        input("按回车键继续测试其他网站...")
        
        # 8. 测试uutool网站
        logger.info("\n🌐 访问 uutool.cn/browser/ 进行综合检测...")
        web.navigate('https://uutool.cn/browser/')
        time.sleep(3)
        
        print("\n" + "="*60)
        print("📋 请在 uutool.cn 页面中查看:")
        print("1. 'Client Hints' 部分的平台信息")
        print("2. 是否显示为 'Windows' 而不是 'macOS'")
        print("3. 其他 Client Hints 信息是否正确")
        print("="*60)
        
        input("检查完成后按回车键结束测试...")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if web:
            try:
                web.close()
                logger.info("🔒 浏览器已关闭")
            except:
                pass
        
        logger.success("\n" + "="*60)
        logger.success("🎉 Client Hints 最终测试完成")
        logger.success("="*60)

if __name__ == '__main__':
    test_client_hints_final()
