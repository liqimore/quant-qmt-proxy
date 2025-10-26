"""
gRPC 数据服务测试用例

测试范围：
1. 已实现接口（9个）：
   - get_market_data() - 获取行情数据
   - get_financial_data() - 获取财务数据
   - get_sector_list() - 获取板块列表
   - get_stock_list_in_sector() - 获取板块成分股
   - get_index_weight() - 获取指数权重
   - get_trading_dates() / get_trading_calendar() - 获取交易日历
   - get_instrument_detail() - 获取合约信息
   - get_etf_info() - 获取ETF信息

2. 未来实现接口（部分重要接口）：
   - subscribe_quote() - 订阅行情（流式）
   - get_l2_quote() - Level2数据
   - download_history_data() - 下载历史数据
"""

import pytest
import grpc
from typing import Iterator
from datetime import datetime

# TODO: 在 proto 文件生成后，导入对应的 pb2 和 pb2_grpc 模块
# from generated import data_pb2, data_pb2_grpc, common_pb2


class TestDataGrpcService:
    """数据服务 gRPC 测试类"""

    @pytest.fixture(scope="class")
    def grpc_channel(self):
        """创建 gRPC 连接通道"""
        # TODO: 从配置文件读取 gRPC 服务地址
        channel = grpc.insecure_channel('localhost:50051')
        yield channel
        channel.close()

    @pytest.fixture(scope="class")
    def data_stub(self, grpc_channel):
        """创建数据服务 stub"""
        # TODO: 替换为实际生成的 stub
        # return data_pb2_grpc.DataServiceStub(grpc_channel)
        return None

    # ==================== 已实现接口测试 ====================

    class TestImplementedApis:
        """测试已实现的数据接口"""

        def test_get_market_data_single_stock(self, data_stub):
            """测试获取单只股票行情数据"""
            # TODO: 使用实际的 protobuf 消息
            # request = data_pb2.MarketDataRequest(
            #     stock_codes=['000001.SZ'],
            #     start_date='20240101',
            #     end_date='20240131',
            #     period=common_pb2.PERIOD_TYPE_1D,
            #     fields=['open', 'high', 'low', 'close', 'volume', 'amount'],
            #     adjust_type='none'
            # )
            
            # response = data_stub.GetMarketData(request)
            
            # 断言测试
            # assert response.status.code == 0
            # assert len(response.data) == 1
            # assert response.data[0].stock_code == '000001.SZ'
            # assert len(response.data[0].bars) > 0
            # assert response.data[0].period == '1d'
            pass

        def test_get_market_data_multiple_stocks(self, data_stub):
            """测试获取多只股票行情数据"""
            # TODO: 测试批量查询
            # request = data_pb2.MarketDataRequest(
            #     stock_codes=['000001.SZ', '600000.SH', '000002.SZ'],
            #     start_date='20240101',
            #     end_date='20240110',
            #     period=common_pb2.PERIOD_TYPE_1D,
            #     fields=['close', 'volume']
            # )
            
            # response = data_stub.GetMarketData(request)
            
            # assert response.status.code == 0
            # assert len(response.data) == 3
            # for stock_data in response.data:
            #     assert stock_data.stock_code in ['000001.SZ', '600000.SH', '000002.SZ']
            pass

        def test_get_market_data_different_periods(self, data_stub):
            """测试不同周期的行情数据"""
            # TODO: 测试不同周期（1分钟、5分钟、日线等）
            periods = [
                # common_pb2.PERIOD_TYPE_1M,
                # common_pb2.PERIOD_TYPE_5M,
                # common_pb2.PERIOD_TYPE_1H,
                # common_pb2.PERIOD_TYPE_1D,
            ]
            
            for period in periods:
                # request = data_pb2.MarketDataRequest(
                #     stock_codes=['000001.SZ'],
                #     start_date='20240101',
                #     end_date='20240105',
                #     period=period
                # )
                # response = data_stub.GetMarketData(request)
                # assert response.status.code == 0
                pass

        def test_get_market_data_with_adjustment(self, data_stub):
            """测试复权数据"""
            # TODO: 测试前复权、后复权、不复权
            adjust_types = ['none', 'front', 'back']
            
            for adjust_type in adjust_types:
                # request = data_pb2.MarketDataRequest(
                #     stock_codes=['000001.SZ'],
                #     start_date='20240101',
                #     end_date='20240131',
                #     adjust_type=adjust_type
                # )
                # response = data_stub.GetMarketData(request)
                # assert response.status.code == 0
                pass

        def test_get_financial_data_balance_sheet(self, data_stub):
            """测试获取资产负债表数据"""
            # TODO: 测试财务数据查询
            # request = data_pb2.FinancialDataRequest(
            #     stock_codes=['000001.SZ'],
            #     table_list=['Balance'],
            #     start_date='20230101',
            #     end_date='20231231'
            # )
            
            # response = data_stub.GetFinancialData(request)
            
            # assert response.status.code == 0
            # assert len(response.data) > 0
            # assert response.data[0].table_name == 'Balance'
            # assert len(response.data[0].rows) > 0
            pass

        def test_get_financial_data_multiple_tables(self, data_stub):
            """测试获取多张财务报表"""
            # TODO: 测试多个财务表
            # request = data_pb2.FinancialDataRequest(
            #     stock_codes=['000001.SZ', '600000.SH'],
            #     table_list=['Balance', 'Income', 'CashFlow'],
            #     start_date='20230101',
            #     end_date='20231231'
            # )
            
            # response = data_stub.GetFinancialData(request)
            # assert response.status.code == 0
            pass

        def test_get_sector_list_all(self, data_stub):
            """测试获取所有板块列表"""
            # TODO: 测试板块列表查询
            # request = google.protobuf.Empty()
            # response = data_stub.GetSectorList(request)
            
            # assert response.status.code == 0
            # assert len(response.sectors) > 0
            # for sector in response.sectors:
            #     assert sector.sector_name
            #     assert isinstance(sector.stock_list, list)
            pass

        def test_get_sector_list_by_type(self, data_stub):
            """测试按类型获取板块列表"""
            # TODO: 测试不同板块类型（行业、概念、地域等）
            # sector_types = ['industry', 'concept', 'area']
            # for sector_type in sector_types:
            #     request = data_pb2.SectorListRequest(sector_type=sector_type)
            #     response = data_stub.GetSectorList(request)
            #     assert response.status.code == 0
            pass

        def test_get_stock_list_in_sector(self, data_stub):
            """测试获取板块成分股"""
            # TODO: 测试板块成分股查询
            # request = data_pb2.SectorStockListRequest(
            #     sector_name='沪深300'
            # )
            # response = data_stub.GetStockListInSector(request)
            
            # assert response.status.code == 0
            # assert len(response.stock_codes) > 0
            pass

        def test_get_index_weight(self, data_stub):
            """测试获取指数权重"""
            # TODO: 测试指数权重查询
            # request = data_pb2.IndexWeightRequest(
            #     index_code='000300.SH',  # 沪深300
            #     date='20240101'
            # )
            
            # response = data_stub.GetIndexWeight(request)
            
            # assert response.status.code == 0
            # assert response.index_code == '000300.SH'
            # assert len(response.weights) > 0
            # 
            # # 验证权重数据结构
            # for weight in response.weights:
            #     assert weight.stock_code
            #     assert weight.weight >= 0
            #     assert weight.weight <= 100
            pass

        def test_get_index_weight_latest(self, data_stub):
            """测试获取最新指数权重（不指定日期）"""
            # TODO: 测试不指定日期的情况
            # request = data_pb2.IndexWeightRequest(
            #     index_code='000300.SH'
            # )
            # response = data_stub.GetIndexWeight(request)
            # assert response.status.code == 0
            pass

        def test_get_trading_calendar_by_year(self, data_stub):
            """测试按年份获取交易日历"""
            # TODO: 测试交易日历查询
            # request = data_pb2.TradingCalendarRequest(
            #     year=2024
            # )
            
            # response = data_stub.GetTradingCalendar(request)
            
            # assert response.status.code == 0
            # assert response.year == 2024
            # assert len(response.trading_dates) > 0
            # assert len(response.holidays) > 0
            # 
            # # 验证日期格式
            # for date in response.trading_dates:
            #     assert len(date) == 8  # YYYYMMDD
            #     datetime.strptime(date, '%Y%m%d')
            pass

        def test_get_trading_calendar_current_year(self, data_stub):
            """测试获取当前年份交易日历"""
            # TODO: 测试当前年份
            # current_year = datetime.now().year
            # request = data_pb2.TradingCalendarRequest(year=current_year)
            # response = data_stub.GetTradingCalendar(request)
            # assert response.status.code == 0
            pass

        def test_get_instrument_info_stock(self, data_stub):
            """测试获取股票合约信息"""
            # TODO: 测试股票合约信息
            # request = data_pb2.InstrumentInfoRequest(
            #     stock_code='000001.SZ'
            # )
            
            # response = data_stub.GetInstrumentInfo(request)
            
            # assert response.status.code == 0
            # assert response.instrument_code == '000001.SZ'
            # assert response.instrument_name == '平安银行'
            # assert response.market_type in ['SZ', 'SH']
            pass

        def test_get_instrument_info_multiple(self, data_stub):
            """测试批量获取合约信息"""
            # TODO: 测试批量查询
            # stock_codes = ['000001.SZ', '600000.SH', '000002.SZ']
            # for code in stock_codes:
            #     request = data_pb2.InstrumentInfoRequest(stock_code=code)
            #     response = data_stub.GetInstrumentInfo(request)
            #     assert response.status.code == 0
            pass

        def test_get_etf_info(self, data_stub):
            """测试获取ETF信息"""
            # TODO: 测试ETF信息查询
            # request = data_pb2.EtfInfoRequest(
            #     etf_code='510050.SH'  # 50ETF
            # )
            
            # response = data_stub.GetEtfInfo(request)
            
            # assert response.status.code == 0
            # assert response.etf_code == '510050.SH'
            pass

    # ==================== 错误处理测试 ====================

    class TestErrorHandling:
        """测试错误处理"""

        def test_invalid_stock_code(self, data_stub):
            """测试无效股票代码"""
            # TODO: 测试错误处理
            # request = data_pb2.MarketDataRequest(
            #     stock_codes=['INVALID.CODE'],
            #     start_date='20240101',
            #     end_date='20240131'
            # )
            
            # response = data_stub.GetMarketData(request)
            # assert response.status.code != 0
            # assert 'error' in response.status.message.lower()
            pass

        def test_invalid_date_range(self, data_stub):
            """测试无效日期范围（开始日期晚于结束日期）"""
            # TODO: 测试日期验证
            # request = data_pb2.MarketDataRequest(
            #     stock_codes=['000001.SZ'],
            #     start_date='20240131',
            #     end_date='20240101'  # 结束日期早于开始日期
            # )
            
            # response = data_stub.GetMarketData(request)
            # assert response.status.code != 0
            pass

        def test_empty_stock_codes(self, data_stub):
            """测试空股票代码列表"""
            # TODO: 测试空列表处理
            # request = data_pb2.MarketDataRequest(
            #     stock_codes=[],
            #     start_date='20240101',
            #     end_date='20240131'
            # )
            
            # response = data_stub.GetMarketData(request)
            # assert response.status.code != 0
            pass

        def test_connection_timeout(self, grpc_channel):
            """测试连接超时"""
            # TODO: 测试超时处理
            # try:
            #     stub = data_pb2_grpc.DataServiceStub(grpc_channel)
            #     request = data_pb2.MarketDataRequest(
            #         stock_codes=['000001.SZ'],
            #         start_date='20240101',
            #         end_date='20240131'
            #     )
            #     response = stub.GetMarketData(request, timeout=0.001)
            # except grpc.RpcError as e:
            #     assert e.code() == grpc.StatusCode.DEADLINE_EXCEEDED
            pass

    # ==================== 性能测试 ====================

    class TestPerformance:
        """性能测试"""

        def test_large_date_range_performance(self, data_stub):
            """测试大日期范围查询性能"""
            import time
            
            # TODO: 测试性能
            # start_time = time.time()
            # 
            # request = data_pb2.MarketDataRequest(
            #     stock_codes=['000001.SZ'],
            #     start_date='20200101',
            #     end_date='20240131',
            #     period=common_pb2.PERIOD_TYPE_1D
            # )
            # response = data_stub.GetMarketData(request)
            # 
            # elapsed_time = time.time() - start_time
            # 
            # assert response.status.code == 0
            # assert elapsed_time < 5.0  # 应在5秒内完成
            pass

        def test_batch_query_performance(self, data_stub):
            """测试批量查询性能"""
            import time
            
            # TODO: 测试批量查询性能
            # start_time = time.time()
            # 
            # request = data_pb2.MarketDataRequest(
            #     stock_codes=[f'{i:06d}.SZ' for i in range(1, 51)],  # 50只股票
            #     start_date='20240101',
            #     end_date='20240131'
            # )
            # response = data_stub.GetMarketData(request)
            # 
            # elapsed_time = time.time() - start_time
            # 
            # assert response.status.code == 0
            # assert elapsed_time < 10.0  # 应在10秒内完成
            pass

        def test_concurrent_requests(self, grpc_channel):
            """测试并发请求"""
            import concurrent.futures
            
            # TODO: 测试并发性能
            # def make_request(stock_code):
            #     stub = data_pb2_grpc.DataServiceStub(grpc_channel)
            #     request = data_pb2.MarketDataRequest(
            #         stock_codes=[stock_code],
            #         start_date='20240101',
            #         end_date='20240131'
            #     )
            #     return stub.GetMarketData(request)
            # 
            # stock_codes = [f'{i:06d}.SZ' for i in range(1, 11)]
            # 
            # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            #     futures = [executor.submit(make_request, code) for code in stock_codes]
            #     results = [f.result() for f in concurrent.futures.as_completed(futures)]
            # 
            # assert all(r.status.code == 0 for r in results)
            pass

    # ==================== 流式接口测试（未来实现） ====================

    class TestStreamingApis:
        """测试流式接口（未来实现）"""

        @pytest.mark.skip(reason="流式接口尚未实现")
        def test_subscribe_market_data_stream(self, data_stub):
            """测试订阅实时行情（服务端流）"""
            # TODO: 测试实时行情推送
            # request = data_pb2.SubscribeMarketDataRequest(
            #     stock_codes=['000001.SZ', '600000.SH'],
            #     fields=['last_price', 'volume', 'amount']
            # )
            
            # received_count = 0
            # for snapshot in data_stub.SubscribeMarketData(request):
            #     assert snapshot.stock_code in ['000001.SZ', '600000.SH']
            #     assert snapshot.last_price > 0
            #     received_count += 1
            #     
            #     if received_count >= 10:  # 接收10条数据后退出
            #         break
            # 
            # assert received_count == 10
            pass

        @pytest.mark.skip(reason="流式接口尚未实现")
        def test_subscribe_multiple_stocks(self, data_stub):
            """测试订阅多只股票实时行情"""
            # TODO: 测试多股票订阅
            # stock_codes = ['000001.SZ', '600000.SH', '000002.SZ', '600519.SH']
            # request = data_pb2.SubscribeMarketDataRequest(
            #     stock_codes=stock_codes,
            #     fields=['last_price']
            # )
            # 
            # received_stocks = set()
            # for snapshot in data_stub.SubscribeMarketData(request):
            #     received_stocks.add(snapshot.stock_code)
            #     if len(received_stocks) == len(stock_codes):
            #         break
            # 
            # assert received_stocks == set(stock_codes)
            pass

        @pytest.mark.skip(reason="流式接口尚未实现")
        def test_unsubscribe_market_data(self, data_stub):
            """测试取消订阅"""
            # TODO: 测试取消订阅
            pass

    # ==================== 未实现接口占位测试 ====================

    class TestFutureApis:
        """未来实现接口的占位测试"""

        @pytest.mark.skip(reason="Level2数据接口尚未实现")
        def test_get_l2_quote(self, data_stub):
            """测试获取Level2快照数据"""
            # TODO: 实现后补充测试
            pass

        @pytest.mark.skip(reason="Level2数据接口尚未实现")
        def test_get_l2_order(self, data_stub):
            """测试获取Level2逐笔委托"""
            # TODO: 实现后补充测试
            pass

        @pytest.mark.skip(reason="Level2数据接口尚未实现")
        def test_get_l2_transaction(self, data_stub):
            """测试获取Level2逐笔成交"""
            # TODO: 实现后补充测试
            pass

        @pytest.mark.skip(reason="数据下载接口尚未实现")
        def test_download_history_data(self, data_stub):
            """测试下载历史数据"""
            # TODO: 实现后补充测试
            pass

        @pytest.mark.skip(reason="数据下载接口尚未实现")
        def test_download_financial_data(self, data_stub):
            """测试下载财务数据"""
            # TODO: 实现后补充测试
            pass

        @pytest.mark.skip(reason="板块管理接口尚未实现")
        def test_create_sector(self, data_stub):
            """测试创建自定义板块"""
            # TODO: 实现后补充测试
            pass

        @pytest.mark.skip(reason="板块管理接口尚未实现")
        def test_add_stock_to_sector(self, data_stub):
            """测试添加股票到板块"""
            # TODO: 实现后补充测试
            pass

        @pytest.mark.skip(reason="节假日数据接口尚未实现")
        def test_get_holidays(self, data_stub):
            """测试获取节假日数据"""
            # TODO: 实现后补充测试
            pass

        @pytest.mark.skip(reason="可转债接口尚未实现")
        def test_get_cb_info(self, data_stub):
            """测试获取可转债信息"""
            # TODO: 实现后补充测试
            pass

        @pytest.mark.skip(reason="新股申购接口尚未实现")
        def test_get_ipo_info(self, data_stub):
            """测试获取新股申购信息"""
            # TODO: 实现后补充测试
            pass


# ==================== 新增接口测试（阶段1-5）====================

class TestNewDataGrpcApis:
    """新增数据服务 gRPC 接口测试"""
    
    @pytest.fixture(scope="class")
    def grpc_channel(self):
        """创建 gRPC 连接通道"""
        channel = grpc.insecure_channel('localhost:50051')
        yield channel
        channel.close()
    
    @pytest.fixture(scope="class")
    def data_stub(self, grpc_channel):
        """创建数据服务 stub"""
        from generated import data_pb2_grpc
        return data_pb2_grpc.DataServiceStub(grpc_channel)
    
    # ===== 阶段1: 基础信息接口测试 =====
    
    def test_get_instrument_type(self, data_stub):
        """测试获取合约类型"""
        from generated import data_pb2
        
        request = data_pb2.InstrumentTypeRequest(stock_code='000001.SZ')
        response = data_stub.GetInstrumentType(request)
        
        print("\n" + "="*80)
        print("📊 [gRPC] 合约类型测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        print(f"消息: {response.status.message}")
        
        if response.status.code == 0:
            print(f"股票代码: {response.data.stock_code}")
            print(f"是否股票: {response.data.stock}")
            print(f"是否指数: {response.data.index}")
            print(f"是否ETF: {response.data.etf}")
            
            assert response.data.stock_code == '000001.SZ'
        
        print("="*80)
    
    def test_get_holidays(self, data_stub):
        """测试获取节假日列表"""
        from generated import data_pb2
        from google.protobuf import empty_pb2
        
        request = empty_pb2.Empty()
        response = data_stub.GetHolidays(request)
        
        print("\n" + "="*80)
        print("🎊 [gRPC] 节假日列表测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        if response.status.code == 0:
            print(f"节假日数量: {len(response.holidays)}")
            if len(response.holidays) > 0:
                print(f"前5个节假日: {list(response.holidays[:5])}")
        
        print("="*80)
    
    def test_get_convertible_bond_info(self, data_stub):
        """测试获取可转债信息"""
        from generated import data_pb2
        from google.protobuf import empty_pb2
        
        request = empty_pb2.Empty()
        response = data_stub.GetConvertibleBondInfo(request)
        
        print("\n" + "="*80)
        print("🔄 [gRPC] 可转债信息测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        if response.status.code == 0:
            print(f"可转债数量: {len(response.bonds)}")
            if len(response.bonds) > 0:
                first_bond = response.bonds[0]
                print(f"第一只可转债代码: {first_bond.bond_code}")
                print(f"可转债名称: {first_bond.bond_name}")
        
        print("="*80)
    
    def test_get_ipo_info_grpc(self, data_stub):
        """测试获取新股申购信息"""
        from generated import data_pb2
        from google.protobuf import empty_pb2
        
        request = empty_pb2.Empty()
        response = data_stub.GetIpoInfo(request)
        
        print("\n" + "="*80)
        print("🆕 [gRPC] 新股申购信息测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        if response.status.code == 0:
            print(f"新股数量: {len(response.ipos)}")
            if len(response.ipos) > 0:
                first_ipo = response.ipos[0]
                print(f"第一只新股代码: {first_ipo.security_code}")
                print(f"新股名称: {first_ipo.code_name}")
        
        print("="*80)
    
    def test_get_period_list(self, data_stub):
        """测试获取可用周期列表"""
        from generated import data_pb2
        from google.protobuf import empty_pb2
        
        request = empty_pb2.Empty()
        response = data_stub.GetPeriodList(request)
        
        print("\n" + "="*80)
        print("📅 [gRPC] 可用周期列表测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        if response.status.code == 0:
            print(f"可用周期: {list(response.periods)}")
            assert len(response.periods) > 0
        
        print("="*80)
    
    def test_get_data_dir(self, data_stub):
        """测试获取本地数据路径"""
        from generated import data_pb2
        from google.protobuf import empty_pb2
        
        request = empty_pb2.Empty()
        response = data_stub.GetDataDir(request)
        
        print("\n" + "="*80)
        print("📁 [gRPC] 本地数据路径测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        if response.status.code == 0:
            print(f"数据路径: {response.data_dir}")
            assert len(response.data_dir) > 0
        
        print("="*80)
    
    # ===== 阶段2: 行情数据获取接口测试 =====
    
    def test_get_local_data(self, data_stub):
        """测试获取本地行情数据"""
        from generated import data_pb2
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        
        request = data_pb2.LocalDataRequest(
            stock_codes=['000001.SZ'],
            start_time=start_date.strftime("%Y%m%d"),
            end_time=end_date.strftime("%Y%m%d"),
            period='1d'
        )
        response = data_stub.GetLocalData(request)
        
        print("\n" + "="*80)
        print("📊 [gRPC] 本地行情数据测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        if response.status.code == 0:
            for stock_code, kline_list in response.data.items():
                print(f"股票代码: {stock_code}")
                print(f"K线数量: {len(kline_list.bars)}")
        
        print("="*80)
    
    def test_get_full_tick(self, data_stub):
        """测试获取完整tick数据"""
        from generated import data_pb2
        
        request = data_pb2.FullTickRequest(
            stock_codes=['000001.SZ'],
            start_time='',
            end_time=''
        )
        response = data_stub.GetFullTick(request)
        
        print("\n" + "="*80)
        print("⏱️  [gRPC] 完整Tick数据测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        if response.status.code == 0:
            for stock_code, tick_list in response.data.items():
                print(f"股票代码: {stock_code}")
                print(f"Tick数量: {len(tick_list.ticks)}")
                if len(tick_list.ticks) > 0:
                    first_tick = tick_list.ticks[0]
                    print(f"最新价: {first_tick.last_price}")
        
        print("="*80)
    
    def test_get_divid_factors(self, data_stub):
        """测试获取除权除息数据"""
        from generated import data_pb2
        
        request = data_pb2.DividFactorsRequest(stock_code='000001.SZ')
        response = data_stub.GetDividFactors(request)
        
        print("\n" + "="*80)
        print("💰 [gRPC] 除权除息数据测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        if response.status.code == 0:
            print(f"除权记录数: {len(response.factors)}")
        
        print("="*80)
    
    def test_get_full_kline(self, data_stub):
        """测试获取完整K线数据"""
        from generated import data_pb2
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        
        request = data_pb2.FullKlineRequest(
            stock_codes=['000001.SZ'],
            start_time=start_date.strftime("%Y%m%d"),
            end_time=end_date.strftime("%Y%m%d"),
            period='1d'
        )
        response = data_stub.GetFullKline(request)
        
        print("\n" + "="*80)
        print("📈 [gRPC] 完整K线数据测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        if response.status.code == 0:
            for stock_code, kline_list in response.data.items():
                print(f"股票代码: {stock_code}")
                print(f"K线数量: {len(kline_list.bars)}")
        
        print("="*80)
    
    # ===== 阶段3: 数据下载接口测试 =====
    
    def test_download_history_data(self, data_stub):
        """测试下载历史数据"""
        from generated import data_pb2
        
        request = data_pb2.DownloadHistoryDataRequest(
            stock_code='000001.SZ',
            period='1d',
            start_time='',
            end_time='',
            incrementally=False
        )
        response = data_stub.DownloadHistoryData(request)
        
        print("\n" + "="*80)
        print("⬇️  [gRPC] 下载历史数据测试:")
        print("="*80)
        print(f"RPC状态码: {response.rpc_status.code}")
        
        if response.rpc_status.code == 0:
            print(f"任务ID: {response.task_id}")
            print(f"任务状态: {response.status}")
            print(f"进度: {response.progress}%")
        
        print("="*80)
    
    def test_download_history_data_batch(self, data_stub):
        """测试批量下载历史数据"""
        from generated import data_pb2
        
        request = data_pb2.DownloadHistoryDataBatchRequest(
            stock_list=['000001.SZ', '000002.SZ'],
            period='1d',
            start_time='',
            end_time=''
        )
        response = data_stub.DownloadHistoryDataBatch(request)
        
        print("\n" + "="*80)
        print("⬇️  [gRPC] 批量下载历史数据测试:")
        print("="*80)
        print(f"RPC状态码: {response.rpc_status.code}")
        
        if response.rpc_status.code == 0:
            print(f"任务ID: {response.task_id}")
            print(f"总数: {response.total}")
            print(f"已完成: {response.finished}")
        
        print("="*80)
    
    def test_download_financial_data(self, data_stub):
        """测试下载财务数据"""
        from generated import data_pb2
        
        request = data_pb2.DownloadFinancialDataRequest(
            stock_list=['000001.SZ'],
            table_list=['Capital'],
            start_date='',
            end_date=''
        )
        response = data_stub.DownloadFinancialData(request)
        
        print("\n" + "="*80)
        print("⬇️  [gRPC] 下载财务数据测试:")
        print("="*80)
        print(f"RPC状态码: {response.rpc_status.code}")
        
        print("="*80)
    
    def test_download_sector_data(self, data_stub):
        """测试下载板块数据"""
        from generated import data_pb2
        from google.protobuf import empty_pb2
        
        request = empty_pb2.Empty()
        response = data_stub.DownloadSectorData(request)
        
        print("\n" + "="*80)
        print("⬇️  [gRPC] 下载板块数据测试:")
        print("="*80)
        print(f"RPC状态码: {response.rpc_status.code}")
        
        print("="*80)
    
    # ===== 阶段4: 板块管理接口测试 =====
    
    def test_create_sector_folder(self, data_stub):
        """测试创建板块文件夹"""
        from generated import data_pb2
        
        request = data_pb2.CreateSectorFolderRequest(
            parent_node='',
            folder_name='测试文件夹_grpc',
            overwrite=True
        )
        response = data_stub.CreateSectorFolder(request)
        
        print("\n" + "="*80)
        print("📁 [gRPC] 创建板块文件夹测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        if response.status.code == 0:
            print(f"创建的文件夹名: {response.created_name}")
        
        print("="*80)
    
    def test_create_sector(self, data_stub):
        """测试创建板块"""
        from generated import data_pb2
        
        request = data_pb2.CreateSectorRequest(
            parent_node='',
            sector_name='测试板块_grpc',
            overwrite=True
        )
        response = data_stub.CreateSector(request)
        
        print("\n" + "="*80)
        print("📊 [gRPC] 创建板块测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        if response.status.code == 0:
            print(f"创建的板块名: {response.created_name}")
        
        print("="*80)
    
    def test_add_sector(self, data_stub):
        """测试添加股票到板块"""
        from generated import data_pb2
        
        request = data_pb2.AddSectorRequest(
            sector_name='测试板块_grpc',
            stock_list=['000001.SZ', '000002.SZ']
        )
        response = data_stub.AddSector(request)
        
        print("\n" + "="*80)
        print("➕ [gRPC] 添加股票到板块测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        print("="*80)
    
    def test_reset_sector(self, data_stub):
        """测试重置板块"""
        from generated import data_pb2
        
        request = data_pb2.ResetSectorRequest(
            sector_name='测试板块_grpc',
            stock_list=['000001.SZ']
        )
        response = data_stub.ResetSector(request)
        
        print("\n" + "="*80)
        print("🔄 [gRPC] 重置板块测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        print(f"成功: {response.success}")
        
        print("="*80)
    
    def test_remove_stock_from_sector(self, data_stub):
        """测试从板块移除股票"""
        from generated import data_pb2
        
        request = data_pb2.RemoveStockFromSectorRequest(
            sector_name='测试板块_grpc',
            stock_list=['000001.SZ']
        )
        response = data_stub.RemoveStockFromSector(request)
        
        print("\n" + "="*80)
        print("➖ [gRPC] 从板块移除股票测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        print(f"成功: {response.success}")
        
        print("="*80)
    
    def test_remove_sector(self, data_stub):
        """测试删除板块"""
        from generated import data_pb2
        
        request = data_pb2.RemoveSectorRequest(sector_name='测试板块_grpc')
        response = data_stub.RemoveSector(request)
        
        print("\n" + "="*80)
        print("🗑️  [gRPC] 删除板块测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        print("="*80)
    
    # ===== 阶段5: Level2数据接口测试 =====
    
    def test_get_l2_quote(self, data_stub):
        """测试获取Level2快照数据（10档）"""
        from generated import data_pb2
        
        request = data_pb2.L2QuoteRequest(
            stock_codes=['000001.SZ'],
            start_time='',
            end_time=''
        )
        response = data_stub.GetL2Quote(request)
        
        print("\n" + "="*80)
        print("📊 [gRPC] Level2快照数据测试（10档）:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        if response.status.code == 0:
            for stock_code, quote_list in response.data.items():
                print(f"股票代码: {stock_code}")
                print(f"快照数量: {len(quote_list.quotes)}")
                if len(quote_list.quotes) > 0:
                    first_quote = quote_list.quotes[0]
                    print(f"委卖价档数: {len(first_quote.ask_price)}")
                    print(f"委买价档数: {len(first_quote.bid_price)}")
        
        print("="*80)
    
    def test_get_l2_order(self, data_stub):
        """测试获取Level2逐笔委托"""
        from generated import data_pb2
        
        request = data_pb2.L2OrderRequest(
            stock_codes=['000001.SZ'],
            start_time='',
            end_time=''
        )
        response = data_stub.GetL2Order(request)
        
        print("\n" + "="*80)
        print("📝 [gRPC] Level2逐笔委托测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        if response.status.code == 0:
            for stock_code, order_list in response.data.items():
                print(f"股票代码: {stock_code}")
                print(f"委托数量: {len(order_list.orders)}")
        
        print("="*80)
    
    def test_get_l2_transaction(self, data_stub):
        """测试获取Level2逐笔成交"""
        from generated import data_pb2
        
        request = data_pb2.L2TransactionRequest(
            stock_codes=['000001.SZ'],
            start_time='',
            end_time=''
        )
        response = data_stub.GetL2Transaction(request)
        
        print("\n" + "="*80)
        print("💹 [gRPC] Level2逐笔成交测试:")
        print("="*80)
        print(f"状态码: {response.status.code}")
        
        if response.status.code == 0:
            for stock_code, trans_list in response.data.items():
                print(f"股票代码: {stock_code}")
                print(f"成交数量: {len(trans_list.transactions)}")
        
        print("="*80)


# ==================== 辅助函数 ====================

def validate_kline_data(bars):
    """验证K线数据的完整性"""
    for bar in bars:
        assert bar.open > 0
        assert bar.high >= bar.open
        assert bar.high >= bar.close
        assert bar.low <= bar.open
        assert bar.low <= bar.close
        assert bar.volume >= 0
        assert bar.amount >= 0


def validate_financial_data(financial_response):
    """验证财务数据的完整性"""
    assert financial_response.stock_code
    assert financial_response.table_name
    assert len(financial_response.columns) > 0
    assert len(financial_response.rows) >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
