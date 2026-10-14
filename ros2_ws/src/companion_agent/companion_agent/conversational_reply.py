"""Build prompts and pick LLM vs template replies for the agent."""
from __future__ import annotations

from companion_agent.llm_client import generate_reply, is_available
from companion_agent.parse_command import CommandPlan, plan_to_reply
from companion_memory.session_buffer import ChatTurn


def _history_from_turns(turns: tuple[ChatTurn, ...]) -> tuple[tuple[str, str], ...]:
    """Map session turns to Ollama chat roles."""
    mapped: list[tuple[str, str]] = []
    for turn in turns:
        role = 'user' if turn.role == 'user' else 'assistant'
        mapped.append((role, turn.text))
    return tuple(mapped)


def conversational_reply(
    provider: str,
    user_text: str,
    context: str,
    template: str,
    ollama_model: str,
    ollama_base_url: str,
    history: tuple[ChatTurn, ...] = (),
) -> str:
    """Prefer an LLM line when configured; otherwise use the template."""
    if provider.strip().lower() != 'ollama':
        return template
    if not is_available(ollama_base_url):
        return template
    llm_text = generate_reply(
        user_text,
        context=context,
        base_url=ollama_base_url,
        model=ollama_model,
        history=_history_from_turns(history),
    )
    return llm_text if llm_text else template


def reply_for_plan(
    provider: str,
    user_text: str,
    plan: CommandPlan,
    context: str,
    ollama_model: str,
    ollama_base_url: str,
    history: tuple[ChatTurn, ...] = (),
) -> str:
    """Speak a natural acknowledgment for a behavior plan."""
    template = plan_to_reply(plan)
    action_hint = f'The robot will: {template}'
    return conversational_reply(
        provider,
        user_text,
        f'{context}; {action_hint}' if context else action_hint,
        template,
        ollama_model,
        ollama_base_url,
        history=history,
    )
