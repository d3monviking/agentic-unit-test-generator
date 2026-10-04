import pytest
from solution import is_armstrong

def test_negative_number():
    assert is_armstrong(-1) == False

def test_zero():
    assert is_armstrong(0) == True

def test_single_digit_armstrong():
    assert is_armstrong(5) == True

def test_two_digit_non_armstrong():
    assert is_armstrong(10) == False

def test_three_digit_armstrong():
    assert is_armstrong(153) == True

def test_three_digit_non_armstrong():
    assert is_armstrong(100) == False

def test_four_digit_armstrong():
    assert is_armstrong(1634) == True

def test_four_digit_non_armstrong():
    assert is_armstrong(1000) == False