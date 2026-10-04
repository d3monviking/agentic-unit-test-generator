import pytest
from solution import diff_first_even_odd

def test_first_even_then_odd():
    assert diff_first_even_odd([2, 3]) == -1

def test_first_odd_then_even():
    assert diff_first_even_odd([1, 2]) == 1

def test_even_at_end():
    assert diff_first_even_odd([1, 3, 5, 2]) == 1

def test_odd_at_end():
    assert diff_first_even_odd([2, 4, 6, 1]) == 1

def test_no_even():
    assert diff_first_even_odd([1, 3, 5]) is None

def test_no_odd():
    assert diff_first_even_odd([2, 4, 6]) is None

def test_empty_list():
    assert diff_first_even_odd([]) is None

def test_both_found_in_middle():
    assert diff_first_even_odd([1, 2, 3, 4]) == -1