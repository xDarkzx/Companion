# High-level behavior command (voice, agent, or manual).
# Nav2 / vendor drivers consume these via companion_behaviors + companion_body.

std_msgs/Header header
string behavior    # idle, follow, patrol, go_to_place, harass_dog, explore, stop, go_home
string target      # named place (kitchen) or person; empty if not applicable
string source      # voice, vision, agent, manual, test, behaviors
float32 intensity  # 0.0-1.0 e.g. playfulness for harass_dog
