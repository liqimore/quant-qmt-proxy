"""
数据服务接口测试

测试所有数据服务相关的 API 端点
"""

import pytest
import httpx
from datetime import datetime, timedelta
from tests.rest.client import RESTTestClient


class TestDataAPI:
    """数据服务接口测试类"""
    
    def test_get_market_data(self, http_client: httpx.Client, sample_stock_codes, sample_date_range):
        """测试获取市场数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        
        data = {
            "stock_codes": sample_stock_codes[:2],  # 只测试前两个
            "start_date": start_date.strftime("%Y%m%d"),
            "end_date": end_date.strftime("%Y%m%d"),
            "period": "1d",
            "fields": ["time", "open", "high", "low", "close", "volume"]
        }
        
        response = http_client.post("/api/v1/data/market", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📊 市场数据测试 - 完整响应信息:")
        print("="*80)
        
        # 提取第一条数据
        first_data = None
        if isinstance(result, list) and len(result) > 0:
            first_data = result[0]
            print(f"✓ 返回类型: list, 数据条数: {len(result)}")
        elif isinstance(result, dict):
            if "data" in result and result["data"]:
                first_data = result["data"][0] if isinstance(result["data"], list) else result["data"]
                print(f"✓ 返回类型: dict (data字段), 数据条数: {len(result.get('data', []))}")
            elif "market_data" in result and result["market_data"]:
                first_data = result["market_data"][0] if isinstance(result["market_data"], list) else result["market_data"]
                print(f"✓ 返回类型: dict (market_data字段), 数据条数: {len(result.get('market_data', []))}")
        
        # 打印第一条完整数据
        if first_data:
            print(f"\n📋 第一条数据完整内容:")
            import json
            print(json.dumps(first_data, indent=2, ensure_ascii=False))
            
            # 验证数据合理性
            print(f"\n✓ 数据合理性验证:")
            
            # 检查股票代码
            stock_code = first_data.get("stock_code")
            if stock_code:
                print(f"  - 股票代码: {stock_code} ✓")
                assert stock_code in sample_stock_codes[:2], f"股票代码 {stock_code} 不在请求列表中"
            
            # 检查数据字段
            data_items = first_data.get("data", [])
            if data_items:
                first_item = data_items[0] if isinstance(data_items, list) else data_items
                print(f"  - K线数据条数: {len(data_items) if isinstance(data_items, list) else 1}")
                print(f"  - 第一条K线数据: {first_item}")
                
                # 验证必需字段
                required_fields = ["time", "open", "high", "low", "close", "volume"]
                for field in required_fields:
                    assert field in first_item, f"缺少必需字段: {field}"
                    value = first_item[field]
                    print(f"  - {field}: {value} ✓")
                
                # 验证价格合理性
                if all(k in first_item for k in ["open", "high", "low", "close"]):
                    assert first_item["high"] >= first_item["low"], "最高价应该 >= 最低价"
                    assert first_item["high"] >= first_item["open"], "最高价应该 >= 开盘价"
                    assert first_item["high"] >= first_item["close"], "最高价应该 >= 收盘价"
                    assert first_item["low"] <= first_item["open"], "最低价应该 <= 开盘价"
                    assert first_item["low"] <= first_item["close"], "最低价应该 <= 收盘价"
                    print(f"  - 价格逻辑验证: OHLC关系正确 ✓")
                
                # 验证成交量
                if "volume" in first_item:
                    assert first_item["volume"] >= 0, "成交量应该 >= 0"
                    print(f"  - 成交量验证: 非负数 ✓")
        else:
            print("⚠️  未找到数据，可能是空结果")
        
        print("="*80)
    
    def test_get_sector_list(self, http_client: httpx.Client):
        """测试获取板块列表"""
        response = http_client.get("/api/v1/data/sectors")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("🏢 板块列表测试 - 完整响应信息:")
        print("="*80)
        
        # 提取第一条数据
        first_sector = None
        total_count = 0
        
        if isinstance(result, list) and len(result) > 0:
            first_sector = result[0]
            total_count = len(result)
            print(f"✓ 返回类型: list, 板块数量: {total_count}")
        elif isinstance(result, dict):
            if "data" in result and result["data"]:
                data = result["data"]
                if isinstance(data, list) and len(data) > 0:
                    first_sector = data[0]
                    total_count = len(data)
                    print(f"✓ 返回类型: dict (data字段), 板块数量: {total_count}")
        
        # 打印第一条板块信息
        if first_sector:
            import json
            print(f"\n📋 第一个板块完整信息:")
            print(json.dumps(first_sector, indent=2, ensure_ascii=False))
            
            # 验证数据合理性
            print(f"\n✓ 数据合理性验证:")
            
            # 检查板块名称
            sector_name = first_sector.get("sector_name")
            if sector_name:
                print(f"  - 板块名称: {sector_name} ✓")
                assert isinstance(sector_name, str) and len(sector_name) > 0, "板块名称应为非空字符串"
            
            # 检查股票列表
            stock_list = first_sector.get("stock_list", [])
            if stock_list:
                print(f"  - 成分股数量: {len(stock_list)}")
                print(f"  - 前3个成分股: {stock_list[:3]} ✓")
                assert isinstance(stock_list, list), "股票列表应为数组"
                # 验证股票代码格式
                if len(stock_list) > 0:
                    first_stock = stock_list[0]
                    if isinstance(first_stock, str):
                        assert "." in first_stock, "股票代码应包含市场后缀 (如.SH, .SZ)"
                        print(f"  - 股票代码格式: 正确 (示例: {first_stock}) ✓")
            
            # 检查板块类型
            sector_type = first_sector.get("sector_type")
            if sector_type:
                print(f"  - 板块类型: {sector_type} ✓")
        else:
            print("⚠️  未找到板块数据")
        
        print("="*80)
    
    def test_get_stock_list_in_sector(self, http_client: httpx.Client, sample_sector_names):
        """测试获取板块股票"""
        data = {"sector_name": sample_sector_names[0]}
        
        response = http_client.post("/api/v1/data/sector", json=data)
        assert response.status_code == 200
        
        result = response.json()
        assert "data" in result or "stocks" in result
    
    def test_get_index_weight(self, http_client: httpx.Client, sample_index_codes):
        """测试获取指数权重"""
        data = {
            "index_code": sample_index_codes[1],  # 沪深300
            "date": None  # 最新权重
        }
        
        response = http_client.post("/api/v1/data/index-weight", json=data)
        assert response.status_code == 200
        
        result = response.json()
        assert "data" in result or "weights" in result
    
    def test_get_trading_calendar(self, http_client: httpx.Client):
        """测试获取交易日历"""
        year = datetime.now().year
        
        response = http_client.get(f"/api/v1/data/trading-calendar/{year}")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print(f"📅 交易日历测试 - {year}年:")
        print("="*80)
        
        # 打印完整数据
        import json
        print(f"\n完整数据:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 验证数据合理性
        print(f"\n✓ 数据合理性验证:")
        
        trading_dates = []
        holidays = []
        
        if isinstance(result, dict):
            trading_dates = result.get("trading_dates", [])
            holidays = result.get("holidays", [])
            year_field = result.get("year")
            
            if year_field:
                print(f"  - 年份: {year_field} ✓")
                assert year_field == year, f"返回年份({year_field})与请求年份({year})不符"
        
        if trading_dates:
            print(f"  - 交易日总数: {len(trading_dates)}")
            print(f"  - 前5个交易日: {trading_dates[:5]}")
            assert len(trading_dates) > 200, f"交易日数量({len(trading_dates)})异常，应该在200-250之间"
            assert len(trading_dates) < 260, f"交易日数量({len(trading_dates)})异常，应该在200-250之间"
            print(f"  - 交易日数量合理 (200-260天) ✓")
            
            # 验证日期格式
            first_date = trading_dates[0]
            assert len(str(first_date)) == 8, "日期格式应为YYYYMMDD (8位)"
            assert str(year) in str(first_date), f"日期应属于{year}年"
            print(f"  - 日期格式: YYYYMMDD ✓")
        
        if holidays:
            print(f"  - 非交易日总数: {len(holidays)}")
            print(f"  - 前5个非交易日: {holidays[:5]}")
            assert len(holidays) > 100, f"非交易日数量({len(holidays)})异常"
            print(f"  - 非交易日数量合理 ✓")
        
        # 验证交易日和非交易日总数应该等于一年的天数
        if trading_dates and holidays:
            total_days = len(trading_dates) + len(holidays)
            expected_days = 366 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 365
            assert total_days == expected_days, f"交易日({len(trading_dates)}) + 非交易日({len(holidays)}) = {total_days}，应等于{expected_days}"
            print(f"  - 日期完整性: 交易日 + 非交易日 = {total_days}天 ✓")
        
        print("="*80)
    
    def test_get_instrument_info(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取合约信息"""
        stock_code = sample_stock_codes[0]
        
        response = http_client.get(f"/api/v1/data/instrument/{stock_code}")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📋 合约信息测试 - 完整响应信息:")
        print("="*80)
        print(f"请求股票代码: {stock_code}")
        
        # 打印完整数据
        import json
        print(f"\n完整数据:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 验证数据合理性
        print(f"\n✓ 数据合理性验证:")
        
        # 检查必需字段
        if "InstrumentID" in result or "instrument_code" in result:
            code = result.get("InstrumentID") or result.get("instrument_code")
            print(f"  - 合约代码: {code} ✓")
            # 验证代码匹配（可能不包含市场后缀）
            code_without_market = stock_code.split('.')[0]  # 提取代码部分，如 "000001"
            assert code_without_market in str(code) or stock_code == str(code), \
                f"返回的合约代码({code})与请求({stock_code})不符"
        
        if "InstrumentName" in result or "instrument_name" in result:
            name = result.get("InstrumentName") or result.get("instrument_name")
            print(f"  - 合约名称: {name} ✓")
            assert name is not None and len(str(name)) > 0, "合约名称不应为空"
        
        # 检查价格字段（如果有）
        if "UpStopPrice" in result and result["UpStopPrice"]:
            print(f"  - 涨停价: {result['UpStopPrice']} ✓")
            assert result["UpStopPrice"] > 0, "涨停价应该大于0"
        
        if "DownStopPrice" in result and result["DownStopPrice"]:
            print(f"  - 跌停价: {result['DownStopPrice']} ✓")
            assert result["DownStopPrice"] > 0, "跌停价应该大于0"
            
        # 验证涨跌停价格关系
        if result.get("UpStopPrice") and result.get("DownStopPrice"):
            assert result["UpStopPrice"] > result["DownStopPrice"], "涨停价应该大于跌停价"
            print(f"  - 涨跌停价格关系: 正确 ✓")
        
        # 检查股本字段（如果有）
        if "TotalVolume" in result and result["TotalVolume"]:
            print(f"  - 总股本: {result['TotalVolume']} ✓")
            assert result["TotalVolume"] > 0, "总股本应该大于0"
        
        if "FloatVolume" in result and result["FloatVolume"]:
            print(f"  - 流通股本: {result['FloatVolume']} ✓")
            assert result["FloatVolume"] > 0, "流通股本应该大于0"
            
        # 验证流通股本不大于总股本
        if result.get("TotalVolume") and result.get("FloatVolume"):
            assert result["FloatVolume"] <= result["TotalVolume"], "流通股本不应大于总股本"
            print(f"  - 股本关系: 流通股本 <= 总股本 ✓")
        
        print("="*80)
    
    def test_get_financial_data(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取财务数据"""
        data = {
            "stock_codes": [sample_stock_codes[0]],
            "table_list": ["Capital"],
            "start_date": "20230101",
            "end_date": "20241231"
        }
        
        response = http_client.post("/api/v1/data/financial", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("💰 财务数据测试 - 完整响应信息:")
        print("="*80)
        print(f"请求股票: {sample_stock_codes[0]}, 财务表: Capital")
        
        # 提取第一条数据
        first_data = None
        if isinstance(result, list) and len(result) > 0:
            first_data = result[0]
            print(f"✓ 返回类型: list, 数据条数: {len(result)}")
        elif isinstance(result, dict) and "data" in result and result["data"]:
            first_data = result["data"][0] if isinstance(result["data"], list) else result["data"]
            print(f"✓ 返回类型: dict")
        
        # 打印第一条完整数据
        if first_data:
            import json
            print(f"\n📋 第一条数据完整内容:")
            print(json.dumps(first_data, indent=2, ensure_ascii=False))
            
            # 验证数据合理性
            print(f"\n✓ 数据合理性验证:")
            
            # 检查股票代码
            if "stock_code" in first_data:
                print(f"  - 股票代码: {first_data['stock_code']} ✓")
                assert first_data["stock_code"] == sample_stock_codes[0]
            
            # 检查表名
            if "table_name" in first_data:
                print(f"  - 财务表: {first_data['table_name']} ✓")
                assert first_data["table_name"] == "Capital"
            
            # 检查财务数据
            if "data" in first_data and first_data["data"]:
                financial_items = first_data["data"]
                item_count = len(financial_items) if isinstance(financial_items, list) else 1
                print(f"  - 财务记录数: {item_count}")
                
                if isinstance(financial_items, list) and len(financial_items) > 0:
                    first_item = financial_items[0]
                    print(f"  - 第一条财务记录: {first_item}")
                    
                    # 验证股本表字段
                    if "total_capital" in first_item:
                        print(f"  - 总股本: {first_item['total_capital']} ✓")
                        assert first_item["total_capital"] > 0, "总股本应该大于0"
                    
                    if "circulating_capital" in first_item:
                        print(f"  - 流通股本: {first_item['circulating_capital']} ✓")
                        assert first_item["circulating_capital"] > 0, "流通股本应该大于0"
                    
                    # 验证流通股本不大于总股本
                    if "total_capital" in first_item and "circulating_capital" in first_item:
                        total = first_item["total_capital"]
                        circulating = first_item["circulating_capital"]
                        assert circulating <= total, f"流通股本({circulating})不应大于总股本({total})"
                        print(f"  - 股本关系: 流通股本 <= 总股本 ✓")
                    
                    # 检查日期字段
                    if "m_timetag" in first_item or "m_anntime" in first_item:
                        date_field = first_item.get("m_timetag") or first_item.get("m_anntime")
                        print(f"  - 日期信息: {date_field} ✓")
        else:
            print("⚠️  未找到财务数据，可能是空结果或时间范围内无数据")
        
        print("="*80)


class TestDataAPIWithClient:
    """使用封装客户端的数据服务测试"""
    
    @pytest.fixture
    def client(self, base_url: str, api_key: str):
        """创建测试客户端"""
        with RESTTestClient(base_url=base_url, api_key=api_key) as client:
            yield client
    
    def test_market_data_with_client(self, client: RESTTestClient, sample_stock_codes):
        """使用客户端测试获取市场数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        
        response = client.get_market_data(
            stock_codes=sample_stock_codes[:2],
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            period="1d",
            fields=["time", "open", "high", "low", "close", "volume"]
        )
        
        result = client.assert_success(response)
        
        print("\n" + "="*80)
        print("📊 [客户端] 市场数据测试:")
        print("="*80)
        
        # 打印第一条数据
        if isinstance(result, list) and len(result) > 0:
            first_data = result[0]
            import json
            print(json.dumps(first_data, indent=2, ensure_ascii=False))
            
            # 基本验证
            if "data" in first_data and first_data["data"]:
                k_data = first_data["data"][0] if isinstance(first_data["data"], list) else first_data["data"]
                print(f"\n✓ K线字段验证:")
                for field in ["time", "open", "high", "low", "close", "volume"]:
                    assert field in k_data, f"缺少字段: {field}"
                    print(f"  - {field}: {k_data[field]} ✓")
        
        print("="*80)
    
    def test_sector_list_with_client(self, client: RESTTestClient):
        """使用客户端测试获取板块列表"""
        response = client.get_sector_list()
        result = client.assert_success(response)
        assert isinstance(result, (list, dict))
    
    def test_stock_list_in_sector_with_client(self, client: RESTTestClient, sample_sector_names):
        """使用客户端测试获取板块股票"""
        response = client.get_stock_list_in_sector(sector_name=sample_sector_names[0])
        result = client.assert_success(response)
        assert result is not None
    
    def test_index_weight_with_client(self, client: RESTTestClient, sample_index_codes):
        """使用客户端测试获取指数权重"""
        response = client.get_index_weight(index_code=sample_index_codes[1])
        result = client.assert_success(response)
        assert result is not None
    
    def test_trading_calendar_with_client(self, client: RESTTestClient):
        """使用客户端测试获取交易日历"""
        year = datetime.now().year
        response = client.get_trading_calendar(year=year)
        result = client.assert_success(response)
        assert isinstance(result, (list, dict))
    
    def test_instrument_info_with_client(self, client: RESTTestClient, sample_stock_codes):
        """使用客户端测试获取合约信息"""
        response = client.get_instrument_info(stock_code=sample_stock_codes[0])
        result = client.assert_success(response)
        
        print("\n" + "="*80)
        print("📋 [客户端] 合约信息测试:")
        print("="*80)
        print(f"股票代码: {sample_stock_codes[0]}")
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 验证关键字段
        print(f"\n✓ 关键字段验证:")
        if "InstrumentName" in result or "instrument_name" in result:
            name = result.get("InstrumentName") or result.get("instrument_name")
            print(f"  - 合约名称: {name} ✓")
        
        # 检查是否包含新增的完整字段
        extended_fields = ["UpStopPrice", "DownStopPrice", "TotalVolume", "FloatVolume"]
        found_extended = [f for f in extended_fields if f in result and result[f] is not None]
        if found_extended:
            print(f"  - 扩展字段: {found_extended} ✓")
        
        print("="*80)
    
    def test_financial_data_with_client(self, client: RESTTestClient, sample_stock_codes):
        """使用客户端测试获取财务数据"""
        response = client.get_financial_data(
            stock_codes=[sample_stock_codes[0]],
            table_list=["Capital"],
            start_date="20230101",
            end_date="20241231"
        )
        result = client.assert_success(response)
        assert result is not None


@pytest.mark.performance
class TestDataAPIPerformance:
    """数据服务接口性能测试"""
    
    def test_single_stock_data_performance(self, http_client: httpx.Client, sample_stock_codes, performance_timer):
        """测试单只股票行情查询性能"""
        from tests.rest.config import PERFORMANCE_BENCHMARKS
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        
        data = {
            "stock_codes": [sample_stock_codes[0]],
            "start_date": start_date.strftime("%Y%m%d"),
            "end_date": end_date.strftime("%Y%m%d"),
            "period": "1d",
        }
        
        performance_timer.start()
        response = http_client.post("/api/v1/data/market", json=data)
        elapsed = performance_timer.stop()
        
        assert response.status_code == 200
        assert performance_timer.elapsed_ms() < PERFORMANCE_BENCHMARKS["single_stock_data"], \
            f"单股行情查询耗时 {performance_timer.elapsed_ms():.2f}ms，超过基准 {PERFORMANCE_BENCHMARKS['single_stock_data']}ms"
    
    @pytest.mark.slow
    def test_batch_stock_data_performance(self, http_client: httpx.Client, sample_stock_codes, performance_timer):
        """测试批量股票行情查询性能"""
        from tests.rest.config import PERFORMANCE_BENCHMARKS
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        
        data = {
            "stock_codes": sample_stock_codes,
            "start_date": start_date.strftime("%Y%m%d"),
            "end_date": end_date.strftime("%Y%m%d"),
            "period": "1d",
        }
        
        performance_timer.start()
        response = http_client.post("/api/v1/data/market", json=data)
        elapsed = performance_timer.stop()
        
        assert response.status_code == 200
        assert performance_timer.elapsed_ms() < PERFORMANCE_BENCHMARKS["batch_stock_data"], \
            f"批量行情查询耗时 {performance_timer.elapsed_ms():.2f}ms，超过基准 {PERFORMANCE_BENCHMARKS['batch_stock_data']}ms"


@pytest.mark.integration
class TestDataAPIIntegration:
    """数据服务接口集成测试"""
    
    def test_complete_data_workflow(self, http_client: httpx.Client, sample_sector_names, sample_stock_codes):
        """测试完整的数据查询工作流"""
        # 1. 获取板块列表
        response = http_client.get("/api/v1/data/sectors")
        assert response.status_code == 200
        
        # 2. 获取板块成分股
        data = {"sector_name": sample_sector_names[0]}
        response = http_client.post("/api/v1/data/sector", json=data)
        assert response.status_code == 200
        
        result = response.json()
        
        # 获取股票列表，支持多种响应格式
        stocks = []
        if "data" in result:
            data_obj = result["data"]
            if isinstance(data_obj, dict):
                # 如果data是字典，尝试获取stock_list字段
                stocks = data_obj.get("stock_list", []) or data_obj.get("stocks", [])
            elif isinstance(data_obj, list):
                # 如果data是列表，直接使用
                stocks = data_obj
        elif "stocks" in result:
            stocks = result["stocks"]
        
        # 如果板块接口没有返回股票，使用样本股票进行测试
        if not stocks:
            stocks = sample_stock_codes[:1]
        
        # 3. 获取第一只股票的行情
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)
        
        # 处理股票代码格式（可能是字符串或字典）
        first_stock = stocks[0]
        stock_code = first_stock if isinstance(first_stock, str) else first_stock.get("stock_code", sample_stock_codes[0])
        
        market_data = {
            "stock_codes": [stock_code],
            "start_date": start_date.strftime("%Y%m%d"),
            "end_date": end_date.strftime("%Y%m%d"),
            "period": "1d",
        }
        
        response = http_client.post("/api/v1/data/market", json=market_data)
        assert response.status_code == 200
