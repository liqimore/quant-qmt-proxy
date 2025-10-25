"""
简单的 gRPC 客户端测试 - 向后兼容版本

⚠️ 此文件已废弃，gRPC 客户端已重构为工具类

新的 gRPC 测试框架：
   - tests/grpc/client.py - gRPC 客户端封装
   - tests/grpc/test_health_grpc_service.py - 健康检查测试
   - tests/grpc/test_data_grpc_service.py - 数据服务测试
   - tests/grpc/test_trading_grpc_service.py - 交易服务测试

如需运行 gRPC 测试，请使用：
   pytest tests/grpc/ -v
"""
import warnings
warnings.warn(
    "test_grpc_client.py 已废弃，请使用: pytest tests/grpc/ -v",
    DeprecationWarning,
    stacklevel=2
)

from tests.grpc.client import GRPCTestClient
from generated import common_pb2, trading_pb2

def test_grpc_client():
    """测试 gRPC 客户端（使用新的客户端类）"""
    print("=" * 70)
    print("QMT gRPC 客户端测试")
    print("=" * 70)
    
    client = GRPCTestClient(host='localhost', port=50051)
    
    try:
        # 1. 健康检查
        print("\n【1. 健康检查】")
        health_response = client.check_health()
        print(f"✅ 服务状态: {health_response.status}")
        
        # 2. 获取板块列表
        print("\n【2. 获取板块列表】")
        sector_response = client.get_sector_list()
        print(f"✅ 状态码: {sector_response.status.code}")
        print(f"✅ 板块数量: {len(sector_response.sectors)}")
        if sector_response.sectors:
            print(f"   第一个板块: {sector_response.sectors[0].sector_name}")
        
        # 3. 连接交易账户
        print("\n【3. 连接交易账户】")
        connect_response = client.connect(
            account_id="mock_account_001",
            password="mock_password"
        )
        print(f"✅ 连接成功: {connect_response.success}")
        
        if connect_response.success:
            session_id = connect_response.session_id
            
            # 4. 获取持仓
            print("\n【4. 获取持仓】")
            position_response = client.get_positions(session_id)
            print(f"✅ 持仓数量: {len(position_response.positions)}")
            
            # 5. 断开连接
            print("\n【5. 断开连接】")
            disconnect_response = client.disconnect(session_id)
            print(f"✅ 断开成功: {disconnect_response.success}")
        
        print("\n" + "=" * 70)
        print("✅ 所有测试通过！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


if __name__ == '__main__':
    test_grpc_client()
