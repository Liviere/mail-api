import re


def check_pattern(pattern, value):
    check = re.match(pattern, value)
    if not check:
        return False
    return True


def validate_email(email):
    # Email pattern
    patt = (
        r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?'
        r':\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*'
        r'|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f'
        r'\x21\x23-\x5b\x5d-\x7f]|\\[\x01'
        r'-\x09\x0b\x0c\x0e-\x7f])*")@(?:'
        r'(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])'
        r'?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])'
        r'?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1'
        r'[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:'
        r'(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]'
        r'|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]'
        r':(?:[\x01-\x08\x0b\x0c\x0e-\x1f'
        r'\x21-\x5a\x53-\x7f]|\\[\x01-'
        r'\x09\x0b\x0c\x0e-\x7f])+)\])')
    return check_pattern(patt, email)
