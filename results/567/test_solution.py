from solution import is_sorted

def test_empty_list():
    assert is_sorted([]) == True

def test_single_element():
    assert is_sorted([5]) == True

def test_two_elements_sorted():
    assert is_sorted([1, 2]) == True

def test_two_elements_unsorted():
    assert is_sorted([2, 1]) == False

def test_three_elements_sorted():
    assert is_sorted([1, 2, 3]) == True

def test_three_elements_unsorted_at_end():
    assert is_sorted([1, 3, 2]) == False

def test_three_elements_unsorted_at_start():
    assert is_sorted([3, 1, 2]) == False

def test_all_equal_elements():
    assert is_sorted([7, 7, 7]) == True