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
    """"
    for char in token[1:]:
        if not (is_letter(char) or char.isdigit()):
            return False
    return True
    """


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

""""
def is_valid_number(token):
   Проверка, является ли токен числом.
    if token[-1].lower() in ['h', 'd', 'o', 'b']:
        # Числа с обозначением системы счисления (H/h, D/d, O/o, B/b)
        base = token[-1].lower()
        digits = token[:-1]

        if base == 'h':  # Шестнадцатеричная система
            return all(c in '0123456789abcdefABCDEF' for c in digits)
        elif base == 'd':  # Десятичная система
            return all(c.isdigit() for c in digits)
        elif base == 'o':  # Восьмеричная система
            return all(c in '01234567' for c in digits)
        elif base == 'b':  # Двоичная система
            return all(c in '01' for c in digits)

    # Обработка чисел с префиксами
    if is_hex_prefix(token):
        # Шестнадцатеричное число с префиксом 0x/0X
        return all(c in '0123456789abcdefABCDEF' for c in token[2:])

    try:
        # Попробуем преобразовать токен в число с плавающей точкой
        float(token)
        return True
    except ValueError:
        return False
"""

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

''''def split_token(token, delimiters):
    
    parts = []
    current_part = ""
    i = 0
    while i < len(token):
        # Проверим на наличие составного разделителя
        two_char_delim = token[i:i+2]  # Получаем текущий и следующий символы
        if two_char_delim in delimiters:
            if current_part:
                parts.append(current_part)
                current_part = ""
            parts.append(two_char_delim)
            i += 2
        elif token[i] in delimiters:
            if current_part:
                parts.append(current_part)
                current_part = ""
            parts.append(token[i])
            i += 1
        else:
            current_part += token[i]
            i += 1
    if current_part:
        parts.append(current_part)
    return parts '''''
