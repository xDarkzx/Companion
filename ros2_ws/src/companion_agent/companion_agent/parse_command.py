"""Parse compound voice commands into ordered behavior steps."""
from dataclasses import dataclass
import re

# Split "go to kitchen and patrol" → parts
_AND_RE = re.compile(r'\s+and\s+', re.IGNORECASE)
_GO_TO_RE = re.compile(
    r'(?:go to|goto|go\s+to the|drive to|navigate to)\s+(?P<place>[a-z][a-z0-9_ ]*?)'
    r'(?:\s+and|\s*$)',
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CommandStep:
    """One step in a multi-part command plan."""

    behavior: str
    target: str = ''


@dataclass(frozen=True)
class CommandPlan:
    """Ordered steps the agent executes."""

    steps: tuple[CommandStep, ...]


def parse_command(text: str, known_places: frozenset[str]) -> CommandPlan | None:
    """Turn natural language into a behavior plan, or None if unrecognized."""
    cleaned = ' '.join(text.strip().lower().split())
    if not cleaned:
        return None

    if cleaned in {'stop', 'stop now', 'halt', 'freeze'}:
        return CommandPlan(steps=(CommandStep('stop'),))

    steps: list[CommandStep] = []

    for part in _AND_RE.split(cleaned):
        part = part.strip()
        if not part:
            continue

        go_match = _GO_TO_RE.search(part + ' ')
        if go_match or part.startswith('go to ') or part.startswith('goto '):
            place = _extract_place(part, known_places)
            if place:
                steps.append(CommandStep('go_to_place', place))
                continue
            return None

        behavior = _single_behavior(part)
        if behavior:
            steps.append(CommandStep(behavior))
            continue

        return None

    if not steps:
        return None
    return CommandPlan(steps=tuple(steps))


def _extract_place(part: str, known_places: frozenset[str]) -> str | None:
    """Resolve a place name from a go-to phrase."""
    for place in sorted(known_places, key=len, reverse=True):
        if place in part.replace('_', ' '):
            return place
        if place.replace('_', ' ') in part:
            return place
    return None


def _normalize_token(part: str) -> str:
    """Normalize a single token to snake_case."""
    return part.strip().lower().replace('-', '_').replace(' ', '_')


def _single_behavior(part: str) -> str | None:
    """Map a single clause to a canonical behavior."""
    phrase_map = (
        ('play with the dog', 'play_with_dog'),
        ('patrol the home', 'patrol'),
        ('patrol home', 'patrol'),
        ('patrol', 'patrol'),
        ('follow me', 'follow'),
        ('go explore', 'explore'),
        ('explore', 'explore'),
        ('go home', 'go_home'),
        ('come home', 'go_home'),
    )
    for phrase, behavior in phrase_map:
        if phrase in part:
            return behavior

    token = _normalize_token(part)
    allowed = {
        'idle', 'follow', 'patrol', 'play_with_dog', 'explore', 'stop', 'go_home',
    }
    if token in allowed:
        return token
    return None


def plan_to_reply(plan: CommandPlan) -> str:
    """Turn a behavior plan into a short spoken acknowledgment."""
    from companion_voice.reply_catalog import going_place_text, phrase_text

    if not plan.steps:
        return phrase_text('ack_ok')
    if len(plan.steps) == 1 and plan.steps[0].behavior == 'stop':
        return phrase_text('stop')

    parts: list[str] = []
    for step in plan.steps:
        if step.behavior == 'go_to_place':
            parts.append(going_place_text(step.target))
        else:
            key_by_behavior = {
                'patrol': 'patrol',
                'follow': 'follow',
                'explore': 'explore',
                'go_home': 'go_home',
                'play_with_dog': 'on_it',
                'idle': 'standing_by',
                'stop': 'stop',
            }
            parts.append(phrase_text(key_by_behavior.get(step.behavior, 'ack_ok')))

    if len(parts) == 1:
        return parts[0]
    return f'OK. {parts[0]} Then {parts[1].lower()}.'
