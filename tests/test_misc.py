import pytest

from solution.misc import search_upper_bound, search_value


@pytest.mark.parametrize("target", [0, 1, 2, 7, 64, 129])
def test_search_value_finds_exact_integer(target: int) -> None:
    def smaller(guess: int) -> bool:
        return target < guess

    def larger(guess: int) -> bool:
        return target > guess

    assert search_value(0, 256, smaller, larger) == target


@pytest.mark.parametrize(
    ("target", "expected_upper_bound"),
    [(0, 1), (1, 2), (2, 4), (7, 8), (64, 128)],
)
def test_search_upper_bound_doubles_until_above_target(
    target: int, expected_upper_bound: int
) -> None:
    assert search_upper_bound(lambda guess: target < guess) == expected_upper_bound


def test_search_value_returns_none_when_value_is_outside_range() -> None:
    target = 20

    assert search_value(0, 10, lambda guess: target < guess, lambda guess: target > guess) is None
