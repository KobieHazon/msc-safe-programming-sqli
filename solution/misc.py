"""
Helper functions for exercise_solver.py
"""

from collections.abc import Callable


def search_upper_bound(search_func: Callable[[int], bool]) -> int:
    """
    Does binary search upwards to look for upper bound to be later used in proper binary search
    :param search_func: boolean function to search upper bound for
    :return: upper bound
    """
    found_upper_bound = False
    upper_bound = 1
    while not found_upper_bound:
        if search_func(upper_bound):
            found_upper_bound = True
        else:
            upper_bound *= 2
    return upper_bound


def search_value(
    lower_bound: int,
    upper_bound: int,
    smaller_func: Callable[[int], bool],
    larger_func: Callable[[int], bool],
) -> int | None:
    """
    Runs binary search to look for value
    :param lower_bound: start lower bound in search
    :param upper_bound: start upper bound in search
    :param smaller_func: search function for the lower_than comparison
    :param larger_func: search function for the larger_than comparison
    :return: search result
    """
    while lower_bound <= upper_bound:
        middle = (upper_bound + lower_bound) // 2
        if smaller_func(middle):
            upper_bound = middle - 1

        else:
            if larger_func(middle):
                lower_bound = middle + 1
            else:
                return middle
