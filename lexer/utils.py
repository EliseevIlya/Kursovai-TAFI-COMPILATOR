def is_letter(char):
    return "a" <= char.lower() <= "z" or char == '_'


def is_hex_prefix(token):
    """Проверяем, является ли число шестнадцатеричным."""
    return token.lower().startswith('0x')


def is_valid_identifier(token):
    """Идентификатор начинается с буквы или '_' и может содержать буквы и цифры."""
    if not is_letter(token[0]) and token[0] != '_':
        return False
    return all("a" <= c.lower() <= "z" or "0" <= c <= "9" for c in token)


def is_part_of_number(current_token, next_char):
    """Проверка, является ли следующий символ частью числа с плавающей точкой или научной нотацией."""
    if current_token.isdigit() and next_char in '.eE':
        return True
    if '.' in current_token and next_char.isdigit():
        return True
    if 'e' in current_token.lower() and next_char in '+-' and current_token[-1].lower() == 'e':
        return True
    return False


def is_valid_number(token):
    """Проверка, является ли токен числом, поддерживая начальные знаки + и -."""

    if token[-1].lower() in 'hdob':
        # Определяем систему счисления
        base = token[-1].lower()
        digits = token[:-1]
        allowed_digits = {
            'h': '0123456789abcdefABCDEF',
            'd': '0123456789',
            'o': '01234567',
            'b': '01'
        }.get(base)
        return all(c in allowed_digits for c in digits)

    if is_hex_prefix(token):
        return all(c in '0123456789abcdefABCDEF' for c in token[2:])

    try:
        float(token)
        return True
    except ValueError:
        return False


"""Разделение токена, примыкающего к разделителям, на части."""


def split_token(token, delimiters):
    parts = []
    current_part = ""
    for char in token:
        if char in delimiters:
            if current_part:
                parts.append(current_part)
                current_part = ""
            parts.append(char)
        else:
            current_part += char
    if current_part:
        parts.append(current_part)
    return parts
