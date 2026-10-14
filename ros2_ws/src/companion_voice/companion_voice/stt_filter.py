"""Filter Whisper output — skip silence, noise, and hallucinated repeats."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TranscriptFilterResult:
    """Outcome of post-STT filtering."""

    text: str
    skipped: bool
    reason: str = ''


def filter_transcription(
    text: str,
    min_words: int = 2,
    max_word_repeat_ratio: float = 0.3,
) -> TranscriptFilterResult:
    """Drop empty, too-short, or repetitive Whisper hallucinations."""
    cleaned = text.strip()
    if not cleaned or len(cleaned) < 2:
        return TranscriptFilterResult('', True, 'empty')

    words = cleaned.split()
    if len(words) < min_words:
        return TranscriptFilterResult(cleaned, True, 'too_short')

    if len(words) > 5:
        counts: dict[str, int] = {}
        for word in words:
            counts[word] = counts.get(word, 0) + 1
        peak = max(counts.values()) / len(words)
        if peak > max_word_repeat_ratio:
            deduped = _dedupe_sentences(cleaned)
            if not deduped:
                return TranscriptFilterResult(cleaned, True, 'repetitive')
            dedup_words = deduped.split()
            if len(dedup_words) < min_words:
                return TranscriptFilterResult(cleaned, True, 'repetitive')
            return TranscriptFilterResult(deduped, False)

    return TranscriptFilterResult(cleaned, False)


def _dedupe_sentences(text: str) -> str:
    """Keep the first few unique sentence fragments from a noisy transcript."""
    parts = [part.strip() for part in text.split('.') if part.strip()]
    unique: list[str] = []
    seen: set[str] = set()
    for part in parts:
        if part in seen:
            continue
        unique.append(part)
        seen.add(part)
        if len(unique) >= 2:
            break
    if not unique:
        return ''
    result = '. '.join(unique)
    if not result.endswith('.'):
        result += '.'
    return result
