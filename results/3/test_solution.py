from solution import is_non_prime
import pytest

def test_n_leq_1():
    assert is_non_prime(1) is True
    assert is_non_prime(0) is True
    assert is_non_prime(-5) is True

def test_prime_number():
    assert is_non_prime(2) is False
    assert is_non_prime(3) is False
    assert is_non_prime(13) is False

def test_composite_small():
    assert is_non_prime(4) is True
    assert is_non_prime(9) is True
    assert is_non_prime(15) is True

def test_composite_larger():
    assert is_non_prime(25) is True
    assert is_non_prime(49) is True

def test_edge_square_root():
    assert is_non_prime(16) is True  # sqrt = 4, divisor found
    assert is_non_prime(36) is True  # sqrt = 6, divisor found

def test_prime_large():
    assert is_non_prime(97) is False
    assert is_non_prime(101) is False

def test_composite_large():
    assert is_non_prime(100) is True
    assert is_non_prime(121) is True

def test_zero_iterations():
    # n = 2, range(2, int(sqrt(2))+1) -> range(2,2) empty
    assert is_non_prime(2) is False
    # n = 3, range(2, int(sqrt(3))+1) -> range(2,2) empty
    assert is_non_prime(3) is False