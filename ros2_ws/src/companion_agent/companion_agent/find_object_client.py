"""Ask perception to find an object without blocking the agent's executor."""
from __future__ import annotations

from collections.abc import Callable

from companion_agent.object_answer import first_position
from companion_interfaces.srv import FindObject
from rclpy.node import Node

FIND_SERVICE = '/companion/find_object'
REASON_UNAVAILABLE = 'unavailable'

Position = tuple[float, float, float]
ResultCallback = Callable[[bool, Position | None, str], None]


class FindObjectClient:
    """Call FindObject asynchronously; report (found, position, reason) exactly once."""

    def __init__(self, node: Node, timeout_sec: float) -> None:
        """Create the service client; timeout bounds how long a caller waits."""
        self._node = node
        self._timeout = timeout_sec
        self._client = node.create_client(FindObject, FIND_SERVICE)

    def request(self, query: str, on_result: ResultCallback) -> None:
        """Send the query; on_result gets the answer, or 'unavailable' on no service/timeout."""
        if not self._client.service_is_ready():
            on_result(False, None, REASON_UNAVAILABLE)
            return
        future = self._client.call_async(FindObject.Request(query=query))
        state = {'done': False}

        def finish(found: bool, position: Position | None, reason: str) -> None:
            if state['done']:
                return
            state['done'] = True
            timer.cancel()
            self._node.destroy_timer(timer)
            on_result(found, position, reason)

        def on_timeout() -> None:
            future.cancel()
            finish(False, None, REASON_UNAVAILABLE)

        def on_done(done_future) -> None:
            response = done_future.result()
            if response is None:
                finish(False, None, REASON_UNAVAILABLE)
                return
            finish(response.found, first_position(response), response.reason)

        timer = self._node.create_timer(self._timeout, on_timeout)
        future.add_done_callback(on_done)
