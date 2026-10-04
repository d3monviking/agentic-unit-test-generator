from solution import is_greater_than_all

def test_empty_array():
    assert is_greater_than_all([], 5) == True

def test_single_element_true():
    assert is_greater_than_all([3], 5) == True

def test_single_element_false_equal():
    assert is_greater_than_all([5], 5) == False

def test_single_element_false_less():
    assert is_greater_than_all([7], 5) == False

def test_multiple_elements_true():
    assert is_greater_than_all([1, 2, 3], 4) == True

def test_multiple_elements_false_one_false():
    assert is_greater_than_all([1, 2, 4], 3) == False

def test_multiple_elements_all_false():
    assert is_greater_than_all([6, 7, 8], 5) == False

def test_with_negative_numbers():
    assert is_greater_than_all([-3, -1, 0], 2) == True