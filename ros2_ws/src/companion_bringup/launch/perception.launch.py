"""Launch perception + empathy nodes (Phase 3)."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Start detector, camera watch, human emotion stub, and empathy."""
    cfg_dir = get_package_share_directory('companion_bringup')
    perception_cfg = os.path.join(cfg_dir, 'config', 'perception.yaml')
    enable = LaunchConfiguration('enable_perception')

    return LaunchDescription([
        DeclareLaunchArgument(
            'enable_perception',
            default_value='true',
            description='Launch Phase 3 perception + empathy nodes',
        ),
        Node(
            package='companion_perception',
            executable='detector_node',
            name='detector_node',
            parameters=[perception_cfg],
            output='screen',
            condition=IfCondition(enable),
        ),
        Node(
            package='companion_perception',
            executable='camera_watch_node',
            name='camera_watch_node',
            parameters=[perception_cfg],
            output='screen',
            condition=IfCondition(enable),
        ),
        Node(
            package='companion_perception',
            executable='human_emotion_stub_node',
            name='human_emotion_stub_node',
            parameters=[perception_cfg],
            output='screen',
            condition=IfCondition(enable),
        ),
        Node(
            package='companion_brain',
            executable='empathy_node',
            name='empathy_node',
            parameters=[perception_cfg],
            output='screen',
            condition=IfCondition(enable),
        ),
    ])
