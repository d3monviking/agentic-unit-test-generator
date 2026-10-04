from solution import is_greater_than_all as check_greater
assert check_greater([1, 2, 3, 4, 5], 4) == 'No, entered number is less than those in the array'
assert check_greater([2, 3, 4, 5, 6], 8) == 'Yes, the entered number is greater than those in the array'
assert check_greater([9, 7, 4, 8, 6, 1], 11) == 'Yes, the entered number is greater than those in the array'
print('ORACLE_OK')