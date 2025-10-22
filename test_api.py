"""
API测试脚本
"""
import requests
import json
from typing import Dict, Any


class APITester:
    """API测试类"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "test-key"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def test_health(self) -> Dict[str, Any]:
        """测试健康检查"""
        response = requests.get(f"{self.base_url}/health/")
        return response.json()
    
    def test_market_data(self) -> Dict[str, Any]:
        """测试市场数据接口"""
        data = {
            "stock_codes": ["000001.SZ", "000002.SZ"],
            "start_date": "20240101",
            "end_date": "20240110",
            "period": "1d"
        }
        response = requests.post(
            f"{self.base_url}/api/v1/data/market",
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def test_financial_data(self) -> Dict[str, Any]:
        """测试财务数据接口"""
        data = {
            "stock_codes": ["000001.SZ"],
            "table_list": ["income", "balance"]
        }
        response = requests.post(
            f"{self.base_url}/api/v1/data/financial",
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def test_connect_account(self) -> Dict[str, Any]:
        """测试连接账户"""
        data = {
            "account_id": "test_account",
            "password": "test_password"
        }
        response = requests.post(
            f"{self.base_url}/api/v1/trading/connect",
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def test_get_positions(self, session_id: str) -> Dict[str, Any]:
        """测试获取持仓"""
        response = requests.get(
            f"{self.base_url}/api/v1/trading/positions/{session_id}",
            headers=self.headers
        )
        return response.json()
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始API测试...")
        print("=" * 50)
        
        # 测试健康检查
        print("1. 测试健康检查...")
        try:
            result = self.test_health()
            print(f"✓ 健康检查: {result['message']}")
        except Exception as e:
            print(f"✗ 健康检查失败: {e}")
        
        # 测试市场数据
        print("2. 测试市场数据接口...")
        try:
            result = self.test_market_data()
            print(f"✓ 市场数据: {result['message']}")
        except Exception as e:
            print(f"✗ 市场数据失败: {e}")
        
        # 测试财务数据
        print("3. 测试财务数据接口...")
        try:
            result = self.test_financial_data()
            print(f"✓ 财务数据: {result['message']}")
        except Exception as e:
            print(f"✗ 财务数据失败: {e}")
        
        # 测试交易连接
        print("4. 测试交易连接...")
        try:
            result = self.test_connect_account()
            print(f"✓ 交易连接: {result['message']}")
            
            # 如果连接成功，测试获取持仓
            if result.get('success') and result.get('session_id'):
                session_id = result['session_id']
                print("5. 测试获取持仓...")
                try:
                    positions = self.test_get_positions(session_id)
                    print(f"✓ 获取持仓: {positions['message']}")
                except Exception as e:
                    print(f"✗ 获取持仓失败: {e}")
        except Exception as e:
            print(f"✗ 交易连接失败: {e}")
        
        print("=" * 50)
        print("API测试完成!")


if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
