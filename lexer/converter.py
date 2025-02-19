import globals
import struct


def convert(numbers):
    parsed_numbers = {}
    for number, id in numbers.items():
        if any(char in number for char in "Ee.") and number[-1].lower() != 'h':
            new_number = float(number)
            binary_repr = ''.join(f'{byte:08b}' for byte in struct.pack('!f', new_number))
            globals.numbers_table_print[id] = binary_repr
        elif number[-1].lower() == 'h':
            new_number = int(number[:-1], 16)
            globals.numbers_table_print[id] = bin(new_number)
        elif number[-1].lower() == 'o':
            new_number = int(number[:-1], 8)
            globals.numbers_table_print[id] = bin(new_number)
        elif number[-1].lower() == 'b':
            new_number = int(number[:-1], 2)
            globals.numbers_table_print[id] = bin(new_number)
        elif number[-1].lower() == 'd':
            new_number = int(number[:-1])
            globals.numbers_table_print[id] = bin(new_number)
        else:
            new_number = int(number)
            globals.numbers_table_print[id] = bin(new_number)
        parsed_numbers[id] = type(new_number).__name__
    globals.numbers_type = parsed_numbers

    print("Numbers in bin view :", globals.numbers_table_print)
    with open("BinNumbers.txt", 'w') as outfile:
        outfile.write(str(globals.numbers_table_print))
