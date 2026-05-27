# The robot's expressed emotion.
# Produced by the Brain; consumed by the Face (and later Audio).

# Emotion vocabulary (string constants for the `emotion` field below):
string NEUTRAL=neutral
string HAPPY=happy
string SAD=sad
string ANGRY=angry
string CRY=cry
string LOVE=love
string SURPRISE=surprise
string SLEEPY=sleepy

std_msgs/Header header   # timestamp + frame (standard ROS practice)
string emotion           # one of the constants above
float32 intensity        # 0.0 (subtle) .. 1.0 (max)
string source            # producer, e.g. "brain" or "manual"
