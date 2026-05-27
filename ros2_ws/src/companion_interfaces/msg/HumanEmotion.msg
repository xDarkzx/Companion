# The perceived emotion of the HUMAN (the empathy MOAT).
# Produced by Perception; consumed by the Brain.
# Defined now (Phase 1) as a contract; first used in Phase 3.

# Perceived-affect vocabulary (string constants for the `emotion` field below):
string UNKNOWN=unknown
string HAPPY=happy
string SAD=sad
string UPSET=upset
string NEUTRAL=neutral

std_msgs/Header header   # timestamp + frame
string emotion           # one of the constants above
float32 confidence       # 0.0 .. 1.0
string source            # e.g. "vision" or "voice"
