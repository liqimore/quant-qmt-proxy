"""
订阅管理器模块
负责管理xtdata行情订阅的生命周期和数据分发
"""
import asyncio
import os
import sys
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

# 添加xtquant包到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import xtquant.xtdata as xtdata
    XTQUANT_AVAILABLE = True
except ImportError:
    XTQUANT_AVAILABLE = False
    class MockModule:
        def __getattr__(self, name):
            def mock_function(*args, **kwargs):
                raise NotImplementedError(f"xtquant模块未正确安装，无法调用 {name}")
            return mock_function
    xtdata = MockModule()

from app.config import Settings, XTQuantMode
from app.utils.exceptions import DataServiceException
from app.utils.logger import logger


@dataclass
class SubscriptionContext:
    """订阅上下文"""
    subscription_id: str
    symbols: List[str]
    adjust_type: str = "none"
    subscription_type: str = "quote"  # "quote" 或 "whole_quote"
    queue: Optional[asyncio.Queue] = None  # 延迟初始化，避免在无事件循环线程中创建
    created_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    active: bool = True
    _queue_maxsize: int = 1000  # 队列最大尺寸配置
    
    def get_queue(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> asyncio.Queue:
        """获取或创建队列（线程安全的惰性初始化）"""
        if self.queue is None:
            # 如果没有队列，创建一个新的
            if loop is not None:
                # 在指定的事件循环中创建队列
                self.queue = asyncio.Queue(maxsize=self._queue_maxsize)
            else:
                # 尝试使用当前事件循环
                try:
                    self.queue = asyncio.Queue(maxsize=self._queue_maxsize)
                except RuntimeError:
                    # 如果没有事件循环，延迟创建
                    # 这种情况下，队列将在第一次stream_quotes调用时创建
                    pass
        return self.queue


class SubscriptionManager:
    """订阅管理器"""
    
    def __init__(self, settings: Settings):
        """初始化订阅管理器"""
        self.settings = settings
        self._subscriptions: Dict[str, SubscriptionContext] = {}
        self._symbol_to_subscriptions: Dict[str, List[str]] = {}  # symbol -> [subscription_ids]
        self._lock = threading.Lock()
        self._xtdata_thread: Optional[threading.Thread] = None
        self._xtdata_running = False
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        
        # 配置参数
        self.max_queue_size = getattr(settings.xtquant.data, 'max_queue_size', 1000)
        self.max_subscriptions = getattr(settings.xtquant.data, 'max_subscriptions', 100)
        self.heartbeat_timeout = getattr(settings.xtquant.data, 'heartbeat_timeout', 60)
        self.whole_quote_enabled = getattr(settings.xtquant.data, 'whole_quote_enabled', False)
        
        logger.info(f"SubscriptionManager初始化完成，模式: {settings.xtquant.mode.value}")
        
        # 如果是真实模式，启动xtdata后台线程
        if settings.xtquant.mode != XTQuantMode.MOCK and XTQUANT_AVAILABLE:
            self._start_xtdata_thread()
    
    def _start_xtdata_thread(self):
        """启动xtdata后台线程"""
        if self._xtdata_running:
            logger.warning("xtdata线程已在运行")
            return
        
        def xtdata_worker():
            """xtdata后台工作线程"""
            logger.info("启动xtdata后台线程")
            self._xtdata_running = True
            
            try:
                # 运行xtdata事件循环（阻塞式）
                xtdata.run()
            except Exception as e:
                logger.error(f"xtdata线程异常退出: {e}")
            finally:
                self._xtdata_running = False
                logger.warning("xtdata线程已停止")
        
        self._xtdata_thread = threading.Thread(target=xtdata_worker, daemon=True, name="xtdata-worker")
        self._xtdata_thread.start()
        logger.info("xtdata后台线程已启动")
    
    def _on_data_callback(self, data: Dict[str, Any]):
        """
        xtdata行情回调处理器
        此方法在xtdata的后台线程中被调用
        """
        try:
            symbols = data.keys()
            if not symbols:
                logger.warning(f"收到无效的行情数据（缺少symbol）: {data}")
                return
                        
            # 查找所有订阅了该symbol的订阅ID
            with self._lock:
                for symbol in symbols:
                    subscription_ids = self._symbol_to_subscriptions.get(symbol, [])
            
            if not subscription_ids:
                return
            
            # 将数据推送到所有相关订阅的队列
            for sub_id in subscription_ids:
                with self._lock:
                    context = self._subscriptions.get(sub_id)
                
                if context and context.active:
                    # 使用线程安全的方式将数据放入asyncio队列
                    if self._event_loop:
                        try:
                            # 确保队列已初始化
                            queue = context.get_queue(self._event_loop)
                            asyncio.run_coroutine_threadsafe(
                                self._put_to_queue(queue, data),
                                self._event_loop
                            )
                        except Exception as e:
                            logger.error(f"推送数据到订阅 {sub_id} 失败: {e}")
        
        except Exception as e:
            logger.error(f"行情回调处理异常: {e}", exc_info=True)
    
    async def _put_to_queue(self, queue: Optional[asyncio.Queue], data: Dict[str, Any]):
        """将数据放入队列（处理队列满的情况）"""
        if queue is None:
            logger.warning("队列尚未初始化，跳过数据推送")
            return
        
        try:
            queue.put_nowait(data)
        except asyncio.QueueFull:
            # 队列满时，丢弃最旧的数据
            try:
                queue.get_nowait()
                queue.put_nowait(data)
                logger.warning(f"订阅队列已满，丢弃旧数据")
            except Exception as e:
                logger.error(f"处理队列满异常: {e}")
    
    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        """设置事件循环（由应用启动时调用）"""
        self._event_loop = loop
        logger.info("已设置事件循环")
    
    def subscribe_quote(
        self, 
        symbols: List[str], 
        adjust_type: str = "none"
    ) -> str:
        """
        订阅单股或多股行情
        
        Args:
            symbols: 股票代码列表
            adjust_type: 复权类型 "none", "front", "back"
        
        Returns:
            subscription_id: 订阅ID
        """
        # 检查股票代码列表不能为空
        if not symbols or len(symbols) == 0:
            raise DataServiceException(
                "股票代码列表不能为空",
                error_code="EMPTY_SYMBOLS"
            )
        
        # 过滤空字符串
        symbols = [s.strip() for s in symbols if s and s.strip()]
        if not symbols:
            raise DataServiceException(
                "股票代码列表不能为空",
                error_code="EMPTY_SYMBOLS"
            )
        
        # 检查订阅数量限制
        with self._lock:
            if len(self._subscriptions) >= self.max_subscriptions:
                raise DataServiceException(
                    f"订阅数量已达上限 {self.max_subscriptions}",
                    error_code="SUBSCRIPTION_LIMIT_EXCEEDED"
                )
        
        # 生成订阅ID
        subscription_id = f"sub_{uuid.uuid4().hex[:16]}"
        
        # 创建订阅上下文
        context = SubscriptionContext(
            subscription_id=subscription_id,
            symbols=symbols,
            adjust_type=adjust_type,
            subscription_type="quote"
        )
        
        # 注册订阅
        with self._lock:
            self._subscriptions[subscription_id] = context
            
            # 更新symbol到订阅的映射
            for symbol in symbols:
                if symbol not in self._symbol_to_subscriptions:
                    self._symbol_to_subscriptions[symbol] = []
                self._symbol_to_subscriptions[symbol].append(subscription_id)
        
        # 真实模式下调用xtdata订阅
        if self.settings.xtquant.mode != XTQuantMode.MOCK and XTQUANT_AVAILABLE:
            try:
                # 调用xtdata订阅接口
                for symbol in symbols:
                    if adjust_type == "none":
                        # 不复权：使用标准订阅接口
                        xtdata.subscribe_quote(symbol, callback=self._on_data_callback)
                        logger.info(f"订阅行情（不复权）: {symbol}")
                    else:
                        # 复权：使用subscribe_quote2接口，支持前复权(front)和后复权(back)
                        # dividend_type参数: 'front'=前复权, 'back'=后复权
                        if not hasattr(xtdata, 'subscribe_quote2'):
                            # 如果xtdata版本不支持subscribe_quote2，降级使用普通订阅并警告
                            logger.warning(f"当前xtdata版本不支持subscribe_quote2，复权参数 {adjust_type} 将被忽略")
                            xtdata.subscribe_quote(symbol, callback=self._on_data_callback)
                        else:
                            xtdata.subscribe_quote2(
                                stock_code=symbol,
                                period='',  # 空字符串表示tick级别
                                start_time='',
                                end_time='',
                                count=-1,
                                dividend_type=adjust_type,  # front/back
                                callback=self._on_data_callback
                            )
                            logger.info(f"订阅行情（{adjust_type}复权）: {symbol}")
                
                logger.info(f"已订阅行情: {subscription_id}, symbols: {symbols}, adjust_type: {adjust_type}")
            
            except Exception as e:
                # 订阅失败，清理上下文
                with self._lock:
                    del self._subscriptions[subscription_id]
                    for symbol in symbols:
                        if symbol in self._symbol_to_subscriptions:
                            self._symbol_to_subscriptions[symbol].remove(subscription_id)
                
                logger.error(f"xtdata订阅失败: {e}")
                raise DataServiceException(f"订阅失败: {e}", error_code="SUBSCRIPTION_FAILED")
        else:
            logger.info(f"Mock模式：创建订阅 {subscription_id}, symbols: {symbols}")
        
        return subscription_id
    
    def subscribe_whole_quote(self) -> str:
        """
        订阅全推行情
        
        Returns:
            subscription_id: 订阅ID
        """
        # 检查是否允许全推
        if not self.whole_quote_enabled:
            raise DataServiceException(
                "全推订阅未启用，请在配置中开启",
                error_code="WHOLE_QUOTE_DISABLED"
            )
        
        if self.settings.xtquant.mode == XTQuantMode.MOCK:
            raise DataServiceException(
                "Mock模式不支持全推订阅",
                error_code="WHOLE_QUOTE_NOT_SUPPORTED_IN_MOCK"
            )
        
        # 生成订阅ID
        subscription_id = f"whole_{uuid.uuid4().hex[:16]}"
        
        # 创建订阅上下文
        context = SubscriptionContext(
            subscription_id=subscription_id,
            symbols=["*"],  # 全推标记
            subscription_type="whole_quote"
        )
        
        # 注册订阅
        with self._lock:
            self._subscriptions[subscription_id] = context
        
        # 真实模式下调用xtdata全推订阅
        if XTQUANT_AVAILABLE:
            try:
                xtdata.subscribe_whole_quote(["SH", "SZ"], callback=self._on_data_callback)
                logger.info(f"已订阅全推行情: {subscription_id}")
            except Exception as e:
                # 订阅失败，清理上下文
                with self._lock:
                    del self._subscriptions[subscription_id]
                
                logger.error(f"全推订阅失败: {e}")
                raise DataServiceException(f"全推订阅失败: {e}", error_code="WHOLE_QUOTE_FAILED")
        
        return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        取消订阅
        
        Args:
            subscription_id: 订阅ID
        
        Returns:
            是否成功取消
        """
        with self._lock:
            context = self._subscriptions.get(subscription_id)
            
            if not context:
                logger.warning(f"订阅不存在: {subscription_id}")
                return True  # 幂等操作，返回成功
            
            # 标记为非活跃
            context.active = False
            
            # 清理symbol映射
            for symbol in context.symbols:
                if symbol in self._symbol_to_subscriptions:
                    try:
                        self._symbol_to_subscriptions[symbol].remove(subscription_id)
                        if not self._symbol_to_subscriptions[symbol]:
                            del self._symbol_to_subscriptions[symbol]
                    except ValueError:
                        pass
            
            # 删除订阅上下文
            del self._subscriptions[subscription_id]
        
        # 真实模式下调用xtdata取消订阅
        if self.settings.xtquant.mode != XTQuantMode.MOCK and XTQUANT_AVAILABLE:
            try:
                if context.subscription_type == "whole_quote":
                    # 全推取消订阅
                    xtdata.unsubscribe_quote("*")
                else:
                    # 单股取消订阅
                    for symbol in context.symbols:
                        # 检查该symbol是否还有其他订阅
                        with self._lock:
                            if symbol not in self._symbol_to_subscriptions:
                                xtdata.unsubscribe_quote(symbol)
                
                logger.info(f"已取消订阅: {subscription_id}")
            except Exception as e:
                logger.error(f"取消订阅失败: {e}")
                # 不抛出异常，因为本地已经清理
        else:
            logger.info(f"Mock模式：取消订阅 {subscription_id}")
        
        return True
    
    async def stream_quotes(self, subscription_id: str) -> AsyncIterator[Dict[str, Any]]:
        """
        流式获取行情数据
        
        Args:
            subscription_id: 订阅ID
        
        Yields:
            行情数据字典
        """
        context = self._subscriptions.get(subscription_id)
        
        if not context:
            raise DataServiceException(
                f"订阅不存在: {subscription_id}",
                error_code="SUBSCRIPTION_NOT_FOUND"
            )
        
        # 确保队列已初始化（惰性创建）
        try:
            loop = asyncio.get_running_loop()
            context.get_queue(loop)
        except RuntimeError:
            # 没有运行中的事件循环，尝试创建
            context.get_queue(None)
        
        logger.info(f"开始流式推送: {subscription_id}")
        
        try:
            # Mock模式：生成模拟数据
            if self.settings.xtquant.mode == XTQuantMode.MOCK:
                while context.active:
                    # 模拟行情数据
                    for symbol in context.symbols:
                        mock_data = {
                            "stock_code": symbol,
                            "timestamp": datetime.now().isoformat(),
                            "last_price": 10.0 + (hash(symbol) % 100) / 10.0,
                            "volume": 1000000,
                            "amount": 10000000.0,
                            "open": 9.9,
                            "high": 10.5,
                            "low": 9.8,
                            "close": 10.0
                        }
                        yield mock_data
                    
                    await asyncio.sleep(1.0)  # 每秒推送一次
            
            # 真实模式：从队列读取数据
            else:
                queue = context.get_queue()
                if queue is None:
                    raise DataServiceException(
                        f"订阅队列未初始化: {subscription_id}",
                        error_code="QUEUE_NOT_INITIALIZED"
                    )
                
                while context.active:
                    try:
                        # 等待队列数据（设置超时以便检查active状态）
                        data = await asyncio.wait_for(queue.get(), timeout=1.0)
                        
                        # 更新心跳时间
                        context.last_heartbeat = datetime.now()
                        
                        yield data
                    
                    except asyncio.TimeoutError:
                        # 超时，检查active状态
                        continue
        
        except asyncio.CancelledError:
            logger.info(f"流式推送被取消: {subscription_id}")
            raise
        
        except Exception as e:
            logger.error(f"流式推送异常: {subscription_id}, {e}", exc_info=True)
            raise
        
        finally:
            logger.info(f"流式推送结束: {subscription_id}")
    
    def get_subscription_info(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """获取订阅信息"""
        context = self._subscriptions.get(subscription_id)
        
        if not context:
            return None
        
        queue = context.get_queue()
        queue_size = queue.qsize() if queue is not None else 0
        
        return {
            "subscription_id": context.subscription_id,
            "symbols": context.symbols,
            "adjust_type": context.adjust_type,
            "subscription_type": context.subscription_type,
            "created_at": context.created_at.isoformat(),
            "last_heartbeat": context.last_heartbeat.isoformat(),
            "active": context.active,
            "queue_size": queue_size
        }
    
    def list_subscriptions(self) -> List[Dict[str, Any]]:
        """列出所有订阅"""
        with self._lock:
            return [
                self.get_subscription_info(sub_id)
                for sub_id in self._subscriptions.keys()
            ]
    
    def cleanup_inactive_subscriptions(self):
        """清理超时的订阅"""
        now = datetime.now()
        inactive_ids = []
        
        with self._lock:
            for sub_id, context in self._subscriptions.items():
                # 检查心跳超时
                elapsed = (now - context.last_heartbeat).total_seconds()
                if elapsed > self.heartbeat_timeout:
                    logger.warning(f"订阅心跳超时: {sub_id}, 已超时 {elapsed:.1f}秒")
                    inactive_ids.append(sub_id)
        
        # 清理超时订阅
        for sub_id in inactive_ids:
            self.unsubscribe(sub_id)
        
        return len(inactive_ids)
    
    def shutdown(self):
        """关闭订阅管理器"""
        logger.info("关闭订阅管理器...")
        
        # 取消所有订阅
        with self._lock:
            subscription_ids = list(self._subscriptions.keys())
        
        for sub_id in subscription_ids:
            try:
                self.unsubscribe(sub_id)
            except Exception as e:
                logger.error(f"关闭订阅失败: {sub_id}, {e}")
        
        # 停止xtdata线程
        self._xtdata_running = False
        
        logger.info("订阅管理器已关闭")
