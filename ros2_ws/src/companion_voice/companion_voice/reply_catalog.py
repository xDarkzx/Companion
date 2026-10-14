"""Canonical robot replies — every spoken line the agent uses maps to one phrase clip."""
from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ReplyPhrase:
    """One pre-generated speech clip."""

    key: str
    text: str
    sfx_before: str = ''  # optional beep from assets/sfx (face/voice)


# All spoken lines. Keys become hello.wav, stop.wav, etc.
REPLY_PHRASES: dict[str, ReplyPhrase] = {
    # --- Greetings (boot + chat) ---
    'hello': ReplyPhrase('hello', 'Hello!'),
    'hi': ReplyPhrase('hi', 'Hi there!'),
    'welcome': ReplyPhrase('welcome', "Hi! I'm Companion, your robot friend."),
    'how_are_you': ReplyPhrase('how_are_you', 'How are you today?'),
    'nice_to_meet': ReplyPhrase('nice_to_meet', 'Nice to meet you!'),
    'here_to_help': ReplyPhrase('here_to_help', "I'm here to help."),
    # --- Command acknowledgments ---
    'ack_ok': ReplyPhrase('ack_ok', 'OK.'),
    'going': ReplyPhrase('going', 'On my way!'),
    'patrol': ReplyPhrase('patrol', 'Starting patrol.'),
    'follow': ReplyPhrase('follow', 'Following you.'),
    'explore': ReplyPhrase('explore', 'Going to explore.'),
    'go_home': ReplyPhrase('go_home', 'Heading home.'),
    'stop': ReplyPhrase('stop', 'Stopping now.'),
    'standing_by': ReplyPhrase('standing_by', 'Standing by.'),
    'on_it': ReplyPhrase('on_it', 'On it.'),
    # Per-place (generated for each entry in places.yaml)
    'going_kitchen': ReplyPhrase('going_kitchen', 'On my way to the kitchen.'),
    'going_bedroom': ReplyPhrase('going_bedroom', 'On my way to the bedroom.'),
    'going_dock': ReplyPhrase('going_dock', 'On my way to the dock.'),
    # --- Memory ---
    'remember_ok': ReplyPhrase('remember_ok', "Got it. I'll remember that."),
    'recall_lead': ReplyPhrase('recall_lead', 'I remember.'),
    'no_memory': ReplyPhrase('no_memory', "I don't have that saved yet."),
    'memory_off': ReplyPhrase('memory_off', 'Memory is not set up yet.'),
    # --- Errors ---
    'dont_understand': ReplyPhrase(
        'dont_understand', "Sorry, I didn't understand that."
    ),
    'nav_failed': ReplyPhrase('nav_failed', 'Navigation failed.'),
    # --- Social / chat ---
    'yes': ReplyPhrase('yes', 'Yes.'),
    'no': ReplyPhrase('no', 'No.'),
    'okay': ReplyPhrase('okay', 'Okay.'),
    'thanks': ReplyPhrase('thanks', 'Thank you!'),
    'sorry': ReplyPhrase('sorry', 'Sorry about that.'),
    'goodbye': ReplyPhrase('goodbye', 'Goodbye! See you later.'),
    # --- Emotion-colored chat (LLM should stay near these) ---
    'happy': ReplyPhrase('happy', 'That makes me happy!'),
    'sad': ReplyPhrase('sad', 'That is sad.'),
    'thinking': ReplyPhrase('thinking', 'Let me think.'),
    'confused': ReplyPhrase('confused', 'What was that?'),
    'ready': ReplyPhrase('ready', "I'm ready when you are."),
}

BOOT_GREETING_KEYS: tuple[str, ...] = (
    'hello',
    'welcome',
    'how_are_you',
    'hi',
    'here_to_help',
)

# Short lines the LLM may use when paraphrasing (first match wins).
TEXT_RULES: tuple[tuple[str, str], ...] = (
    (r'\b(hello|hi there|hey there|good morning|good evening)\b', 'hello'),
    (r"\b(i'm companion|i am companion|your robot friend)\b", 'welcome'),
    (r'\bhow are you\b', 'how_are_you'),
    (r"\b(didn't understand|don't understand|not understand)\b", 'dont_understand'),
    (r"\b(i'll remember|will remember|got it\. i'll)\b", 'remember_ok'),
    (r'\b(i remember|here\'s what i remember)\b', 'recall_lead'),
    (r"\b(don't have that|not saved yet|no memory)\b", 'no_memory'),
    (r'\b(memory is not|not configured)\b', 'memory_off'),
    (r'\bon my way to the kitchen\b', 'going_kitchen'),
    (r'\bon my way to the bedroom\b', 'going_bedroom'),
    (r'\bon my way to the dock\b', 'going_dock'),
    (r'\b(on my way|heading to|going to the)\b', 'going'),
    (r'\b(stopping|stop now)\b', 'stop'),
    (r'\bstarting patrol\b', 'patrol'),
    (r'\bpatrol\b', 'patrol'),
    (r'\bfollowing you\b', 'follow'),
    (r'\b(going to explore|exploring)\b', 'explore'),
    (r'\bheading home\b', 'go_home'),
    (r'\bstanding by\b', 'standing_by'),
    (r'\bon it\b', 'on_it'),
    (r'\bnavigation failed\b', 'nav_failed'),
    (r'\b(sorry|apolog)\b', 'sorry'),
    (r'\b(thank|thanks)\b', 'thanks'),
    (r'\b(bye|goodbye|see you later)\b', 'goodbye'),
    (r'\b(yes|sure|absolutely|of course)\b', 'yes'),
    (r'\b(no|nope|cannot|can\'t)\b', 'no'),
    (r'\b(happy|great|awesome|wonderful)\b', 'happy'),
    (r'\b(sad|that is sad)\b', 'sad'),
    (r'\b(let me think|thinking)\b', 'thinking'),
    (r'\b(what was that|huh)\b', 'confused'),
    (r'^ok[.,!]?$', 'ack_ok'),
)

EMOTION_PHRASE_KEY: dict[str, str] = {
    'happy': 'happy',
    'love': 'happy',
    'surprise': 'confused',
    'sad': 'sad',
    'cry': 'sad',
    'sleepy': 'thinking',
    'neutral': 'okay',
    'focused': 'thinking',
    'angry': 'no',
}


def phrase_text(key: str) -> str:
    """Return the spoken line for a phrase key."""
    entry = REPLY_PHRASES.get(key)
    if entry is None:
        raise KeyError(key)
    return entry.text


def going_place_key(place: str) -> str:
    """Phrase key for navigating to a named place."""
    slug = place.strip().lower().replace('-', '_').replace(' ', '_')
    return f'going_{slug}'


def going_place_text(place: str) -> str:
    """Spoken line for go-to-place; uses catalog or a generic line."""
    key = going_place_key(place)
    if key in REPLY_PHRASES:
        return phrase_text(key)
    label = place.replace('_', ' ')
    return f'On my way to the {label}.'


def recall_reply(fact: str) -> str:
    """Spoken recall line; clip plays lead-in, tail may use live TTS."""
    trimmed = fact.strip().rstrip('.')
    if not trimmed:
        return phrase_text('no_memory')
    return f'{phrase_text("recall_lead")} {trimmed}.'


def catalog_phrase_dict() -> dict[str, str]:
    """Flat key → text map for WAV generation."""
    return {key: entry.text for key, entry in REPLY_PHRASES.items()}


def extra_place_phrases(place_names: list[str]) -> dict[str, str]:
    """Build going_<place> lines for places not already in the catalog."""
    extra: dict[str, str] = {}
    for name in place_names:
        key = going_place_key(name)
        if key not in REPLY_PHRASES:
            label = name.replace('_', ' ')
            extra[key] = f'On my way to the {label}.'
    return extra


def text_slug(text: str) -> str:
    """Normalize reply text to a phrase key slug."""
    lower = text.strip().lower()
    return re.sub(r'[^a-z0-9]+', '_', lower).strip('_')[:80]
