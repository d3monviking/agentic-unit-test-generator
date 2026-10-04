from solution import first_repeated_char

def test_empty_string():
    assert first_repeated_char("") is None

def test_no_repeated_chars():
    assert first_repeated_char("abc") is None

def test_first_char_repeated_immediately():
    assert first_repeated_char("aabc") == 'a'

def test_first_repeated_char_not_first():
    assert first_repeated_char("abca") == 'a'

def test_first_repeated_char_later_in_string():
    assert first_repeated_char("abbc") == 'b'

def test_first_repeated_char_with_spaces():
    assert first_repeated_char("a b c a") == 'a'

def test_first_repeated_char_case_sensitive():
    assert first_repeated_char("aA") is None

def test_first_repeated_char_all_same():
    assert first_repeated_char("aaaa") == 'a'