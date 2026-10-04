import pytest
from solution import dog_years

def test_dog_years_zero_or_negative():
    assert dog_years(0) == 0
    assert dog_years(-5) == 0

def test_dog_years_one():
    assert dog_years(1) == 15

def test_dog_years_two():
    assert dog_years(2) == 24

def test_dog_years_three():
    assert dog_years(3) == 29

def test_dog_years_four():
    assert dog_years(4) == 34