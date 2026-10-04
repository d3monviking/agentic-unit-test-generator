from solution import find_similar_elements

def test_both_empty():
    assert find_similar_elements((), ()) == ()

def test_first_empty():
    assert find_similar_elements((), (1, 2)) == ()

def test_second_empty():
    assert find_similar_elements((1, 2), ()) == ()

def test_no_common_elements():
    assert find_similar_elements((1, 2), (3, 4)) == ()

def test_one_common_element():
    assert find_similar_elements((1, 2), (2, 3)) == (2,)

def test_multiple_common_elements():
    assert find_similar_elements((1, 2, 3), (2, 3, 4)) == (2, 3)

def test_duplicate_elements_in_input():
    assert find_similar_elements((1, 1, 2), (1, 2, 2)) == (1, 2)