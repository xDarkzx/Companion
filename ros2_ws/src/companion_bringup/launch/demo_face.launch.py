"""Launch ASCII face + voice-driven emotion demo (no PNG assets)."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Start voice_demo_node and face_ascii_node."""
    cfg = os.path.join(
        get_package_share_directory('companion_bringup'), 'config', 'face.yaml'
    )
    return LaunchDescription([
        Node(
            package='companion_brain',
            executable='voice_demo_node',
            name='voice_demo_node',
            parameters=[cfg],
            output='screen',
        ),
        Node(
            package='companion_face',
            executable='face_ascii_node',
            name='face_ascii_node',
            parameters=[cfg],
            output='screen',
        ),
    ])
