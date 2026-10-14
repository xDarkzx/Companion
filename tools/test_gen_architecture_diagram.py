"""Tests for the architecture diagram generated from the contract registry."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from companion_contracts import ServiceContract, TopicContract  # noqa: E402
from gen_architecture_diagram import render_mermaid, splice  # noqa: E402


def test_topics_and_services_become_labelled_edges():
    topics = {'/companion/tts_request': TopicContract(
        msg_type='String', publishers=frozenset({'companion_agent'}),
        subscribers=frozenset({'companion_voice'}))}
    services = {'/companion/find_object': ServiceContract(
        srv_type='FindObject', servers=frozenset({'companion_perception'}),
        clients=frozenset({'companion_agent'}))}
    text = render_mermaid(topics, services)
    assert text.startswith('```mermaid\nflowchart LR\n')
    assert '  agent -- "tts_request" --> voice' in text
    assert '  agent -. "find_object (service)" .-> perception' in text


def test_topics_without_a_subscriber_are_shown_as_outputs():
    topics = {'/companion/objects': TopicContract(
        msg_type='Detection3DArray', publishers=frozenset({'companion_perception'}),
        subscribers=frozenset())}
    assert '  perception -- "objects" --> out_objects(["objects"])' in render_mermaid(topics, {})


def test_splice_replaces_the_generated_block_only():
    doc = 'a\n<!-- diagram:start -->\nold\n<!-- diagram:end -->\nb\n'
    assert splice(doc, 'new\n') == 'a\n<!-- diagram:start -->\nnew\n<!-- diagram:end -->\nb\n'
