def float_to_binary(num_str):
    # Преобразуем строку в float
    num = float(num_str)

    # Разделяем целую и дробную части
    integer_part = int(num)
    fractional_part = num - integer_part

    # Конвертируем целую часть в двоичную систему
    binary_integer_part = bin(integer_part)[2:]  # [2:] убирает префикс '0b'

    # Конвертируем дробную часть в двоичную систему
    binary_fractional_part = []
    while fractional_part != 0 and len(binary_fractional_part) < 32:  # Ограничим длину дробной части
        fractional_part *= 2
        bit = int(fractional_part)
        binary_fractional_part.append(str(bit))
        fractional_part -= bit

    # Объединяем целую и дробную части
    if binary_fractional_part:
        return f"{binary_integer_part}.{''.join(binary_fractional_part)}"
    else:
        return binary_integer_part

if __name__ == '__main__':
    # Примеры использования
    a = float_to_binary("1.23")
    print(a)
    print(int(a,2))
    a = float_to_binary("2e10")
    print(a)
    print(int(a, 2))
    a = float_to_binary("11.2e-10")
    print(a)
    print(int(a, 2))
    a = float_to_binary("1.23e2")
    print(a)
    print(int(a, 2))
    a = float_to_binary("-1.23e2")
    print(a)
    print(int(a, 2))
    a = float_to_binary("-1.23e2")
    print(a)
    print(int(a, 2))


