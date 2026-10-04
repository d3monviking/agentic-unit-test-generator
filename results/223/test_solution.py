import pytest
from solution import has_majority_element

def test_empty_array():
    assert has_majority_element([]) == False

def test_single_element():
    assert has_majority_element([5]) == True

def test_two_elements_no_majority():
    assert has_majority_element([1, 2]) == False

def test_two_elements_with_majority():
    assert has_majority_element([2, 2]) == True

def test_three_elements_no_majority():
    assert has_majority_element([1, 2, 3]) == False

def test_three_elements_with_majority():
    assert has_majority_element([2, 2, 3]) == True

def test_four_elements_no_majority():
    assert has_majority_element([1, 2, 3, 4]) == False

def test_four_elements_with_majority():
    assert has_majority_element([2, 2, 2, 3]) == True

def test_candidate_not_found_first():
    assert has_majority_element([1, 3, 5, 7]) == False

def test_candidate_not_found_last():
    assert has_majority_element([1, 3, 5, 7]) == False

def test_candidate_found_at_end():
    assert has_majority_element([1, 2, 3, 3, 3]) == True

def test_candidate_found_at_beginning():
    assert has_majority_element([1, 1, 1, 2, 3]) == True

def test_candidate_not_found_middle():
    assert has_majority_element([1, 2, 4, 5, 6]) == False