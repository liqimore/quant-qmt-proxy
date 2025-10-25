"""
FastAPI应用完整测试脚本 - 向后兼容版本

⚠️ 此文件已废弃，请使用新的测试框架：
   - pytest tests/rest/ -v

此文件保留用于向后兼容，实际测试已迁移到：
   - tests/rest/test_health_api.py
   - tests/rest/test_data_api.py
   - tests/rest/test_trading_api.py

如需运行完整测试，请使用：
   pytest tests/rest/ -v
"""
import warnings
warnings.warn(
    "test_fastapi_app.py 已废弃，请使用: pytest tests/rest/ -v",
    DeprecationWarning,
    stacklevel=2
)

import httpx
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000"

# API密钥（从config_dev.yml中获取）
API_KEY = "dev-api-key-001"

# 测试结果统计
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": []
}

def print_header(title: str):
    """打印测试标题"""
    print("\n" + "=" * 80)
    print(f"📋 {title}")
    print("=" * 80)

def test_api(name: str, method: str, endpoint: str, data: Dict[str, Any] = None) -> tuple[bool, Dict[str, Any]]:
    """测试API端点，返回(成功与否, 响应数据)"""
    test_results["total"] += 1
    url = f"{BASE_URL}{endpoint}"
    
    try:
        print(f"\n🔍 测试: {name}")
        print(f"   方法: {method}")
        print(f"   端点: {endpoint}")
        if data:
            print(f"   请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # 准备请求头（使用Bearer Token）
        headers = {"Authorization": f"Bearer {API_KEY}"}
        
        with httpx.Client() as client:
            if method.upper() == "GET":
                response = client.get(url, headers=headers, timeout=60)
            elif method.upper() == "POST":
                response = client.post(url, json=data, headers=headers, timeout=60)
            else:
                print(f"   ❌ 不支持的HTTP方法: {method}")
                test_results["failed"] += 1
                return False, {}
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 成功")
                
                # 显示部分响应数据
                if "data" in result:
                    data_str = json.dumps(result["data"], ensure_ascii=False, indent=2)
                    if len(data_str) > 500:
                        print(f"   响应数据: {data_str[:500]}... (已截断)")
                    else:
                        print(f"   响应数据: {data_str}")
                
                test_results["passed"] += 1
                return True, result
            else:
                print(f"   ❌ 失败: HTTP {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                test_results["failed"] += 1
                test_results["errors"].append({
                    "test": name,
                    "error": f"HTTP {response.status_code}",
                    "response": response.text[:200]
                })
                return False, {}
            
    except httpx.ConnectError:
        print(f"   ❌ 连接失败: 无法连接到 {BASE_URL}")
        print(f"   💡 请确保FastAPI应用正在运行")
        test_results["failed"] += 1
        test_results["errors"].append({
            "test": name,
            "error": "连接失败",
            "message": "FastAPI应用未启动"
        })
        return False, {}
    except Exception as e:
        print(f"   ❌ 异常: {str(e)}")
        test_results["failed"] += 1
        test_results["errors"].append({
            "test": name,
            "error": str(e)
        })
        return False, {}

def main():
    print("=" * 80)
    print("🚀 FastAPI应用完整测试")
    print("=" * 80)
    print(f"API基础URL: {BASE_URL}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查服务是否可访问
    print_header("1. 系统健康检查")
    test_api("根路径", "GET", "/")
    test_api("应用信息", "GET", "/info")
    test_api("健康检查", "GET", "/health/")
    test_api("就绪检查", "GET", "/health/ready")
    test_api("存活检查", "GET", "/health/live")
    
    # 测试数据服务API
    print_header("2. 数据服务API测试")
    
    # 2.1 获取市场数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)
    market_data_request = {
        "stock_codes": ["000001.SZ", "600000.SH"],
        "start_date": start_date.strftime("%Y%m%d"),
        "end_date": end_date.strftime("%Y%m%d"),
        "period": "1d",
        "fields": ["time", "open", "high", "low", "close", "volume"]
    }
    test_api("获取市场数据", "POST", "/api/v1/data/market", market_data_request)
    
    # 2.2 获取板块列表
    test_api("获取板块列表", "GET", "/api/v1/data/sectors")
    
    # 2.3 获取板块股票
    sector_request = {
        "sector_name": "银行"
    }
    test_api("获取板块股票", "POST", "/api/v1/data/sector", sector_request)
    
    # 2.4 获取指数权重
    index_weight_request = {
        "index_code": "000300.SH",
        "date": None
    }
    test_api("获取指数权重", "POST", "/api/v1/data/index-weight", index_weight_request)
    
    # 2.5 获取交易日历
    year = datetime.now().year
    test_api(f"获取{year}年交易日历", "GET", f"/api/v1/data/trading-calendar/{year}")
    
    # 2.6 获取合约信息
    test_api("获取合约信息-000001.SZ", "GET", "/api/v1/data/instrument/000001.SZ")
    test_api("获取合约信息-600000.SH", "GET", "/api/v1/data/instrument/600000.SH")
    
    # 2.7 获取财务数据
    financial_data_request = {
        "stock_codes": ["000001.SZ"],
        "table_list": ["Capital"],
        "start_date": "20230101",
        "end_date": "20241231"
    }
    test_api("获取财务数据", "POST", "/api/v1/data/financial", financial_data_request)
    
    # 测试交易服务API
    print_header("3. 交易服务API测试")
    
    # 3.1 连接交易账户
    connect_request = {
        "account_id": "test_account_001",
        "password": "test_password",
        "account_type": "SECURITY"
    }
    success, connect_response = test_api("连接交易账户", "POST", "/api/v1/trading/connect", connect_request)
    
    # 如果连接成功，继续测试其他交易接口
    if success:
        # 从响应中提取真实的session_id
        # ConnectResponse字段在根级别，不在data字段下
        session_id = "test_session"  # 默认值
        if "session_id" in connect_response:
            session_id = connect_response["session_id"]
            print(f"   📝 提取到session_id: {session_id}")
        else:
            print(f"   ⚠️  未能提取session_id，使用默认值: {session_id}")
            print(f"   响应结构: {list(connect_response.keys())}")
        
        # 3.2 获取账户信息
        test_api("获取账户信息", "GET", f"/api/v1/trading/account/{session_id}")
        
        # 3.3 获取持仓信息
        test_api("获取持仓信息", "GET", f"/api/v1/trading/positions/{session_id}")
        
        # 3.4 获取资产信息
        test_api("获取资产信息", "GET", f"/api/v1/trading/asset/{session_id}")
        
        # 3.5 获取风险信息
        test_api("获取风险信息", "GET", f"/api/v1/trading/risk/{session_id}")
        
        # 3.6 获取策略列表
        test_api("获取策略列表", "GET", f"/api/v1/trading/strategies/{session_id}")
        
        # 3.7 获取订单列表
        test_api("获取订单列表", "GET", f"/api/v1/trading/orders/{session_id}")
        
        # 3.8 获取成交记录
        test_api("获取成交记录", "GET", f"/api/v1/trading/trades/{session_id}")
        
        # 3.9 提交订单（注意：这会真实提交订单，谨慎使用）
        order_request = {
            "stock_code": "000001.SZ",
            "side": "BUY",
            "volume": 100,
            "price": 13.50,
            "order_type": "LIMIT"
        }
        print(f"\n⚠️  注意：下单测试（当前为模拟模式，不会真实下单）")
        test_api("提交订单", "POST", f"/api/v1/trading/order/{session_id}", order_request)
        
        # 3.10 撤销订单
        cancel_request = {
            "order_id": "order_1000"
        }
        test_api("撤销订单", "POST", f"/api/v1/trading/cancel/{session_id}", cancel_request)
        
        # 3.11 断开账户连接
        test_api("断开账户连接", "POST", f"/api/v1/trading/disconnect/{session_id}")
    
    # 测试结果统计
    print_header("测试结果统计")
    print(f"\n总测试数: {test_results['total']}")
    print(f"✅ 通过: {test_results['passed']}")
    print(f"❌ 失败: {test_results['failed']}")
    
    if test_results['failed'] > 0:
        print("\n失败的测试:")
        for i, error in enumerate(test_results['errors'], 1):
            print(f"\n{i}. {error['test']}")
            print(f"   错误: {error.get('error', 'Unknown')}")
            if 'message' in error:
                print(f"   信息: {error['message']}")
    
    success_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
    print(f"\n成功率: {success_rate:.2f}%")
    
    print("\n" + "=" * 80)
    print(f"测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 返回退出码
    return 0 if test_results['failed'] == 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
