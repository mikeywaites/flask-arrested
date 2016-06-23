
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock  # NOQA

import pytest

from arrested.handlers import Handler


def test_handler_sets_params():

    handler = Handler(one=1, two=2)
    assert handler.params == {'one': 1, 'two': 2}


def test_handler_to_json():

    handler = Handler()
    handler.data = {'one': 1}
    assert handler.to_json() == '{"one": 1}'


def test_handler_must_implement_handle_method():

    handler = Handler()
    with pytest.raises(NotImplementedError):
        handler.process({'one': 1})
