import globals
from lexer.utils import *
from .converter import convert


class Lexer:

    def __init__(self):
        # Инициализируем таблицы

        self.keywords = {
            "let": 1, "if": 2, "then": 3, "else": 4, "end_else": 5, "for": 6,
            "do": 7, "while": 8, "input": 9, "output": 10, "%": 11, "!": 12, "$": 13, "loop": 14,
            "true": 15, "false": 16
        }
        self.delimiters = {
            "NE": 1, "EQ": 2, "LT": 3, "LE": 4, "GT": 5, "GE": 6,
            "plus": 7, "min": 8, "or": 9, "mult": 10, "div": 11, "and": 12,
            "~": 13, "{": 14, "}": 15, ";": 16, ",": 17, ":": 18, "(": 19, ")": 20,
            "=": 21, "/*": 22, "*/": 23
        }
        self.identifiers = {}
        self.numbers = {}


    def add_to_dict(self, lexeme, table):
        """Добавить лексему в таблицу, если её там ещё нет."""
        if lexeme not in table:
            table[lexeme] = len(table) + 1
        return table[lexeme]

    def process_token(self, token, outfile, line_num, position_in_line, line):

        """Обработка токенов и запись их в выходной файл."""
        if self.keywords.get(token) is not None:
            outfile.write(f"(1,{self.keywords.get(token)})")
            globals.lexemes.append((1, self.keywords.get(token)))
            #outfile.write(f"(1, {self.keywords.lookup(token)})  // {token}\n")
        elif self.delimiters.get(token) is not None:
            outfile.write(f"(2,{self.delimiters.get(token)})")
            globals.lexemes.append((2, self.delimiters.get(token)))
            #outfile.write(f"(2, {self.delimiters.lookup(token)})  // {token}\n")
        elif is_valid_identifier(token):
            outfile.write(f"(3,{self.add_to_dict(token, self.identifiers)})")
            globals.lexemes.append((3, self.add_to_dict(token, self.identifiers)))
            #outfile.write(f"(3, {self.identifiers.add(token)})  // {token}\n")
        elif is_valid_number(token):
            outfile.write(f"(4,{self.add_to_dict(token, self.numbers)})")
            globals.lexemes.append((4, self.add_to_dict(token, self.numbers)))
            #outfile.write(f"(4, {self.numbers.add(token)})  // {token}\n")
        else:
            print(f"Ошибка: некорректный токен '{token}'")
            # Определение типа ошибки
            '''
            if not is_valid_identifier(token):
                error_type = "Ошибка идентификатора"
                error_message = f"Идентификатор содержит недопустимые символы или начинается с цифры: {token}"
            else:
                error_type = "Неизвестный символ"
                error_message = f"Неизвестный или некорректный токен: {token}"
            '''

            if not is_valid_number(token):
                error_type = "Ошибка числа"
                error_message = f"Некорректный формат числа: {token}"

            # Запись ошибки в файл и консоль и остановка программы
            line = line.rstrip("\n")
            error_msg = f"{error_type}: {error_message} [строка {line_num} : {line} , позиция {position_in_line + 1}]\n"
            print(error_msg)
            exit()

    def tokenize(self, input_file, output_file):
        current_token = ""
        in_comment = False

        with open(input_file, 'r', encoding='utf8') as infile, open(output_file, 'w') as outfile:
            line_num = 0
            for line in infile:
                line_num += 1
                position_in_line = 0
                while position_in_line < len(line):
                    char = line[position_in_line]

                    if in_comment:
                        if line[position_in_line:position_in_line + 2] == "*/":
                            in_comment = False
                            position_in_line += 2
                        else:
                            position_in_line += 1
                        continue

                    if line[position_in_line:position_in_line + 2] == "/*":
                        in_comment = True
                        position_in_line += 2
                        continue

                    if is_letter(char) or char.isdigit() or char in "!%$":
                        current_token += char
                    elif char == '.' and line[position_in_line + 1].isdigit():
                        current_token += char  # Поддержка дробных чисел
                    elif char in 'eE' and current_token and (current_token[-1].isdigit() or current_token[-1] == '.'):
                        current_token += char  # Поддержка экспоненты
                    elif char in '+-' and is_part_of_number(current_token, char):
                        current_token += char  # Поддержка знака после 'e' в научной нотации
                    else:
                        if current_token:
                            self.process_token(current_token, outfile, line_num, position_in_line, line)
                            ''''
                            tokens = split_token(current_token, self.delimiters.table)
                            for token in tokens:
                                self.process_token(token, outfile, line_num, position_in_line, line)
                            '''''
                            current_token = ""
                        if char in self.delimiters:
                            double_delimiter = line[position_in_line:position_in_line + 2]
                            if double_delimiter in self.delimiters:
                                position_in_line += 1
                                self.process_token(double_delimiter, outfile, line_num, position_in_line, line)
                            else:
                                self.process_token(char, outfile, line_num, position_in_line, line)
                        # Ошибка неизвестного символа и выход из программы
                        if not (is_letter(char) or char.isdigit() or self.keywords.get(
                                char) or self.delimiters.get(char) or char.isspace()):
                            line = line.rstrip("\n")
                            print(
                                f"Ошибка - неизвестный символ {char} [строка {line_num} : {line} , позиция {position_in_line + 1}]")
                            exit()

                    if char.isspace() or char == '\n':
                        if current_token:
                            self.process_token(current_token, outfile, line_num, position_in_line, line)
                            ''''
                            tokens = split_token(current_token, self.delimiters.table)
                            for token in tokens:
                                self.process_token(token, outfile, line_num, position_in_line, line)
                            '''''
                            current_token = ""
                    position_in_line += 1

                if current_token:
                    self.process_token(current_token, outfile, line_num, position_in_line, line)
                    ''''
                    tokens = split_token(current_token, self.delimiters.table)
                    for token in tokens:
                        self.process_token(token, outfile, line_num, position_in_line, line)
                    '''''
                    current_token = ""
        #print(self.keywords, self.delimiters, self.identifiers, self.numbers, sep="\n")
        convert(self.numbers)

        reversed_dict = {v: k for k, v in self.identifiers.items()}
        globals.identifiers = self.identifiers
        globals.reversed_identifiers = reversed_dict

        reversed_dict = {v: k for k, v in self.numbers.items()}
        globals.reversed_numbers = reversed_dict
