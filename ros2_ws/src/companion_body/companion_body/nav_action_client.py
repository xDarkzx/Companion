"""Nav2 NavigateToPose action client wrapper."""
from __future__ import annotations

from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionClient
from rclpy.node import Node


def _navigate_to_pose_type():
    """Import Nav2 action type when nav2_msgs is installed (Pi / Nav2 stack)."""
    try:
        from nav2_msgs.action import NavigateToPose
    except ImportError:
        return None
    return NavigateToPose


class NavActionClient:
    """Send goals to Nav2 and report arrival or failure."""

    def __init__(
        self,
        node: Node,
        action_name: str,
        on_arrived,
        on_failed,
    ) -> None:
        """Wire the action client and result callbacks."""
        action_type = _navigate_to_pose_type()
        if action_type is None:
            raise RuntimeError('nav2_msgs not installed')

        self._node = node
        self._logger = node.get_logger()
        self._on_arrived = on_arrived
        self._on_failed = on_failed
        self._action_type = action_type
        self._client = ActionClient(node, action_type, action_name)
        self._goal_handle = None

    def server_ready(self, timeout_sec: float = 2.0) -> bool:
        """Return True when the Nav2 action server is reachable."""
        return self._client.wait_for_server(timeout_sec=timeout_sec)

    def cancel(self) -> None:
        """Cancel an in-flight navigation goal."""
        if self._goal_handle is None:
            return
        cancel_future = self._goal_handle.cancel_goal_async()
        cancel_future.add_done_callback(lambda _f: None)

    def send_goal(self, pose: PoseStamped) -> None:
        """Dispatch a NavigateToPose goal."""
        goal = self._action_type.Goal()
        goal.pose = pose
        send_future = self._client.send_goal_async(goal)
        send_future.add_done_callback(self._on_goal_response)

    def _on_goal_response(self, future) -> None:
        """Handle goal acceptance from Nav2."""
        self._goal_handle = future.result()
        if not self._goal_handle.accepted:
            self._logger.warn('Nav2 rejected goal')
            self._on_failed()
            return
        result_future = self._goal_handle.get_result_async()
        result_future.add_done_callback(self._on_result)

    def _on_result(self, future) -> None:
        """Map action result status to arrived/failed callbacks."""
        result = future.result()
        status = result.status
        if status == 4:  # rclpy.action.GoalStatus.STATUS_SUCCEEDED
            self._on_arrived()
        else:
            self._logger.warn(f'Nav2 goal finished with status {status}')
            self._on_failed()
