from companion_vision.backends.grounding_dino import match_query, prompt_for


def test_prompt_joins_queries_with_full_stops():
    assert prompt_for(['red mug', 'dog']) == 'red mug. dog.'


def test_grounded_phrases_map_back_to_their_query():
    queries = ['mug', 'red mug', 'dog']
    assert match_query('red mug', queries) == 'red mug'
    assert match_query('Red  Mug', queries) == 'red mug'
    assert match_query('red', queries) == 'red mug'
    assert match_query('cat', queries) is None
    assert match_query('', queries) is None
