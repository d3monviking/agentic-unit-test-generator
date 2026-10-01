from solution import min_cost_path
import pytest

def test_start_to_start():
    cost = [[5]]
    assert min_cost_path(cost, 0, 0) == 5

def test_first_row():
    cost = [[1, 2, 3]]
    assert min_cost_path(cost, 0, 2) == 6

def test_first_col():
    cost = [[1], [2], [3]]
    assert min_cost_path(cost, 2, 0) == 6

def test_single_cell_2x2():
    cost = [[1, 2], [3, 4]]
    assert min_cost_path(cost, 1, 1) == 5

def test_2x2_path():
    cost = [[1, 2], [3, 4]]
    assert min_cost_path(cost, 1, 1) == 5

def test_3x3_all_equal():
    cost = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    assert min_cost_path(cost, 2, 2) == 3

def test_3x3_diagonal_cheapest():
    cost = [[5, 9, 3], [8, 2, 6], [4, 7, 1]]
    assert min_cost_path(cost, 2, 2) == 8

def test_larger_matrix():
    cost = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ]
    assert min_cost_path(cost, 2, 3) == 22