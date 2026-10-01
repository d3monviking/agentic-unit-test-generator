import pytest
from solution import largest_numbers

def test_k_zero():
    assert largest_numbers([1, 2, 3], 0) == []

def test_k_greater_equal_len():
    assert largest_numbers([1, 2, 3], 5) == [3, 2, 1]
    assert largest_numbers([5, -1, 2], 3) == [5, 2, -1]

def test_normal_case_single_k():
    assert largest_numbers([1, 2, 3], 1) == [3]

def test_normal_case_multiple_k():
    assert largest_numbers([3, 1, 4, 1, 5, 9, 2, 6], 3) == [9, 6, 5]

def test_all_equal():
    assert largest_numbers([7, 7, 7, 7], 2) == [7, 7]

def test_negative_numbers():
    assert largest_numbers([-5, -2, -9, -1], 2) == [-1, -2]

def test_mixed_numbers():
    assert largest_numbers([-1, 0, 1, -2, 2], 3) == [2, 1, 0]

def test_k_equals_len():
    assert largest_numbers([10, 20, 30], 3) == [30, 20, 10]