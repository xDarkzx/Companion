"""Launch the full Companion stack (agent + behaviors + face + nav bridge)."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Start agent, behaviors, nav bridge, perception/body stubs, and face."""
    cfg_dir = get_package_share_directory('companion_bringup')
    face_cfg = os.path.join(cfg_dir, 'config', 'face.yaml')
    stack_cfg = os.path.join(cfg_dir, 'config', 'stack.yaml')
    places_cfg = os.path.join(cfg_dir, 'config', 'places.yaml')
    people_cfg = os.path.join(cfg_dir, 'config', 'people.yaml')
    show_face = LaunchConfiguration('show_face')
    enable_voice = LaunchConfiguration('enable_voice')

    agent_params = [stack_cfg, {
        'places_file': places_cfg,
        'people_file': people_cfg,
    }]
    nav_params = [stack_cfg, {'places_file': places_cfg}]

    return LaunchDescription([
        DeclareLaunchArgument(
            'show_face',
            default_value='true',
            description='Launch ASCII face window',
        ),
        DeclareLaunchArgument(
            'enable_voice',
            default_value='false',
            description='Launch STT/TTS voice nodes (Pi + USB mic)',
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(cfg_dir, 'launch', 'voice.launch.py'),
            ]),
            launch_arguments={'enable_voice': enable_voice}.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(cfg_dir, 'launch', 'perception.launch.py'),
            ]),
        ),
        Node(
            package='companion_agent',
            executable='agent_node',
            name='agent_node',
            parameters=agent_params,
            output='screen',
        ),
        Node(
            package='companion_behaviors',
            executable='behavior_controller_node',
            name='behavior_controller_node',
            parameters=[stack_cfg],
            output='screen',
        ),
        Node(
            package='companion_body',
            executable='nav_bridge_node',
            name='nav_bridge_node',
            parameters=nav_params,
            output='screen',
        ),
        Node(
            package='companion_body',
            executable='body_status_node',
            name='body_status_node',
            parameters=[stack_cfg],
            output='screen',
        ),
        Node(
            package='companion_face',
            executable='face_ascii_node',
            name='face_ascii_node',
            parameters=[face_cfg],
            output='screen',
            condition=IfCondition(show_face),
        ),
    ])
