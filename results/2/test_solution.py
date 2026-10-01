from solution import find_similar_elements

def test_both_empty():
    assert find_similar_elements([], []) == []

def test_one_empty():
    assert find_similar_elements([(1, 2)], []) == []
    assert find_similar_elements([], [(3, 4)]) == []

def test_no_overlap():
    assert find_similar_elements([(1, 2)], [(3, 4)]) == []

def test_single_match():
    assert find_similar_elements([(1, 2)], [(1, 2)]) == [(1, 2)]

def test_multiple_matches():
    assert set(find_similar_elements([(1, 2), (3, 4), (5, 6)], [(3, 4), (5, 6), (7, 8)])) == {(3, 4), (5, 6)}

def test_duplicate_in_input():
    assert find_similar_elements([(1, 2), (1, 2)], [(1, 2)]) == [(1, 2)]

def test_order_independence():
    result = find_similar_elements([(2, 1), (3, 4)], [(3, 4), (2, 1)])
    assert set(result) == {(2, 1), (3, 4)}

def test_mixed_types():
    assert find_similar_elements([(1, 'a'), (2, 'b')], [(2, 'b'), (3, 'c')]) == [(2, 'b')]