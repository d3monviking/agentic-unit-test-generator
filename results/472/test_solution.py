from solution import are_consecutive

def test_empty_list():
    assert are_consecutive([]) == False

def test_single_element():
    assert are_consecutive([5]) == True

def test_two_consecutive():
    assert are_consecutive([3, 4]) == True

def test_two_non_consecutive():
    assert are_consecutive([3, 5]) == False

def test_three_consecutive():
    assert are_consecutive([1, 2, 3]) == True

def test_three_non_consecutive_middle_gap():
    assert are_consecutive([1, 2, 4]) == False

def test_three_non_consecutive_end_gap():
    assert are_consecutive([1, 3, 4]) == False

def test_duplicates():
    assert are_consecutive([1, 2, 2, 3]) == False