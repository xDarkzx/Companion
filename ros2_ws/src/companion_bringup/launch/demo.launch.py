"""Launch the Phase 1 demo: stub Brain + stub Face wired together."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Start heartbeat_node and face_stub_node with the demo parameters."""
    config = os.path.join(
        get_package_share_directory("companion_bringup"), "config", "demo.yaml"
    )
    return LaunchDescription([
        Node(
            package="companion_brain",
            executable="heartbeat_node",
            name="heartbeat_node",
            parameters=[config],
            output="screen",
        ),
        Node(
            package="companion_face",
            executable="face_stub_node",
            name="face_stub_node",
            output="screen",
        ),
    ])
