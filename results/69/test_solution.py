from solution import contains_sublist

def test_empty_sublist():
    assert contains_sublist([1, 2, 3], []) == True

def test_sublist_longer_than_main():
    assert contains_sublist([1, 2], [1, 2, 3]) == False

def test_sublist_at_start():
    assert contains_sublist([1, 2, 3, 4], [1, 2]) == True

def test_sublist_in_middle():
    assert contains_sublist([1, 2, 3, 4], [2, 3]) == True

def test_sublist_at_end():
    assert contains_sublist([1, 2, 3, 4], [3, 4]) == True

def test_sublist_not_present():
    assert contains_sublist([1, 2, 3, 4], [2, 4]) == False

def test_sublist_equal_to_main():
    assert contains_sublist([1, 2, 3], [1, 2, 3]) == True

def test_no_iteration_when_sublist_longer():
    assert contains_sublist([1], [2, 3]) == False