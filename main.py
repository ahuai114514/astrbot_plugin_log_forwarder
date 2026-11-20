import asyncio
from contextlib import suppress
from contextvars import ContextVar

from astrbot.api.event import MessageChain
from astrbot.api.star import Context, Star, register
from loguru import logger


FORWARDING = ContextVar("log_forwarder_sending", default=False)


@register("astrbot_plugin_log_forwarder", "ahuai", "转发警告和错误日志", "1.0.0")
class LogForwarder(Star):
    def __init__(self, context: Context, config: dict) -> None:
        super().__init__(context)
        self.target_session = config.get("target_session", "").strip()
        self._sink_id: int | None = None
        self._worker: asyncio.Task[None] | None = None

    async def initialize(self) -> None:
        if not self.target_session or self._sink_id is not None:
            return

        loop = asyncio.get_running_loop()
        pending: asyncio.Queue[str] = asyncio.Queue(maxsize=100)

        def enqueue(text: str) -> None:
            with suppress(asyncio.QueueFull):
                pending.put_nowait(text)

        def capture(message) -> None:
            loop.call_soon_threadsafe(enqueue, str(message).rstrip("\n"))

        self._sink_id = logger.add(
            capture,
            level="WARNING",
            filter=lambda record: (
                record["level"].name in {"WARNING", "ERROR"} and not FORWARDING.get()
            ),
            format="[{time:HH:mm:ss}] [{level}] [{name}:{line}] {message}",
            backtrace=False,
            diagnose=False,
            colorize=False,
        )
        self._worker = loop.create_task(self._forward(pending))

    async def _forward(self, pending: asyncio.Queue[str]) -> None:
        # Adapter errors during proactive sends must not feed the sink again.
        token = FORWARDING.set(True)
        try:
            while True:
                text = await pending.get()
                try:
                    sent = await asyncio.wait_for(
                        self.context.send_message(
                            self.target_session, MessageChain().message(text)
                        ),
                        timeout=15,
                    )
                    if not sent:
                        logger.warning("[日志转发] 未找到目标会话对应的平台实例")
                except Exception as exc:
                    logger.warning("[日志转发] 发送失败 ({})", type(exc).__name__)
        finally:
            FORWARDING.reset(token)

    async def terminate(self) -> None:
        if self._sink_id is not None:
            logger.remove(self._sink_id)
            self._sink_id = None
        if self._worker is not None:
            self._worker.cancel()
            with suppress(asyncio.CancelledError):
                await self._worker
            self._worker = None
