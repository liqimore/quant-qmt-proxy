"""
WebSocket路由 - 用于实时行情推送
"""
import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status

from app.config import Settings, get_settings
from app.dependencies import get_subscription_manager
from app.utils.exceptions import DataServiceException
from app.utils.logger import logger

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/quote/{subscription_id}")
async def websocket_quote_stream(
    websocket: WebSocket,
    subscription_id: str,
    settings: Settings = Depends(get_settings)
):
    """
    WebSocket行情流式推送
    
    客户端连接后，持续接收订阅的行情数据
    支持心跳机制保持连接
    
    Args:
        subscription_id: 订阅ID
    """
    await websocket.accept()
    logger.info(f"WebSocket连接建立: subscription_id={subscription_id}, client={websocket.client}")
    
    try:
        # 获取订阅管理器
        subscription_manager = get_subscription_manager(settings)
        
        # 验证订阅是否存在
        info = subscription_manager.get_subscription_info(subscription_id)
        if not info:
            await websocket.send_json({
                "type": "error",
                "message": f"订阅不存在: {subscription_id}"
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # 发送连接确认
        await websocket.send_json({
            "type": "connected",
            "subscription_id": subscription_id,
            "message": "WebSocket连接成功",
            "timestamp": datetime.now().isoformat()
        })
        
        # 创建接收客户端消息的任务（用于心跳）
        async def receive_messages():
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # 处理心跳消息
                    if message.get("type") == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        })
                        logger.debug(f"收到心跳: {subscription_id}")
            
            except WebSocketDisconnect:
                logger.info(f"客户端断开连接: {subscription_id}")
            except Exception as e:
                logger.error(f"接收消息异常: {e}")
        
        # 启动接收消息任务
        receive_task = asyncio.create_task(receive_messages())
        
        try:
            # 流式推送行情数据
            async for quote_data in subscription_manager.stream_quotes(subscription_id):
                try:
                    # 发送行情数据
                    await websocket.send_json({
                        "type": "quote",
                        "data": quote_data,
                        "timestamp": datetime.now().isoformat()
                    })
                
                except WebSocketDisconnect:
                    logger.info(f"客户端已断开: {subscription_id}")
                    break
                
                except Exception as e:
                    logger.error(f"发送数据异常: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
        
        finally:
            # 取消接收任务
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass
    
    except DataServiceException as e:
        logger.warning(f"订阅服务异常: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket断开: {subscription_id}")
    
    except Exception as e:
        logger.error(f"WebSocket异常: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"服务器内部错误: {str(e)}"
            })
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:
            pass
    
    finally:
        logger.info(f"WebSocket连接关闭: {subscription_id}")


@router.get("/ws/test")
async def websocket_test_page():
    """返回WebSocket测试页面的简单HTML"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #messages { height: 400px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; }
            input, button { margin: 5px; padding: 5px; }
        </style>
    </head>
    <body>
        <h1>WebSocket行情推送测试</h1>
        <div>
            <input type="text" id="subscriptionId" placeholder="输入subscription_id" style="width: 300px;">
            <button onclick="connect()">连接</button>
            <button onclick="disconnect()">断开</button>
            <button onclick="sendPing()">发送心跳</button>
        </div>
        <div id="messages"></div>
        
        <script>
            let ws = null;
            
            function connect() {
                const subId = document.getElementById('subscriptionId').value;
                if (!subId) {
                    alert('请输入subscription_id');
                    return;
                }
                
                const wsUrl = `ws://${window.location.host}/ws/quote/${subId}`;
                ws = new WebSocket(wsUrl);
                
                ws.onopen = () => {
                    addMessage('WebSocket已连接');
                };
                
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    addMessage('收到消息: ' + JSON.stringify(data, null, 2));
                };
                
                ws.onerror = (error) => {
                    addMessage('WebSocket错误: ' + error);
                };
                
                ws.onclose = () => {
                    addMessage('WebSocket已关闭');
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }
            
            function sendPing() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: 'ping' }));
                    addMessage('已发送心跳');
                }
            }
            
            function addMessage(msg) {
                const messagesDiv = document.getElementById('messages');
                const time = new Date().toLocaleTimeString();
                messagesDiv.innerHTML += `[${time}] ${msg}<br>`;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        </script>
    </body>
    </html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)
