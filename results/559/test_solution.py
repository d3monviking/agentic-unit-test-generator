from solution import max_subarray_sum

def test_empty_array():
    assert max_subarray_sum([]) == 0

def test_single_positive():
    assert max_subarray_sum([5]) == 5

def test_single_negative():
    assert max_subarray_sum([-3]) == -3

def test_all_negative():
    assert max_subarray_sum([-2, -1, -3]) == -1

def test_mixed_with_positive_sum():
    assert max_subarray_sum([2, -1, 3]) == 4

def test_reset_at_start():
    assert max_subarray_sum([-1, 2, 3]) == 5

def test_all_zeros():
    assert max_subarray_sum([0, 0, 0]) == 0