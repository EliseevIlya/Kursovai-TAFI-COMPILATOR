from syntax.node import Node

class SyntaxError(Exception):
    pass

class Parser:

    def __init__(self, token_file):
        self.token_file = open(token_file, 'r')
        self.current_token = None
        self.previous_token = None  # Для хранения предыдущей лексемы
        self.next_token()

    def next_token(self):
        # Чтение токена непосредственно из файла
        token_str = ''
        char = self.token_file.read(1)

        # Пропускаем пробелы и другие ненужные символы
        while char and char not in '()':
            char = self.token_file.read(1)

        if not char:  # Если конец файла
            self.current_token = None
            return

        # Считываем токен внутри скобок
        token_str = char
        while char != ')':
            char = self.token_file.read(1)
            token_str += char

        # Преобразуем строку в кортеж
        self.previous_token = self.current_token  # сохраняем предыдущий токен
        self.current_token = eval(token_str)  # Преобразуем строку '(n, k)' в кортеж (n, k)
        print(self.current_token)

    def parse(self):
        """ <программа>::= «{» {/ (<описание> | <оператор>) ; /} «}» """
        program_node = Node("Program")
        if self.current_token == (2, 14):  # '{'
            self.next_token()
            while self.current_token != (2,15):  # пока не встретили }
                if self.current_token in [(2, 14),(1, 1),(1, 2), (1, 6), (1,7), (1, 9), (1, 10)] or self.current_token[0]==3: # { let if for do input output
                    self.parse_operator()
                if self.current_token == (2, 16):  # ';'
                    self.next_token()
                else:
                    raise SyntaxError(f"Ожидалась ; , но встречено {self.current_token} in program")

            # Проверяем конец программы на сочетание ;}
            if self.current_token == (2,15):
                if self.previous_token != (2,16):
                    raise SyntaxError("Ожидалась ;")
                self.next_token()  # Пропускаем '}'
                self.check_end_of_program()  # Проверяем, есть ли лексемы после окончания программы
            else:
                raise SyntaxError("Программа должна завершаться  '}'")
        else:
            raise SyntaxError("Программа должна начинаться с '{'")

    def check_end_of_program(self):
        """ Проверка на наличие лексем после завершения программы """

        if self.current_token is not None:
            raise SyntaxError(f"Лексемы после конца программы: {self.current_token}")


    def parse_declaration(self):
        """ <описание>::= { <идентификатор> { , <идентификатор> } : <тип> ; } """
        """"в присваивание (assigment) первый идентификатор уже обработан """
        while self.current_token == (2, 17):  # ','
            self.next_token()
            self.parse_identifier()
        if self.current_token == (2, 18):  # ':'
            self.next_token()
            self.parse_type()
            if self.current_token == (2,16):
                self.next_token()

            else:
                raise SyntaxError(f"Ожидалась ; , но встречено {self.current_token} in declaration")
        else:
            raise SyntaxError(f"Ожидался ':' после идентификаторов {self.current_token}")

    def parse_type(self):
        """ <тип>::= % | ! | $ """
        if self.current_token in [(1, 11), (1, 12), (1, 13)]:
            self.next_token()
        else:
            raise SyntaxError(f"Неверный тип переменной {self.current_token}")

    def parse_operator(self):
        """ <оператор>::= <составной> | <присваивания> | <условный> | <фиксированного_цикла> | <условного_цикла> | <ввода> | <вывода> """
        if self.current_token == (2, 14):  # '{' — составной оператор
            self.parse_compound()
        elif self.current_token == (1, 1) or self.current_token[0] == 3:  # let или идентификатор
            self.parse_assignment()
        elif self.current_token == (1, 2):  # if
            self.parse_conditional()
        elif self.current_token == (1, 6):  # for
            self.parse_fixed_loop()
        elif self.current_token == (1, 7):  # do
            self.parse_while_loop()
        elif self.current_token == (1, 9):  # input
            self.parse_input()
        elif self.current_token == (1, 10):  # output
            self.parse_output()
        else:
            raise SyntaxError(f"Некорректный оператор {self.current_token}")

    def parse_compound(self):
        """ <составной>::= «{» <оператор> { ; <оператор> } «}» """
        if self.current_token == (2, 14):  # '{'
            self.next_token()
            self.parse_operator()  # Разбираем первый оператор внутри составного оператора

            # Цикл для обработки последующих операторов, разделенных символом ';'
            while self.current_token == (2, 16):  # ';'
                self.next_token()
                self.parse_operator()  # Разбираем следующий оператор

            if self.current_token == (2, 15):  # '}'
                self.next_token()  # Закрываем составной оператор
            else:
                raise SyntaxError(f"Ожидалась '}}' для закрытия составного оператора, получено {self.current_token}")
        else:
            raise SyntaxError(f"Ожидалась '{{' для начала составного оператора, получено {self.current_token}")

    def parse_assignment(self):
        """ <присваивания> ::= [ let ] <идентификатор> = <выражение> """
        if self.current_token == (1, 1):  # let
            self.next_token()
        self.parse_identifier()
        if self.current_token == (2, 21):  # '='
            self.next_token()
            self.parse_expression()
        elif self.current_token == (2,17) or self.current_token == (2,18):
            self.parse_declaration()
        else:
            raise SyntaxError(f"Ожидался '=' после идентификатора {self.current_token}")

    def parse_expression(self):
        """ <выражение>::= <операнд>{<операции_группы_отношения><операнд>} """
        self.parse_operand()
        while self.current_token in [(2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6)]: # NE EQ LT LE GT GE
            self.next_token()
            self.parse_operand()

    def parse_operand(self):
        """ <операнд>::= <слагаемое>{<операции_группы_сложения><слагаемое>} """
        self.parse_term()
        while self.current_token in [(2, 7), (2, 8), (2, 9)]: # plus min or
            self.next_token()
            self.parse_term()

    def parse_term(self):
        """ <слагаемое>::= <множитель> {<операции_группы_умножения> <множитель>} """
        self.parse_factor()
        while self.current_token in [(2, 10), (2, 11), (2, 12)]: # mult div and
            self.next_token()
            self.parse_factor()

    def parse_factor(self):
        """ <множитель>::= <идентификатор> | <число> | <логическая_константа> | <унарная_операция> <множитель> | « (»<выражение>«)» """
        if self.current_token == (2, 19):  # '('
            self.next_token()
            self.parse_expression()
            if self.current_token == (2, 20):  # ')'
                self.next_token()
            else:
                raise SyntaxError(f"Ожидалась ')' после выражения {self.current_token}")
        elif self.current_token == (2, 13):  # '~'
            self.next_token()
            self.parse_factor()
        elif self.current_token[0] == 3: # идентификатор
            self.parse_identifier()
        elif self.current_token[0] == 4: # число
            self.next_token()
        elif self.current_token in [(1, 15), (1, 16)]:  # Логические константы true | false
            self.next_token()
        else:
            raise SyntaxError(f"Некорректный множитель {self.current_token}")

    def parse_identifier(self):
        """ <идентификатор>::= <буква> {<буква> | <цифра>} """
        if self.current_token[0] == 3 : # идентификатор
            self.next_token()
        else:
            raise SyntaxError(f"Ожидался идентификатор {self.current_token}")

    def parse_conditional(self):
        """ <условный>::= if <выражение> then <оператор> [else <оператор>] end_else """
        if self.current_token == (1, 2):  # if
            self.next_token()
            self.parse_expression()
            if self.current_token == (1, 3):  # then
                self.next_token()
                self.parse_operator()
                if self.current_token == (1, 4):  # else
                    self.next_token()
                    self.parse_operator()
                if self.current_token == (1, 5):  # end_else
                    self.next_token()
                else:
                    raise SyntaxError(f"Ожидался end_else {self.current_token}")
            else:
                raise SyntaxError(f"Ожидался then после выражения {self.current_token}")
        else:
            raise SyntaxError(f"Ожидался if {self.current_token}")

    def parse_fixed_loop(self):
        """ <фиксированного_цикла>::= for «(» [<выражение>] ; [<выражение>] ; [<выражение>] «)» <оператор> """
        if self.current_token == (1, 6):  # for
            self.next_token()
            if self.current_token == (2, 19):  # '('
                self.next_token()
                if self.current_token != (2, 16):  # ';'
                    self.parse_expression()
                if self.current_token == (2, 16):  # ';'
                    self.next_token()
                    if self.current_token != (2, 16):  # ';'
                        self.parse_expression()
                    if self.current_token == (2, 16):  # ';'
                        self.next_token()
                        if self.current_token != (2, 20):  # ')'
                            self.parse_expression()
                        if self.current_token == (2, 20):  # ')'
                            self.next_token()
                            self.parse_operator()
                        else:
                            raise SyntaxError(f"Ожидалась ')' после for {self.current_token}")
                    else:
                        raise SyntaxError(f"Ожидалась ';' {self.current_token}")
                else:
                    raise SyntaxError(f"Ожидалась ';' {self.current_token}")
            else:
                raise SyntaxError(f"Ожидалась '(' после for {self.current_token}")

    def parse_while_loop(self):
        """ <условного_цикла>::= do while <выражение> <оператор> loop """
        if self.current_token == (1, 7):  # do
            self.next_token()
            if self.current_token == (1, 8):  # while
                self.next_token()
                self.parse_expression()
                self.parse_operator()
                if self.current_token == (1, 14):  # loop
                    self.next_token()
                else:
                    raise SyntaxError(f"Ожидался loop {self.current_token}")
            else:
                raise SyntaxError(f"Ожидался while после do {self.current_token}")

    def parse_input(self):
        """ <ввода>::= input «(»<идентификатор> { <идентификатор> } «)» """
        if self.current_token == (1, 9):  # input
            self.next_token()
            if self.current_token == (2, 19):  # '('
                self.next_token()
                self.parse_identifier()  # Парсим первый идентификатор
                while self.current_token is not None and self.current_token != (2, 20):  # Пока не встретили ')'
                    self.parse_identifier()  # Парсим следующие идентификаторы
                if self.current_token == (2, 20):  # ')'
                    self.next_token()
                else:
                    raise SyntaxError(f"Ожидалась ')' после списка идентификаторов {self.current_token}")
            else:
                raise SyntaxError(f"Ожидалась '(' после input {self.current_token}")
        else:
            raise SyntaxError(f"Ожидался input {self.current_token}")

    def parse_output(self):
        """ <вывода>::= output «(»<выражение> { <выражение> } «)» """
        if self.current_token == (1, 10):  # output
            self.next_token()
            if self.current_token == (2, 19):  # '('
                self.next_token()
                self.parse_expression()  # Парсим первое выражение
                while self.current_token is not None and self.current_token != (2, 20):  # Пока не встретили ')'
                    self.parse_expression()  # Парсим следующие выражения
                if self.current_token == (2, 20):  # ')'
                    self.next_token()
                else:
                    raise SyntaxError(f"Ожидалась ')' после списка выражений {self.current_token}")
            else:
                raise SyntaxError(f"Ожидалась '(' после output {self.current_token}")
        else:
            raise SyntaxError(f"Ожидался output {self.current_token}")


# Пример использования
if __name__ == '__main__':
    #lexer = Lexer('output_tokens.txt')  
    parser = Parser('..//output.txt')
    try:
        parser.parse()
        print("Синтаксический анализ завершен успешно.")
    except SyntaxError as e:
        print(f"Ошибка синтаксического анализа: {e}")
