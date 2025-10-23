"""
启动FastAPI应用并运行测试
"""
import subprocess
import time
import sys
import os
import signal

def check_port_in_use(port=8000):
    """检查端口是否被占用"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main():
    print("=" * 80)
    print("🚀 FastAPI应用启动和测试流程")
    print("=" * 80)
    
    # 检查端口是否已被占用
    if check_port_in_use(8000):
        print("\n⚠️  端口8000已被占用")
        response = input("是否要继续？(y/n): ")
        if response.lower() != 'y':
            print("测试已取消")
            return 1
    
    # 设置环境变量
    os.environ["ENVIRONMENT"] = "dev"
    
    print("\n📋 步骤1: 启动FastAPI应用")
    print("-" * 80)
    print("启动命令: python start.py --env dev")
    print("等待服务启动...")
    
    # 启动FastAPI应用
    app_process = subprocess.Popen(
        [sys.executable, "start.py", "--env", "dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # 等待服务启动
    max_wait = 30
    waited = 0
    service_ready = False
    
    print("\n等待服务启动", end="", flush=True)
    while waited < max_wait:
        time.sleep(1)
        waited += 1
        print(".", end="", flush=True)
        
        if check_port_in_use(8000):
            service_ready = True
            print(" ✅")
            break
    
    if not service_ready:
        print(" ❌")
        print("\n❌ 服务启动失败或超时")
        app_process.terminate()
        return 1
    
    print(f"\n✅ FastAPI服务已启动 (等待 {waited} 秒)")
    print(f"服务地址: http://localhost:8000")
    print(f"API文档: http://localhost:8000/docs")
    
    # 额外等待一点时间确保完全就绪
    time.sleep(2)
    
    try:
        # 运行测试
        print("\n📋 步骤2: 运行API测试")
        print("-" * 80)
        
        test_process = subprocess.run(
            [sys.executable, "test_fastapi_app.py"],
            timeout=60
        )
        
        test_result = test_process.returncode
        
    except subprocess.TimeoutExpired:
        print("\n⚠️  测试超时")
        test_result = 1
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        test_result = 1
    finally:
        # 停止FastAPI应用
        print("\n📋 步骤3: 停止FastAPI应用")
        print("-" * 80)
        
        try:
            app_process.terminate()
            app_process.wait(timeout=5)
            print("✅ FastAPI应用已停止")
        except subprocess.TimeoutExpired:
            print("⚠️  正常停止超时，强制终止")
            app_process.kill()
            print("✅ FastAPI应用已强制停止")
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 测试流程完成")
    print("=" * 80)
    
    if test_result == 0:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败，请查看上面的详细信息")
    
    return test_result

if __name__ == "__main__":
    sys.exit(main())
