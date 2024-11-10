def float_to_bin(number: str) -> str:
    # Разбираем число и проверяем наличие экспоненциальной части
    if 'e' in number or 'E' in number:
        base, exponent = number.split('e') if 'e' in number else number.split('E')
        base = float(base)  # Преобразуем основную часть в float
        exponent = int(exponent)  # Преобразуем экспоненту в int
    else:
        base = float(number)
        exponent = 0

    # Отделяем целую и дробную часть числа
    int_part, frac_part = divmod(abs(base), 1)
    int_part = int(int_part)

    # Преобразуем целую часть в двоичную систему
    bin_int_part = bin(int_part)[2:] if int_part != 0 else '0'

    # Преобразуем дробную часть в двоичную систему
    bin_frac_part = []
    while frac_part and len(bin_frac_part) < 52:  # Ограничение длины мантиссы (IEEE 754)
        frac_part *= 2
        bit, frac_part = divmod(frac_part, 1)
        bin_frac_part.append(str(int(bit)))

    bin_frac_part = ''.join(bin_frac_part)

    # Если число имеет экспоненциальную часть, сдвигаем мантиссу
    if exponent != 0:
        bin_int_part = bin(int(int_part * (2 ** exponent)))[2:]
        bin_frac_part = ''  # Пренебрегаем дробной частью, если экспонента велика

    # Формируем результат
    result = f'{bin_int_part}' + (f'.{bin_frac_part}' if bin_frac_part else '')

    # Добавляем знак
    if base < 0:
        result = '-' + result

    return result

if __name__ == '__main__':
    # Примеры использования
    print(float_to_bin("123.456"))        # Пример обычного числа с плавающей точкой
    print(float_to_bin("1.23e5"))         # Пример числа в научной нотации
    print(float_to_bin("-0.125"))         # Пример отрицательного числа
    print(int('100',2))
