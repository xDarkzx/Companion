"""Map RobotEmotion strings to ASCII renderer mood keys (no pygame)."""

ROS_TO_MOOD = {
    'neutral': 'neutral',
    'happy': 'happy',
    'sad': 'sad',
    'angry': 'angry',
    'cry': 'cry',
    'love': 'love',
    'surprise': 'surprise',
    'sleepy': 'sleepy',
}


def mood_for_emotion(emotion: str) -> str:
    """Map a RobotEmotion string to a renderer mood (defaults to neutral)."""
    return ROS_TO_MOOD.get(emotion.lower(), 'neutral')
