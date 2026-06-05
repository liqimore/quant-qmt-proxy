from __future__ import annotations

from concurrent import futures
import time
import uuid
from typing import Iterable

import grpc

from app.config import Settings, get_settings
from app.dependencies import (
    get_market_data_service,
    get_reference_data_service,
    get_trading_session_manager,
)
from app.grpc_services.data_grpc_service import DataGrpcService
from app.grpc_services.health_grpc_service import HealthGrpcService
from app.grpc_services.trading_grpc_service import TradingGrpcService
from app.utils.logger import configure_logging_from_settings, log_runtime_configuration, logger
from generated import data_pb2_grpc, health_pb2_grpc, trading_pb2_grpc


def _extract_bearer_token(metadata: Iterable[tuple[str, str]]) -> str | None:
    for key, value in metadata:
        if key.lower() != "authorization":
            continue
        if not value:
            return None
        if value.lower().startswith("bearer "):
            return value[7:].strip()
        return value.strip()
    return None


class ApiKeyServerInterceptor(grpc.ServerInterceptor):
    def __init__(self, api_keys: list[str] | None = None, exempt_methods: set[str] | None = None):
        self.api_keys = set(api_keys or [])
        self.exempt_methods = exempt_methods or set()

    def intercept_service(self, continuation, handler_call_details):
        handler = continuation(handler_call_details)
        if handler is None:
            return None

        if not self.api_keys or handler_call_details.method in self.exempt_methods:
            return handler

        token = _extract_bearer_token(handler_call_details.invocation_metadata or [])
        if token in self.api_keys:
            return handler

        logger.warning(f"gRPC authentication failed: method={handler_call_details.method}")
        return self._abort_handler(handler)

    def _abort_handler(self, handler: grpc.RpcMethodHandler) -> grpc.RpcMethodHandler:
        def abort_unary_unary(request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "invalid api key")

        def abort_unary_stream(request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "invalid api key")
            yield

        def abort_stream_unary(request_iterator, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "invalid api key")

        def abort_stream_stream(request_iterator, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "invalid api key")
            yield

        if handler.unary_unary:
            return grpc.unary_unary_rpc_method_handler(
                abort_unary_unary,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        if handler.unary_stream:
            return grpc.unary_stream_rpc_method_handler(
                abort_unary_stream,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        if handler.stream_unary:
            return grpc.stream_unary_rpc_method_handler(
                abort_stream_unary,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        return grpc.stream_stream_rpc_method_handler(
            abort_stream_stream,
            request_deserializer=handler.request_deserializer,
            response_serializer=handler.response_serializer,
        )


class RequestLoggingServerInterceptor(grpc.ServerInterceptor):
    @staticmethod
    def _request_summary(request) -> str:
        details: list[str] = []
        for field_name in ("session_id", "account_id", "stock_code", "order_id", "order_sysid", "market", "index_code", "symbol", "count"):
            if hasattr(request, field_name):
                value = getattr(request, field_name)
                if value not in ("", None, 0):
                    details.append(f"{field_name}={value}")
        for field_name in ("symbols", "markets"):
            if hasattr(request, field_name):
                values = list(getattr(request, field_name))
                if values:
                    preview = values[:3]
                    suffix = "..." if len(values) > 3 else ""
                    details.append(f"{field_name}={preview}{suffix}")
        if hasattr(request, "period"):
            period = getattr(request, "period")
            if period not in ("", None, 0):
                details.append(f"period={period}")
        if hasattr(request, "WhichOneof"):
            try:
                target = request.WhichOneof("target")
            except ValueError:
                target = None
            if target == "sysid_target":
                sysid_target = request.sysid_target
                details.append(f"sysid_market={sysid_target.market}")
                details.append(f"sysid_order_sysid={sysid_target.order_sysid}")
            elif target == "order_id":
                details.append(f"target=order_id:{request.order_id}")
        return ", ".join(details) if details else "no-key-fields"

    @staticmethod
    def _status_name(context) -> str:
        return (context.code() or grpc.StatusCode.OK).name

    def intercept_service(self, continuation, handler_call_details):
        handler = continuation(handler_call_details)
        if handler is None:
            return None

        method = handler_call_details.method

        if handler.unary_unary:
            def unary_unary(request, context):
                request_id = uuid.uuid4().hex[:12]
                start = time.perf_counter()
                summary = self._request_summary(request)
                logger.info(f"gRPC request started: id={request_id}, method={method}, {summary}")
                try:
                    response = handler.unary_unary(request, context)
                    duration_ms = (time.perf_counter() - start) * 1000
                    logger.info(
                        f"gRPC request completed: id={request_id}, method={method}, status={self._status_name(context)}, duration_ms={duration_ms:.2f}, {summary}"
                    )
                    return response
                except Exception as exc:
                    duration_ms = (time.perf_counter() - start) * 1000
                    logger.error(
                        f"gRPC request failed: id={request_id}, method={method}, status={self._status_name(context)}, duration_ms={duration_ms:.2f}, error={exc}, {summary}"
                    )
                    raise

            return grpc.unary_unary_rpc_method_handler(
                unary_unary,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.unary_stream:
            def unary_stream(request, context):
                request_id = uuid.uuid4().hex[:12]
                start = time.perf_counter()
                summary = self._request_summary(request)
                logger.info(f"gRPC stream started: id={request_id}, method={method}, {summary}")
                try:
                    for item in handler.unary_stream(request, context):
                        yield item
                    duration_ms = (time.perf_counter() - start) * 1000
                    logger.info(
                        f"gRPC stream completed: id={request_id}, method={method}, status={self._status_name(context)}, duration_ms={duration_ms:.2f}, {summary}"
                    )
                except Exception as exc:
                    duration_ms = (time.perf_counter() - start) * 1000
                    logger.error(
                        f"gRPC stream failed: id={request_id}, method={method}, status={self._status_name(context)}, duration_ms={duration_ms:.2f}, error={exc}, {summary}"
                    )
                    raise

            return grpc.unary_stream_rpc_method_handler(
                unary_stream,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        return handler


def create_grpc_server(settings: Settings | None = None) -> grpc.Server:
    settings = settings or get_settings()
    configure_logging_from_settings(settings)
    log_runtime_configuration("grpc", settings)

    interceptors: list[grpc.ServerInterceptor] = [
        RequestLoggingServerInterceptor(),
        ApiKeyServerInterceptor(
            api_keys=settings.security.api_keys,
            exempt_methods={"/grpc.health.v1.Health/Check", "/qmt.health.Health/Check"},
        )
    ]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=settings.grpc_max_workers),
        interceptors=interceptors,
        options=[
            ("grpc.max_send_message_length", settings.grpc_max_message_length),
            ("grpc.max_receive_message_length", settings.grpc_max_message_length),
            ("grpc.so_reuseport", 1),
        ],
    )

    data_pb2_grpc.add_DataServiceServicer_to_server(
        DataGrpcService(
            market_data_service=get_market_data_service(settings),
            reference_data_service=get_reference_data_service(settings),
        ),
        server,
    )
    trading_pb2_grpc.add_TradingServiceServicer_to_server(
        TradingGrpcService(get_trading_session_manager(settings)),
        server,
    )
    health_pb2_grpc.add_HealthServicer_to_server(HealthGrpcService(), server)

    server_address = f"{settings.grpc_host}:{settings.grpc_port}"
    bound_port = server.add_insecure_port(server_address)
    if bound_port == 0:
        raise RuntimeError(f"failed to bind gRPC server to {server_address}")
    setattr(server, "_bound_port", bound_port)
    logger.info(f"gRPC server configured on {settings.grpc_host}:{bound_port}")
    return server


def serve(settings: Settings | None = None) -> None:
    from app.startup import bootstrap_application, shutdown_application

    settings = settings or get_settings()
    bootstrap_application(settings)
    server = create_grpc_server(settings)
    server.start()
    bound_port = getattr(server, "_bound_port", settings.grpc_port)
    logger.info(f"gRPC server started on {settings.grpc_host}:{bound_port}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("gRPC server stopping")
        server.stop(grace=5)
    finally:
        shutdown_application()


if __name__ == "__main__":
    serve()
