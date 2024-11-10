import globals
from syntax.node import Node


class ParserTree:
    #TODO оптимизации + возможно как-то передавать номера строк и номера позиций или
    # как-то продумать чтобы легче определять позицию ошибок

    def __init__(self, token_file):
        self.token_file = open(token_file, 'r')
        self.current_token = None
        self.previous_token = None  # Для хранения предыдущей лексемы
        self.next_token()
        #TODO добавить таблицы необходимых ключ слов и разделителей и заменить токены на прямые их значения
        # также сделать этот файл осноным
        self.keywords = {"%": 11, "!": 12, "$": 13}

    #TODO сделать передачу по буферу или считывание всего файла сразу, а не по символам
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

    def parse(self):
        """ <программа>::= «{» {/ (<описание> | <оператор>) ; /} «}» """
        program_node = Node("Program")
        if self.current_token == (2, 14):  # '{'
            self.next_token()
            while self.current_token != (2, 15):  # пока не встретили }
                if self.current_token in [(2, 14), (1, 1), (1, 2), (1, 6), (1, 7), (1, 9), (1, 10)] or \
                        self.current_token[0] == 3:  # { let if for do input output
                    program_node.add_child(self.parse_operator())
                if self.current_token == (2, 16):  # ';'
                    self.next_token()
                else:
                    raise SyntaxError(f"Ожидалась ; , но встречено {self.current_token} in program")

            # Проверяем конец программы на сочетание ;}
            if self.current_token == (2, 15):
                if self.previous_token != (2, 16):
                    raise SyntaxError("Ожидалась ;")
                self.next_token()  # Пропускаем '}'
                self.check_end_of_program()  # Проверяем, есть ли лексемы после окончания программы
            else:
                raise SyntaxError("Программа должна завершаться  '}'")
        else:
            raise SyntaxError("Программа должна начинаться с '{'")
        return program_node

    def check_end_of_program(self):
        """ Проверка на наличие лексем после завершения программы """
        if self.current_token is not None:
            raise SyntaxError(f"Лексемы после конца программы: {self.current_token}")

    def parse_declaration(self, token, flag):
        """ <описание>::= { <идентификатор> { , <идентификатор> } : <тип> ; } """
        """"в присваивание (assigment) первый идентификатор уже обработан """

        global declaration_node

        if flag:
            declaration_node = Node("Declaration")
            node1 = Node("Identifier")
            node1.value = token
            declaration_node.add_child(node1)
        else:
            node1 = Node("Identifier")
            node1.value = token
            declaration_node.add_child(node1)

        identifier_list = [token]
        while self.current_token == (2, 17):  # ','
            self.next_token()
            identifier_list.append(self.current_token)
            declaration_node.add_child(self.parse_identifier())
        if self.current_token == (2, 18):  # ':'
            self.next_token()
            for lex in identifier_list:
                if self.current_token == (1, 11):
                    globals.identifier_type[lex[1]] = "int"
                elif self.current_token == (1, 12):
                    globals.identifier_type[lex[1]] = "float"
                elif self.current_token == (1, 13):
                    globals.identifier_type[lex[1]] = "boolean"
            declaration_node.add_child(self.parse_type())
            if self.current_token == (2, 16):  # ;
                self.next_token()
                if self.current_token != (2, 16):
                    dec_token = self.current_token
                    self.next_token()
                    self.parse_declaration(dec_token, False)
            else:
                raise SyntaxError(f"Ожидалась ; , но встречено {self.current_token} in declaration")
        else:
            raise SyntaxError(f"Ожидался ':' после идентификаторов {self.current_token}")
        return declaration_node

    def parse_type(self):
        """ <тип>::= % | ! | $ """
        keywords =self.keywords
        type_node = Node("Type")
        if self.current_token in [(1, 11), (1, 12), (1, 13)]:
            type_node.value = list(keywords.keys())[list(keywords.values()).index(self.current_token[1])]
            self.next_token()
        else:
            raise SyntaxError(f"Неверный тип переменной {self.current_token}")
        return type_node

    def parse_operator(self):
        """ <оператор>::= <составной> | <присваивания> | <условный> | <фиксированного_цикла> | <условного_цикла> | <ввода> | <вывода> """
        operator_node = Node("Operator")
        if self.current_token == (2, 14):  # '{' — составной оператор
            operator_node.add_child(self.parse_compound())
        elif self.current_token == (1, 1) or self.current_token[0] == 3:  # let или идентификатор
            operator_node.add_child(self.parse_assignment())
        elif self.current_token == (1, 2):  # if
            operator_node.add_child(self.parse_conditional())
        elif self.current_token == (1, 6):  # for
            operator_node.add_child(self.parse_fixed_loop())
        elif self.current_token == (1, 7):  # do
            operator_node.add_child(self.parse_while_loop())
        elif self.current_token == (1, 9):  # input
            operator_node.add_child(self.parse_input())
        elif self.current_token == (1, 10):  # output
            operator_node.add_child(self.parse_output())
        else:
            raise SyntaxError(f"Некорректный оператор {self.current_token}")
        return operator_node

    def parse_compound(self):
        """ <составной>::= «{» <оператор> { ; <оператор> } «}» """
        compound_node = Node("Compound")
        if self.current_token == (2, 14):  # '{'
            self.next_token()
            # Разбираем первый оператор внутри составного оператора
            compound_node.add_child(self.parse_operator())
            # Цикл для обработки последующих операторов, разделенных символом ';'
            while self.current_token == (2, 16):  # ';'
                self.next_token()
                # Разбираем следующий оператор
                compound_node.add_child(self.parse_operator())
            if self.current_token == (2, 15):  # '}'
                self.next_token()  # Закрываем составной оператор
            else:
                raise SyntaxError(f"Ожидалась '}}' для закрытия составного оператора, получено {self.current_token}")
        else:
            raise SyntaxError(f"Ожидалась '{{' для начала составного оператора, получено {self.current_token}")
        return compound_node

    def parse_assignment(self):
        """ <присваивания> ::= [ let ] <идентификатор> = <выражение> """
        assignment_node = Node("Assignment")
        if self.current_token == (1, 1):  # let
            self.next_token()
        token = self.current_token
        assignment_node.add_child(self.parse_identifier())
        if self.current_token == (2, 21):  # '='
            self.next_token()
            assignment_node.add_child(self.parse_expression())
        elif self.current_token == (2, 17) or self.current_token == (2, 18):  # , :
            return self.parse_declaration(token, True)
        else:
            raise SyntaxError(f"Ожидался '=' после идентификатора {self.current_token}")
        return assignment_node

    def parse_expression(self):
        """ <выражение>::= <операнд> {<операции_группы_отношения> <операнд>} """
        expression_node = Node("Expression")
        expression_node.add_child(self.parse_operand())
        while self.current_token in [(2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6)]:  # NE EQ LT LE GT GE
            operation_node = Node("RelationalOperation", value=self.current_token)
            self.next_token()
            operation_node.add_child(expression_node)
            operation_node.add_child(self.parse_operand())
            expression_node = operation_node  # Обновляем вершину дерева
        return expression_node

    def parse_operand(self):
        """ <операнд>::= <слагаемое> {<операции_группы_сложения> <слагаемое>} """
        operand_node = Node("Operand")
        operand_node.add_child(self.parse_term())
        while self.current_token in [(2, 7), (2, 8), (2, 9)]:  # plus min or
            operation_node = Node("AdditiveOperation", value=self.current_token)
            self.next_token()
            operation_node.add_child(operand_node)
            operation_node.add_child(self.parse_term())
            operand_node = operation_node  # Обновляем вершину дерева
        return operand_node

    def parse_term(self):
        """ <слагаемое>::= <множитель> {<операции_группы_умножения> <множитель>} """
        term_node = Node("Term")
        term_node.add_child(self.parse_factor())
        while self.current_token in [(2, 10), (2, 11), (2, 12)]:  # mult div and
            operation_node = Node("MultiplicativeOperation", value=self.current_token)
            self.next_token()
            operation_node.add_child(term_node)
            operation_node.add_child(self.parse_factor())
            term_node = operation_node  # Обновляем вершину дерева
        return term_node

    def parse_factor(self):
        """ <множитель>::= <идентификатор> | <число> | <логическая_константа> | <унарная_операция> <множитель> | « (»<выражение>«)» """
        factor_node = Node("Factor")
        if self.current_token == (2, 19):  # '('
            self.next_token()
            factor_node.add_child(self.parse_expression())
            if self.current_token == (2, 20):  # ')'
                self.next_token()
            else:
                raise SyntaxError(f"Ожидалась ')' после выражения {self.current_token}")
        elif self.current_token == (2, 13):  # '~'
            factor_node.value = self.current_token
            self.next_token()
            factor_node.add_child(self.parse_factor())
        elif self.current_token[0] == 3:  # идентификатор
            factor_node.add_child(self.parse_identifier())

        elif self.current_token[0] == 4:  # число

            number_type = globals.numbers_type[self.current_token[1]]
            factor_node.add_child(Node(str(number_type), value=self.current_token))
            self.next_token()
        elif self.current_token in [(1, 15), (1, 16)]:  # Логические константы true | false
            factor_node.add_child(Node(str("boolean"), value=self.current_token))
            self.next_token()
        else:
            raise SyntaxError(f"Некорректный множитель {self.current_token}")
        return factor_node

    def parse_identifier(self):
        """ <идентификатор>::= <буква> {<буква> | <цифра>} """
        identifier_node = Node("Identifier")
        if self.current_token[0] == 3:  # идентификатор
            identifier_node.value = self.current_token
            self.next_token()
        else:
            raise SyntaxError(f"Ожидался идентификатор {self.current_token}")
        return identifier_node

    def parse_conditional(self):
        """ <условный>::= if <выражение> then <оператор> [else <оператор>] end_else """
        conditional_node = Node("Conditional")
        if self.current_token == (1, 2):  # if
            self.next_token()
            conditional_node.add_child(self.parse_expression())
            if self.current_token == (1, 3):  # then
                self.next_token()
                conditional_node.add_child(self.parse_operator())
                if self.current_token == (1, 4):  # else
                    self.next_token()
                    conditional_node.add_child(self.parse_operator())
                if self.current_token == (1, 5):  # end_else
                    self.next_token()
                else:
                    raise SyntaxError(f"Ожидался end_else {self.current_token}")
            else:
                raise SyntaxError(f"Ожидался then после выражения {self.current_token}")
        else:
            raise SyntaxError(f"Ожидался if {self.current_token}")
        return conditional_node

    def parse_fixed_loop(self):
        """ <фиксированного_цикла>::= for «(» [<выражение>] ; [<выражение>] ; [<выражение>] «)» <оператор> """
        fixed_loop_node = Node("Fixed_loop")
        if self.current_token == (1, 6):  # for
            self.next_token()
            if self.current_token == (2, 19):  # '('
                self.next_token()
                if self.current_token != (2, 16):  # ';'
                    fixed_loop_node.add_child(self.parse_expression())
                if self.current_token == (2, 16):  # ';'
                    self.next_token()
                    if self.current_token != (2, 16):  # ';'
                        fixed_loop_node.add_child(self.parse_expression())
                    if self.current_token == (2, 16):  # ';'
                        self.next_token()
                        if self.current_token != (2, 20):  # ')'
                            fixed_loop_node.add_child(self.parse_expression())
                        if self.current_token == (2, 20):  # ')'
                            self.next_token()
                            fixed_loop_node.add_child(self.parse_operator())
                        else:
                            raise SyntaxError(f"Ожидалась ')' после for {self.current_token}")
                    else:
                        raise SyntaxError(f"Ожидалась ';' {self.current_token}")
                else:
                    raise SyntaxError(f"Ожидалась ';' {self.current_token}")
            else:
                raise SyntaxError(f"Ожидалась '(' после for {self.current_token}")
            return fixed_loop_node

    def parse_while_loop(self):
        """ <условного_цикла>::= do while <выражение> <оператор> loop """
        while_loop_node = Node("While_loop")
        if self.current_token == (1, 7):  # do
            self.next_token()
            if self.current_token == (1, 8):  # while
                self.next_token()
                while_loop_node.add_child(self.parse_expression())
                while_loop_node.add_child(self.parse_operator())
                if self.current_token == (1, 14):  # loop
                    self.next_token()
                else:
                    raise SyntaxError(f"Ожидался loop {self.current_token}")
            else:
                raise SyntaxError(f"Ожидался while после do {self.current_token}")
            return while_loop_node

    def parse_input(self):
        """ <ввода>::= input «(»<идентификатор> { <идентификатор> } «)» """
        input_node = Node("Input")
        if self.current_token == (1, 9):  # input
            self.next_token()
            if self.current_token == (2, 19):  # '('
                self.next_token()
                # Парсим первый идентификатор
                input_node.add_child(self.parse_identifier())
                while self.current_token is not None and self.current_token != (2, 20):  # Пока не встретили ')'
                    # Парсим следующие идентификаторы
                    input_node.add_child(self.parse_identifier())
                if self.current_token == (2, 20):  # ')'
                    self.next_token()
                else:
                    raise SyntaxError(f"Ожидалась ')' после списка идентификаторов {self.current_token}")
            else:
                raise SyntaxError(f"Ожидалась '(' после input {self.current_token}")
        else:
            raise SyntaxError(f"Ожидался input {self.current_token}")
        return input_node

    def parse_output(self):
        """ <вывода>::= output «(»<выражение> { <выражение> } «)» """
        output_node = Node("Output")
        if self.current_token == (1, 10):  # output
            self.next_token()
            if self.current_token == (2, 19):  # '('
                self.next_token()
                # Парсим первое выражение
                output_node.add_child(self.parse_expression())
                while self.current_token is not None and self.current_token != (2, 20):  # Пока не встретили ')'
                    # Парсим следующие выражения
                    output_node.add_child(self.parse_expression())
                if self.current_token == (2, 20):  # ')'
                    self.next_token()
                else:
                    raise SyntaxError(f"Ожидалась ')' после списка выражений {self.current_token}")
            else:
                raise SyntaxError(f"Ожидалась '(' после output {self.current_token}")
        else:
            raise SyntaxError(f"Ожидался output {self.current_token}")
        return output_node


if __name__ == "__main__":
    input_file = '..//output.txt'
    parser = ParserTree(input_file)
    root_node = parser.parse()  # Вернём корневой узел
    print("Синтаксический анализ завершен успешно.")
    print("Дерево узлов:")
    print(root_node.print_tree())  # Печатаем дерево узлов
    print(root_node.to_dict())
    print(globals.identifier_type)
