#!/usr/bin/env python3
"""
TikTok 循环操作测试文件
多轮循环操作：点击头像 -> 点击私信 -> 返回 -> 返回 -> 向下滚轮
"""

import sys
import signal

# 添加项目根目录到Python路径
sys.path.insert(0, '/Users/forhheart/AIGC/AutoAgents-CUA-Python/src')

from autoagents_cua.prebuilt.tiktok_manager import TikTokManager


def signal_handler(sig, frame):
    """处理Ctrl+C信号"""
    print('\n⏹️  接收到中断信号，正在停止...')
    sys.exit(0)


def main():
    """主函数 - 多轮循环操作"""
    print("🎯 TikTok 多轮循环操作")
    print("=" * 40)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    # 获取循环次数参数
    if len(sys.argv) > 1:
        try:
            cycle_count = int(sys.argv[1])
            if cycle_count <= 0:
                cycle_count = -1  # 无限循环
        except ValueError:
            print("❌ 循环次数必须是数字")
            print("使用方法: python test_cycle_operations.py [循环次数]")
            print("  循环次数 <= 0 或不指定 = 无限循环")
            print("  示例: python test_cycle_operations.py 10")
            return False
    else:
        cycle_count = -1  # 默认无限循环
    
    # 创建TikTok管理器
    manager = TikTokManager()
    
    if not manager.is_connected:
        print("❌ 设备连接失败，无法进行测试")
        return False
    
    # 启动应用并处理弹窗
    print("\n🚀 启动TikTok应用...")
    if not manager.start_app():
        print("❌ 应用启动失败")
        return False
    
    print("🔍 处理弹窗...")
    manager.handle_popups()
    
    # 检查登录状态
    if manager.check_login_required():
        print("⚠️  需要登录，请先登录后重新运行")
        return False
    
    # 确认在视频页面
    if not manager.is_video_page():
        print("⚠️  可能不在视频页面，继续尝试...")
    else:
        print("✓ 确认在视频页面")
    
    # 显示运行信息
    if cycle_count > 0:
        print(f"\n🎯 开始多轮循环操作 (目标: {cycle_count} 次)")
    else:
        print("\n🎯 开始无限循环操作")
        print("💡 提示: 按 Ctrl+C 可以随时停止循环")
    
    print("🔄 循环流程: 点击头像 → 点击私信 → 返回 → 返回 → 向下滚轮")
    print("=" * 60)
    
    # 运行多轮循环
    try:
        stats = manager.run_continuous_cycle(
            cycle_count=cycle_count, 
            max_errors=3  # 最大连续错误次数
        )
        
        print("\n✅ 循环操作完成")
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️  用户中断循环")
        return True
    except Exception as e:
        print(f"\n❌ 循环过程中发生错误: {e}")
        return False


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️  程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序执行错误: {e}")
        sys.exit(1)

