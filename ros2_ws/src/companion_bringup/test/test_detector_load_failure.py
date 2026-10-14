"""Integration test: a detector that cannot load stops the node instead of degrading silently."""
import unittest

import launch
import launch_ros.actions
import launch_testing.actions
import launch_testing.asserts
import pytest

DETECTOR = launch_ros.actions.Node(
    package='companion_perception',
    executable='grounded_detector_node',
    name='grounded_detector_node',
    parameters=[{
        'backend': 'owlv2',
        'device': 'cpu',
        'depth_mode': 'none',
        'watch_labels': [''],
    }],
)


@pytest.mark.launch_test
def generate_test_description():
    """Ask for a real backend in an environment that cannot load it."""
    return launch.LaunchDescription([DETECTOR, launch_testing.actions.ReadyToTest()]), {}


class TestDetectorLoadFailure(unittest.TestCase):
    """The failure must be logged with its cause."""

    def test_load_error_is_logged(self, proc_output):
        """The log names the DetectorLoadError, so the cause is visible."""
        proc_output.assertWaitFor('DetectorLoadError', process=DETECTOR, timeout=30)


@launch_testing.post_shutdown_test()
class TestDetectorExitCode(unittest.TestCase):
    """The process must end with a failure code, never keep running on a fallback."""

    def test_exit_code_is_non_zero(self, proc_info):
        """Exit code 1 signals the load failure to launch and systemd."""
        launch_testing.asserts.assertExitCodes(proc_info, [1], process=DETECTOR)
