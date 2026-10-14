"""Map natural-language phrases to companion behavior names (legacy simple router)."""
_SIMPLE_BEHAVIORS = frozenset({
    'idle', 'follow', 'patrol', 'harass_dog', 'explore', 'stop', 'go_home',
})

_PHRASE_MAP = (
    ('harass the dog', 'harass_dog'),
    ('harass dog', 'harass_dog'),
    ('chase the dog', 'harass_dog'),
    ('patrol the home', 'patrol'),
    ('patrol home', 'patrol'),
    ('follow me', 'follow'),
    ('go explore', 'explore'),
    ('come home', 'go_home'),
    ('go home', 'go_home'),
    ('stop', 'stop'),
)


def route_intent(text: str) -> str | None:
    """Return a canonical behavior name or None if unrecognized."""
    cleaned = ' '.join(text.strip().lower().split())
    if not cleaned:
        return None

    for phrase, behavior in _PHRASE_MAP:
        if phrase in cleaned:
            return behavior

    token = cleaned.replace('-', '_').replace(' ', '_')
    if token in _SIMPLE_BEHAVIORS:
        return token
    return None
