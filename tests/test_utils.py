import pytest
from utils import _require_one_of


def test_require_one_of_raises_when_none_provided():
    with pytest.raises(ValueError, match="user_id or graph_id"):
        _require_one_of(user_id=None, graph_id=None)


def test_require_one_of_raises_when_both_provided():
    with pytest.raises(ValueError, match="Provide only one"):
        _require_one_of(user_id="u1", graph_id="g1")


def test_require_one_of_passes_when_one_provided():
    _require_one_of(user_id="u1", graph_id=None)
    _require_one_of(user_id=None, graph_id="g1")
