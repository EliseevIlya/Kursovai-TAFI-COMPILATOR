import globals
from llvmlite import ir, binding


class SemanticAnalyzer:
    def __init__(self, parse_tree):
        self.parse_tree = parse_tree
        self.variable_types = globals.identifier_type
        self.variable_init = set()
        self.declaration_identifier = set()

        #TODO генерация obj через llvm: input,output,declaration - +
        #TODO генерация obj через llvm: if, for , while,compare,assigment, operation
        # Шаг 1: Создание модуля и типов
        self.module = ir.Module(name="program")
        self.module.triple = binding.get_default_triple()
        self.int_type = ir.IntType(32)
        self.float_type = ir.FloatType()
        self.void_type = ir.VoidType()
        self.bool_type = ir.IntType(1)
        self.printf, self.scanf = self.create_c_io_functions(self.module)
        self.builder = None
        self.variable_obj_file = {}

    def create_global_string(self,module, name, value):
        # Если строка уже существует, возвращаем её
        if name in self.variable_obj_file:
            return self.variable_obj_file[name]

        # Добавляем нулевой байт, необходимый для C-строк
        string_value = bytearray(value.encode("utf-8")) + b'\0'
        string_type = ir.ArrayType(ir.IntType(8), len(string_value))

        # Создаём глобальную переменную для строки
        global_var = ir.GlobalVariable(module, string_type, name=name)
        global_var.global_constant = True
        global_var.initializer = ir.Constant(string_type, string_value)

        # Кэшируем созданную переменную
        self.variable_obj_file[name] = global_var
        return global_var

    def create_c_io_functions(self, module):
        # Объявляем printf
        printf_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
        printf = ir.Function(module, printf_ty, name="printf")

        # Объявляем scanf
        scanf_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
        scanf = ir.Function(module, scanf_ty, name="scanf")

        return printf, scanf

    # Функция для вызова scanf

    def scan_value(self, builder, value_ptr, is_float=False):
        fmt = "%f\0" if is_float else "%d\0"
        fmt_global = self.create_global_string(self.module, "scanf_fmt", fmt)  # Создаём строку
        fmt_ptr = builder.bitcast(fmt_global, ir.PointerType(ir.IntType(8)))  # Приводим к указателю char*

        # Вызываем scanf с указателем на строку формата и указателем на переменную
        builder.call(self.scanf, [fmt_ptr, value_ptr])


    # Функция для вывода значения
    def print_value(self, builder, value, is_float=False):
        fmt = "%.2f\n\0" if is_float else "%d\n\0"
        fmt_global = self.create_global_string(self.module, "printf_fmt", fmt)  # Создаём строку
        fmt_ptr = builder.bitcast(fmt_global, ir.PointerType(ir.IntType(8)))  # Приводим к указателю char*

        # Вызываем printf с указателем на строку формата и значением
        builder.call(self.printf, [fmt_ptr, value])

    def analyze(self):
        # Шаг 2: Создание функции main
        self.func_type = ir.FunctionType(self.void_type, [])
        self.main_func = ir.Function(self.module, self.func_type, name="main")
        self.block = self.main_func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(self.block)

        # Построение дерева
        self.visit(self.parse_tree)

        # Завершаем main
        self.builder.ret_void()

        # Инициализация LLVM
        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()

        # Получение целевой машины
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine()

        # Компиляция модуля
        compiled_module = binding.parse_assembly(str(self.module))
        compiled_module.verify()

        # Генерация объектного файла
        with open("program.o", "wb") as obj_file:
            obj_file.write(target_machine.emit_object(compiled_module))

        # Генерация файла с ассемблерным кодом
        with open("program.asm", "w") as asm_file:
            asm_file.write(target_machine.emit_assembly(compiled_module))

    def visit(self, node):
        node_type = node['type']
        handlers = {
            'Program': lambda n: [self.visit(child) for child in n['children']],
            'Declaration': self.handle_declaration,
            'Assignment': self.handle_assignment,
            'Operator': self.handle_operator,
            'Compound': self.handle_compound,
            'Input': self.handle_input,
            'Output': self.handle_output,
            'Conditional': self.handle_control_structure,
            'Fixed_loop': self.handle_control_structure,
            'While_loop': self.handle_control_structure
        }
        if node_type in handlers:
            print(node_type)
            handlers[node_type](node)

    def handle_operator(self, node):
        for child in node['children']:
            self.visit(child)

    def handle_declaration(self, node):
        global var_alloca
        for child in node['children']:
            if child['type'] == 'Identifier':
                if child['value'] not in self.declaration_identifier:
                    self.declaration_identifier.add(child['value'])
                    var_type = self.variable_types[child['value'][1]]
                    var_name = globals.reversed_identifiers[child['value'][1]]
                    if var_type == "int":
                        var_alloca = self.builder.alloca(self.int_type, name=var_name)
                    elif var_type == "float":
                        var_alloca = self.builder.alloca(self.float_type, name=var_name)
                    elif var_type == "boolean":
                        var_alloca = self.builder.alloca(self.bool_type, name=var_name)
                    self.variable_obj_file[var_name] = var_alloca
                else:
                    #print(self.declaration_identifier)
                    raise TypeError(
                        f"Нельзя повторно объявить переменную {globals.reversed_identifiers[child['value'][1]]}")

    def handle_compound(self, node):
        for child in node['children']:
            self.visit(child)

    def handle_assignment(self, node):
        """"
        if len(node['children']) != 2:
            raise ValueError("Некорректная структура Assignment")
        """

        left, right = node['children']

        self.check_type_consistency(left, right)

    def check_type_consistency(self, left, right):
        right_type = self.evaluate_expression(right)
        _, var_id = left['value']
        self.variable_init.add(var_id)
        left_type = self.get_type(left)

        if left_type != right_type:
            raise TypeError(f"Несоответствие типов: слева '{left_type}', справа '{right_type}'")

    def get_type(self, node):
        if node['type'] == 'Identifier':
            _, var_id = node['value']
            return self.check_variable_init(var_id)
        type_map = {'int': 'int', 'float': 'float', 'boolean': 'boolean'}
        return type_map.get(node['type'], None)

    def check_variable_init(self, var_id):
        if var_id not in self.variable_init:
            raise TypeError(f"Переменная не инициализирована {globals.reversed_identifiers[var_id]}")
        return self.variable_types.get(var_id)

    def evaluate_expression(self, node):
        if node['type'] == 'Expression':
            return self.evaluate_expression(node['children'][0])
        elif node['type'] in ['AdditiveOperation', 'MultiplicativeOperation', 'RelationalOperation']:
            return self.evaluate_operation(node)
        elif node['type'] in ['Operand', 'Term', 'Factor']:
            return self.evaluate_expression(node['children'][0])
        else:
            return self.get_type(node)

    def evaluate_operation(self, node):
        operand_type = self.evaluate_expression(node['children'][0])
        for child in node['children'][1:]:
            child_type = self.evaluate_expression(child)
            if node['type'] == 'MultiplicativeOperation' and node['value'] == (2, 11):
                return 'float'
            if child_type != operand_type:
                raise TypeError(f"Несоответствие типов в операции {node['type']}: '{operand_type}' и '{child_type}'")
        return 'boolean' if node['type'] == 'RelationalOperation' else operand_type

    def handle_control_structure(self, node):
        for child in node['children']:
            if child['type'] == 'RelationalOperation':
                self.evaluate_expression(child)
            elif child['type'] == 'Expression':
                self.ensure_boolean_expression(child)
            elif child['type'] == 'Operator':
                self.handle_operator(child)

    def ensure_boolean_expression(self, node):
        if self.evaluate_expression(node) != 'boolean':
            raise TypeError("Условие должно быть boolean.")

    def get_factors_children(self, node, factors_children):
        if node['type'] == 'Factor':
            if node.get('value') is not None:
                factors_children.append(node['value'])
            for child in node.get('children', []):
                self.get_factors_children(child, factors_children)
        else:
            for child in node.get('children', []):
                self.get_factors_children(child, factors_children)
        return factors_children

    """"
    
    def handle_output(self, node):
        self.evaluate_expression(node['children'][0])
    
    """

    def evaluate_expression_llvm(self, node):
        global value, is_float, result
        node_type = node['type']

        # Если это идентификатор, загружаем его значение
        if node_type == 'Identifier':
            var_name = globals.reversed_identifiers[node['value'][1]]
            value = self.builder.load(self.variable_obj_file[var_name])
            var_type = self.variable_types[node['value'][1]]
            is_float = var_type == 'float'
            return value, is_float

        # Если это число, возвращаем его значение
        elif node_type in ['int', 'float']:
            if node_type == 'int':
                value = ir.Constant(self.int_type, int(node['value']))
                is_float = False
            elif node_type == 'float':
                value = ir.Constant(self.float_type, float(node['value']))
                is_float = True
            return value, is_float

        # Если это операция (Additive, Multiplicative), обрабатываем её
        elif node_type in ['AdditiveOperation', 'MultiplicativeOperation']:
            # Получаем левый и правый операнды
            left, right = node['children']
            left_value, left_is_float = self.evaluate_expression_llvm(left)
            right_value, right_is_float = self.evaluate_expression_llvm(right)

            # Если один из операндов float, оба операнда приводим к float
            if left_is_float or right_is_float:
                left_value = self.builder.uitofp(left_value, self.float_type) if not left_is_float else left_value
                right_value = self.builder.uitofp(right_value, self.float_type) if not right_is_float else right_value
                is_float = True
            else:
                is_float = False
            # Выбираем операцию
            if node['value'] == (2,7):
                result = self.builder.fadd(left_value, right_value) if is_float else self.builder.add(left_value,
                                                                                                      right_value)
            elif node['value'] == (2,8):
                result = self.builder.fsub(left_value, right_value) if is_float else self.builder.sub(left_value,
                                                                                                      right_value)
            elif node['value'] == (2,10):
                result = self.builder.fmul(left_value, right_value) if is_float else self.builder.mul(left_value,
                                                                                                      right_value)
            elif node['value'] == (2,11):
                result = self.builder.fdiv(left_value, right_value) if is_float else self.builder.sdiv(left_value,
                                                                                                       right_value)
            else:
                pass
                #raise ValueError(f"Неизвестная операция: {node['value']}")

            return result, is_float

        # Рекурсивно обрабатываем вложенные узлы (например, Expression → Operand → Term → Factor)
        elif node_type in ['Expression', 'Operand', 'Term', 'Factor']:
            return self.evaluate_expression_llvm(node['children'][0])

        # Если тип узла не распознан
        else:
            raise ValueError(f"Неизвестный тип узла: {node_type}")

    def handle_output(self, node):
        # Извлекаем Expression из детей узла Output
        expression = node['children'][0]
        # Вычисляем значение выражения (рекурсивно обрабатывая узлы)
        value, is_float = self.evaluate_expression_llvm(expression)
        # Печатаем значение
        self.print_value(self.builder, value, is_float=is_float)

    def handle_input(self, node):
        for child in node['children']:
            _, var_id = child['value']
            if self.variable_types.get(var_id, None) is None:
                raise TypeError(f"Неизвестная переменная {globals.reversed_identifiers[child['value'][1]]}")
            self.variable_init.add(var_id)

            var_type = self.variable_types[var_id]
            var_name = globals.reversed_identifiers[child['value'][1]]
            if var_type == "int":
                self.scan_value(self.builder, self.variable_obj_file[var_name])
            elif var_type == "float":
                self.scan_value(self.builder, self.variable_obj_file[var_name], is_float=True)
            elif var_type == "boolean":
                temp_bool = self.builder.alloca(self.int_type, name=f"{var_name}_temp")  # Временный int для boolean
                self.scan_value(self.builder, temp_bool)
                bool_value = self.builder.trunc(self.builder.load(temp_bool), self.bool_type, name=f"{var_name}_bool")
                self.builder.store(bool_value, self.variable_obj_file[var_name])


