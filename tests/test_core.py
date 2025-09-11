from mlops_vision_service.core import add


def test_add() -> None:
    assert add(2, 3) == 5
