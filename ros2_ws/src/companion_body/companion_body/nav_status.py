"""Nav status strings shared by nav_bridge and agent."""
IDLE = 'idle'
NAVIGATING = 'navigating'
ARRIVED = 'arrived'
FAILED = 'failed'
FOLLOWING = 'following'

NAV_BEHAVIORS = frozenset({'go_to_place', 'go_home'})
MOTION_NAV_STATUSES = frozenset({FOLLOWING})
