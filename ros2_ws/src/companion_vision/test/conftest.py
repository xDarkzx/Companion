"""Skip tests that need real model weights unless explicitly requested."""
import os

import pytest


def pytest_collection_modifyitems(config, items):
    """Model tests download weights and want a GPU, so they run only on request."""
    if os.environ.get('COMPANION_MODEL_TESTS') == '1':
        return
    skip = pytest.mark.skip(reason='set COMPANION_MODEL_TESTS=1 to run model tests')
    for item in items:
        if 'models' in item.keywords:
            item.add_marker(skip)
