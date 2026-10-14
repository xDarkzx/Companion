"""Launch MentorPi vendor drivers when present (Ackermann A1)."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, LogInfo
from launch_ros.actions import Node

VENDOR_ORCHESTRATOR = os.path.join(
    os.path.dirname(get_package_share_directory('companion_bringup')),
    '..', '..', 'src', 'vendor', 'orchestrator_launch',
)


def generate_launch_description():
    """Start body status; include vendor bringup when orchestrator exists."""
    actions = [
        LogInfo(msg='Companion MentorPi body launch (vendor drivers if fetched)'),
        Node(
            package='companion_body',
            executable='body_status_node',
            name='body_status_node',
            output='screen',
        ),
    ]

    launch_py = os.path.normpath(
        os.path.join(VENDOR_ORCHESTRATOR, 'launch', 'bringup.launch.py')
    )
    if os.path.isfile(launch_py):
        from launch.actions import IncludeLaunchDescription
        from launch.launch_description_sources import PythonLaunchDescriptionSource
        actions.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(launch_py),
            )
        )
    else:
        actions.append(
            LogInfo(
                msg='Vendor not fetched — run: bash scripts/fetch_mentorpi_vendor.sh'
            )
        )
        actions.append(
            ExecuteProcess(
                cmd=['echo', 'See docs/DEPLOY_MENTORPI.md'],
                output='screen',
            )
        )

    return LaunchDescription(actions)
