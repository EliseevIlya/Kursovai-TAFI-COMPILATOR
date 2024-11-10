import globals


def convert(numbers):
    parsed_numbers = {}
    for number, id in numbers.items():
        if any(char in number for char in "Ee.") and number[-1].lower() != 'h':
            new_number = float(number)
        elif number[-1].lower() == 'h':
            new_number = int(number[:-1], 16)
        elif number[-1].lower() == 'o':
            new_number = int(number[:-1], 8)
        elif number[-1].lower() == 'b':
            new_number = int(number[:-1], 2)
        elif number[-1].lower() == 'd':
            new_number = int(number[:-1])
        else:
            new_number = int(number)
        parsed_numbers[id] = type(new_number).__name__
    globals.numbers_type = parsed_numbers

