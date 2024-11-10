from syntax.node import Node

class SyntaxError(Exception):
    pass

class ParserTree:

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
        #print(self.current_token)

    def parse(self):
        """ <программа>::= «{» {/ (<описание> | <оператор>) ; /} «}» """
        program_node = Node("Program")
        if self.current_token == (2, 14):  # '{'
            self.next_token()
            while self.current_token != (2, 15):  # пока не встретили }
                if self.current_token in [(2, 14), (1, 1), (1, 2), (1, 6), (1, 7), (1, 9), (1, 10)] or \
                        self.current_token[0] == 3:  # { let if for do input output
                    program_node.add_child(self.parse_operator())
                    #self.parse_operator()
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

        global declaration_node

        if flag:
            declaration_node = Node("Declaration")
            node1 = Node("Identifier")
            node1.add_child((Node(str(token))))
            declaration_node.add_child(node1)
        else:
            node1 = Node("Identifier")
            node1.add_child((Node(str(token))))
            declaration_node.add_child(node1)

        while self.current_token == (2, 17):  # ','
            self.next_token()
            # self.parse_identifier()
            declaration_node.add_child(self.parse_identifier())
        if self.current_token == (2, 18):  # ':'
            self.next_token()
            # self.parse_type()
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

        """ <описание>::= { <идентификатор> { , <идентификатор> } : <тип> ; } """
        """"в присваивание (assigment) первый идентификатор уже обработан """
        """"declaration_node = Node("Declaration")
        node1 = Node("Identifier")
        node1.add_child((Node(str(token))))
        declaration_node.add_child(node1)
        while self.current_token == (2, 17):  # ','
            self.next_token()
            #self.parse_identifier()
            declaration_node.add_child(self.parse_identifier())
        if self.current_token == (2, 18):  # ':'
            self.next_token()
            #self.parse_type()
            declaration_node.add_child(self.parse_type())
            if self.current_token == (2, 16): # ;
                self.next_token()
                if self.current_token != (2, 16):
                    dec_token = self.current_token
                    self.next_token()
                    declaration_node.add_child(self.parse_declaration(dec_token))
                    #self.parse_declaration(dec_token)
            else:
                raise SyntaxError(f"Ожидалась ; , но встречено {self.current_token} in declaration")
        else:
            raise SyntaxError(f"Ожидался ':' после идентификаторов {self.current_token}")"""""
        return declaration_node

    def parse_type(self):
        """ <тип>::= % | ! | $ """
        type_node = Node("Type")
        if self.current_token in [(1, 11), (1, 12), (1, 13)]:
            type_node.add_child(Node(str(self.current_token)))
            self.next_token()
        else:
            raise SyntaxError(f"Неверный тип переменной {self.current_token}")
        return type_node

    def parse_operator(self):
        """ <оператор>::= <составной> | <присваивания> | <условный> | <фиксированного_цикла> | <условного_цикла> | <ввода> | <вывода> """
        operator_node = Node("Operator")
        if self.current_token == (2, 14):  # '{' — составной оператор
            #self.parse_compound()
            operator_node.add_child(self.parse_compound())
        elif self.current_token == (1, 1) or self.current_token[0] == 3:  # let или идентификатор
            #self.parse_assignment()
            operator_node.add_child(self.parse_assignment())
        elif self.current_token == (1, 2):  # if
            #self.parse_conditional()
            operator_node.add_child(self.parse_conditional())
        elif self.current_token == (1, 6):  # for
            #self.parse_fixed_loop()
            operator_node.add_child(self.parse_fixed_loop())
        elif self.current_token == (1, 7):  # do
            #self.parse_while_loop()
            operator_node.add_child(self.parse_while_loop())
        elif self.current_token == (1, 9):  # input
            #self.parse_input()
            operator_node.add_child(self.parse_input())
        elif self.current_token == (1, 10):  # output
            #self.parse_output()
            operator_node.add_child(self.parse_output())
        else:
            raise SyntaxError(f"Некорректный оператор {self.current_token}")
        return operator_node

    def parse_compound(self):
        """ <составной>::= «{» <оператор> { ; <оператор> } «}» """
        compound_node = Node("Compound")
        if self.current_token == (2, 14):  # '{'
            self.next_token()
            #self.parse_operator()  # Разбираем первый оператор внутри составного оператора
            compound_node.add_child(self.parse_operator())
            # Цикл для обработки последующих операторов, разделенных символом ';'
            while self.current_token == (2, 16):  # ';'
                self.next_token()
                #self.parse_operator()  # Разбираем следующий оператор
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
        #self.parse_identifier()
        token = self.current_token
        assignment_node.add_child(self.parse_identifier())
        if self.current_token == (2, 21):  # '='
            self.next_token()
            #self.parse_expression()
            ''''node1 = Node("Value")
            node1.add_child((Node(str(self.current_token))))
            assignment_node.add_child(node1)
            self.parse_expression()'''''
            assignment_node.add_child(self.parse_expression())
        elif self.current_token == (2, 17) or self.current_token == (2, 18): # , :
            #self.parse_declaration()
            #assignment_node.add_child(self.parse_declaration())
            return self.parse_declaration(token,True)
        else:
            raise SyntaxError(f"Ожидался '=' после идентификатора {self.current_token}")
        return assignment_node

    def parse_expression(self):
        """ <выражение>::= <операнд>{<операции_группы_отношения><операнд>} """
        expression_node = Node("Expression")
        """"node1 = Node("Identifier")
        node1.add_child(Node(str(self.current_token)))
        expression_node.add_child(node1)
        self.parse_operand()"""""
        expression_node.add_child(self.parse_operand())
        while self.current_token in [(2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6)]:  # NE EQ LT LE GT GE
            expression_node.add_child(Node(str(self.current_token)))
            self.next_token()
            """"node1 = Node("Identifier")
            node1.add_child(Node(str(self.current_token)))
            expression_node.add_child(node1)
            self.parse_operand()"""""
            expression_node.add_child(self.parse_operand())
        return expression_node

    def parse_operand(self):
        """ <операнд>::= <слагаемое>{<операции_группы_сложения><слагаемое>} """
        operand_node = Node("Operand")
        #self.parse_term()
        operand_node.add_child(self.parse_term())
        while self.current_token in [(2, 7), (2, 8), (2, 9)]:  # plus min or
            operand_node.add_child(Node(str(self.current_token)))
            self.next_token()
            #self.parse_term()
            operand_node.add_child(self.parse_term())
        return operand_node

    def parse_term(self):
        """ <слагаемое>::= <множитель> {<операции_группы_умножения> <множитель>} """
        term_node = Node("Term")
        #self.parse_factor()
        term_node.add_child(self.parse_factor())
        while self.current_token in [(2, 10), (2, 11), (2, 12)]:  # mult div and
            term_node.add_child(Node(str(self.current_token)))
            self.next_token()
            #self.parse_factor()
            term_node.add_child(self.parse_factor())
        return term_node

    def parse_factor(self):
        """ <множитель>::= <идентификатор> | <число> | <логическая_константа> | <унарная_операция> <множитель> | « (»<выражение>«)» """
        factor_node = Node("Factor")
        if self.current_token == (2, 19):  # '('
            self.next_token()
            #self.parse_expression()
            factor_node.add_child(self.parse_expression())
            if self.current_token == (2, 20):  # ')'
                self.next_token()
            else:
                raise SyntaxError(f"Ожидалась ')' после выражения {self.current_token}")
        elif self.current_token == (2, 13):  # '~'
            factor_node.add_child(Node(str(self.current_token)))
            self.next_token()
            #self.parse_factor()
            factor_node.add_child(self.parse_factor())
        elif self.current_token[0] == 3:  # идентификатор
            #self.parse_identifier()
            factor_node.add_child(self.parse_identifier())
        elif self.current_token[0] == 4:  # число
            factor_node.add_child(Node(str(self.current_token)))
            self.next_token()
        elif self.current_token in [(1, 15), (1, 16)]:  # Логические константы true | false
            factor_node.add_child(Node(str(self.current_token)))
            self.next_token()
        else:
            raise SyntaxError(f"Некорректный множитель {self.current_token}")
        return factor_node

    def parse_identifier(self):
        """ <идентификатор>::= <буква> {<буква> | <цифра>} """
        identifier_node = Node("Identifier")
        if self.current_token[0] == 3:  # идентификатор
            identifier_node.add_child(Node(str(self.current_token)))
            self.next_token()
        else:
            raise SyntaxError(f"Ожидался идентификатор {self.current_token}")
        return identifier_node

    def parse_conditional(self):
        """ <условный>::= if <выражение> then <оператор> [else <оператор>] end_else """
        conditional_node = Node("Conditional")
        if self.current_token == (1, 2):  # if
            conditional_node.add_child(Node(str(self.current_token)))
            self.next_token()
            #self.parse_expression()
            conditional_node.add_child(self.parse_expression())
            if self.current_token == (1, 3):  # then
                conditional_node.add_child(Node(str(self.current_token)))
                self.next_token()
                #self.parse_operator()
                conditional_node.add_child(self.parse_operator())
                if self.current_token == (1, 4):  # else
                    conditional_node.add_child(Node(str(self.current_token)))
                    self.next_token()
                    #self.parse_operator()
                    conditional_node.add_child(self.parse_operator())
                if self.current_token == (1, 5):  # end_else
                    conditional_node.add_child(Node(str(self.current_token)))
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
            fixed_loop_node.add_child(Node(str(self.current_token)))
            self.next_token()
            if self.current_token == (2, 19):  # '('
                self.next_token()
                if self.current_token != (2, 16):  # ';'
                    #self.parse_expression()
                    fixed_loop_node.add_child(self.parse_expression())
                if self.current_token == (2, 16):  # ';'
                    self.next_token()
                    if self.current_token != (2, 16):  # ';'
                        #self.parse_expression()
                        fixed_loop_node.add_child(self.parse_expression())
                    if self.current_token == (2, 16):  # ';'
                        self.next_token()
                        if self.current_token != (2, 20):  # ')'
                            #self.parse_expression()
                            fixed_loop_node.add_child(self.parse_expression())
                        if self.current_token == (2, 20):  # ')'
                            self.next_token()
                            #self.parse_operator()
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
            while_loop_node.add_child(Node(str(self.current_token)))
            self.next_token()
            if self.current_token == (1, 8):  # while
                while_loop_node.add_child(Node(str(self.current_token)))
                self.next_token()
                #self.parse_expression()
                while_loop_node.add_child(self.parse_expression())
                #self.parse_operator()
                while_loop_node.add_child(self.parse_operator())
                if self.current_token == (1, 14):  # loop
                    while_loop_node.add_child(Node(str(self.current_token)))
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
            input_node.add_child(Node(str(self.current_token)))
            self.next_token()
            if self.current_token == (2, 19):  # '('
                self.next_token()
                #self.parse_identifier()  # Парсим первый идентификатор
                input_node.add_child(self.parse_identifier())
                while self.current_token is not None and self.current_token != (2, 20):  # Пока не встретили ')'
                    #self.parse_identifier()  # Парсим следующие идентификаторы
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
        output_node = Node("Output", value="RRRRR")
        if self.current_token == (1, 10):  # output
            output_node.add_child(Node(str(self.current_token)))
            self.next_token()
            if self.current_token == (2, 19):  # '('
                self.next_token()
                #self.parse_expression()  # Парсим первое выражение
                output_node.add_child(self.parse_expression())
                while self.current_token is not None and self.current_token != (2, 20):  # Пока не встретили ')'
                    #self.parse_expression()  # Парсим следующие выражения
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