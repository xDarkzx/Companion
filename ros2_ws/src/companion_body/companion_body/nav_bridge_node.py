"""Resolve named places to Nav2 goals (action client or /goal_pose fallback)."""
from pathlib import Path

from companion_body.body_behaviors import MOTION_BEHAVIORS
from companion_body.goal_pose_builder import place_to_pose
from companion_body.motion_controller import MotionController
from companion_body.nav_action_client import NavActionClient
from companion_body.nav_status import ARRIVED, FAILED, IDLE, NAV_BEHAVIORS, NAVIGATING
from companion_interfaces.msg import BehaviorRequest, DetectionBatch
from companion_memory.places_store import load_places, PlacePose
from geometry_msgs.msg import PoseStamped
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

BEHAVIOR_TOPIC = '/companion/behavior_request'
DETECTION_TOPIC = '/companion/detections'
GOAL_TOPIC = '/goal_pose'
NAV_STATUS_TOPIC = '/companion/nav_status'
BODY_STATUS_TOPIC = '/companion/body_status'
QUEUE_DEPTH = 10


class NavBridgeNode(Node):
    """Bridge behavior requests to Nav2 via action or legacy goal topic."""

    def __init__(self) -> None:
        """Load places and wire navigation backends."""
        super().__init__('nav_bridge_node')
        self.declare_parameter('places_file', '')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('simulated_travel_sec', 0.0)
        self.declare_parameter('use_nav_action', True)
        self.declare_parameter('nav_action_name', 'navigate_to_pose')
        self.declare_parameter('follow_standoff_m', 1.5)
        self.declare_parameter('follow_min_confidence', 0.4)
        self.declare_parameter('follow_anchor_place', '')
        self.declare_parameter('follow_rate_hz', 2.0)
        self.declare_parameter('patrol_places', ['kitchen', 'bedroom', 'dock'])

        places_path = self.get_parameter('places_file').value
        self._map_frame = str(self.get_parameter('map_frame').value)
        self._sim_travel = float(self.get_parameter('simulated_travel_sec').value)
        self._use_action = bool(self.get_parameter('use_nav_action').value)
        self._places = load_places(Path(places_path))
        patrol_names = list(self.get_parameter('patrol_places').value)

        self._goal_pub = self.create_publisher(PoseStamped, GOAL_TOPIC, QUEUE_DEPTH)
        self._status_pub = self.create_publisher(String, NAV_STATUS_TOPIC, QUEUE_DEPTH)
        self._body_pub = self.create_publisher(String, BODY_STATUS_TOPIC, QUEUE_DEPTH)
        self._arrival_timer = self.create_timer(1.0, self._on_arrival_timer)
        self._arrival_timer.cancel()
        self._follow_timer = self.create_timer(0.5, self._on_follow_timer)
        self._follow_timer.cancel()

        self._motion = MotionController(
            map_frame=self._map_frame,
            places=self._places,
            standoff_m=float(self.get_parameter('follow_standoff_m').value),
            follow_min_confidence=float(self.get_parameter('follow_min_confidence').value),
            follow_anchor=str(self.get_parameter('follow_anchor_place').value),
            patrol_names=patrol_names,
            now_stamp=lambda: self.get_clock().now().to_msg(),
            publish_nav_status=self._publish_status,
            publish_body_status=self._publish_body_status,
            send_nav_goal=self._send_nav_goal,
            cancel_nav=self._cancel_nav,
            cancel_timers=self._cancel_motion_timers,
        )

        action_name = str(self.get_parameter('nav_action_name').value)
        self._nav_client: NavActionClient | None = None
        if self._use_action and self._sim_travel <= 0:
            self._nav_client = self._try_nav_client(action_name)

        self.create_subscription(
            BehaviorRequest, BEHAVIOR_TOPIC, self._on_behavior, QUEUE_DEPTH
        )
        self.create_subscription(
            DetectionBatch, DETECTION_TOPIC, self._on_detections, QUEUE_DEPTH
        )

        follow_rate = float(self.get_parameter('follow_rate_hz').value)
        if follow_rate > 0:
            self._follow_timer.timer_period_ns = int((1.0 / follow_rate) * 1e9)

        names = ', '.join(sorted(self._places.keys())) or '(none)'
        self.get_logger().info(f'NavBridgeNode places: {names}')
        self._publish_status(IDLE)

    def _try_nav_client(self, action_name: str) -> NavActionClient | None:
        """Create Nav2 action client when nav2_msgs and server are available."""
        try:
            client = NavActionClient(
                self,
                action_name,
                on_arrived=self._handle_arrived,
                on_failed=self._handle_failed,
            )
        except RuntimeError:
            self.get_logger().warn(
                'nav2_msgs missing — install Nav2 or use simulated_travel_sec'
            )
            return None
        if client.server_ready(timeout_sec=3.0):
            self.get_logger().info(f'Nav2 action client ready ({action_name})')
            return client
        self.get_logger().warn('Nav2 action server not found — falling back to /goal_pose')
        return None

    def _on_behavior(self, msg: BehaviorRequest) -> None:
        """Emit Nav2 goal for navigation and motion behaviors."""
        behavior = msg.behavior
        target = (msg.target or '').strip().lower()

        if behavior == 'stop':
            self._motion.stop_all()
            self._publish_status(IDLE)
            self._publish_body_status('motion:stopped')
            self.get_logger().info('Navigation stop requested')
            return

        if behavior == 'follow':
            self._motion.start_follow()
            self._follow_timer.reset()
            self.get_logger().info('Follow mode active — goals driven by person detections')
            return

        if behavior == 'patrol':
            self._motion.start_patrol()
            self.get_logger().info('Patrol motion started')
            return

        if behavior in MOTION_BEHAVIORS:
            self._motion.acknowledge_motion(behavior)
            self.get_logger().info(f'Motion behavior {behavior!r} acknowledged')
            return

        if behavior not in NAV_BEHAVIORS:
            return

        self._motion.stop_all()
        place = self._resolve_place(behavior, target)
        if place is None:
            self._publish_status(FAILED)
            self.get_logger().warn(f'Unknown place for {behavior} target={target!r}')
            return

        stamp = self.get_clock().now().to_msg()
        pose = place_to_pose(place, self._map_frame, stamp)
        self._publish_status(NAVIGATING)
        self.get_logger().info(
            f'Nav goal {place.name}: x={place.x} y={place.y} yaw={place.yaw}'
        )
        self._send_nav_goal(pose)

    def _on_detections(self, msg: DetectionBatch) -> None:
        """Forward vision detections to follow controller."""
        self._motion.on_detections(msg)

    def _on_follow_timer(self) -> None:
        """Refresh follow goals while follow mode is active."""
        if not self._motion.follow_active:
            self._follow_timer.cancel()
            return
        self._motion.on_follow_tick()

    def _send_nav_goal(self, pose: PoseStamped) -> None:
        """Send goal via Nav2 action or /goal_pose fallback."""
        if self._nav_client is not None:
            self._nav_client.send_goal(pose)
            return
        self._goal_pub.publish(pose)
        if self._sim_travel > 0:
            self._arrival_timer.timer_period_ns = int(self._sim_travel * 1e9)
            self._arrival_timer.reset()

    def _cancel_nav(self) -> None:
        """Cancel Nav2 action goal if active."""
        if self._nav_client is not None:
            self._nav_client.cancel()

    def _cancel_motion_timers(self) -> None:
        """Stop follow refresh and simulated arrival timers."""
        self._follow_timer.cancel()
        self._arrival_timer.cancel()

    def _resolve_place(self, behavior: str, target: str) -> PlacePose | None:
        """Look up a place record for navigation behaviors."""
        if behavior == 'go_to_place' and target:
            return self._places.get(target)
        if behavior == 'go_home':
            return self._places.get('dock') or self._places.get('home')
        return None

    def _on_arrival_timer(self) -> None:
        """Simulate Nav2 arrival when no action server is connected."""
        self._arrival_timer.cancel()
        self._handle_arrived()

    def _handle_arrived(self) -> None:
        """Publish arrived status or advance patrol."""
        if self._motion.patrol_active:
            self._motion.on_patrol_arrived()
            return
        self._publish_status(ARRIVED)
        self.get_logger().info('Navigation arrived')

    def _handle_failed(self) -> None:
        """Publish failed status for the agent sequencer."""
        self._publish_status(FAILED)
        self.get_logger().warn('Navigation failed')

    def _publish_status(self, status: str) -> None:
        """Publish nav lifecycle for the agent step sequencer."""
        msg = String()
        msg.data = status
        self._status_pub.publish(msg)

    def _publish_body_status(self, status: str) -> None:
        """Publish body motion mode for orchestration and debugging."""
        msg = String()
        msg.data = status
        self._body_pub.publish(msg)


def main(args=None) -> None:
    """Spin with clean shutdown."""
    rclpy.init(args=args)
    node = NavBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
