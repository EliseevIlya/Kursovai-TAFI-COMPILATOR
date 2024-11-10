import globals
from semantic import assembler_writer


class SemanticAnalyzer:
    def __init__(self, parse_tree):
        self.parse_tree = parse_tree
        self.variable_types = globals.identifier_type
        self.variable_init = set()
        self.declaration_identifier = set()
        self.address = 0x1000

    def analyze(self):
        self.visit(self.parse_tree)

    def visit(self, node):
        node_type = node['type']
        print(node_type)
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
            handlers[node_type](node)

    def handle_operator(self, node):
        for child in node['children']:
            self.visit(child)

    def handle_declaration(self, node):
        indet = []
        send = []
        for child in node['children']:
            if child['type'] == 'Identifier' and child['value'] not in self.declaration_identifier:
                indet.append(child['value'])
                self.declaration_identifier.add(child['value'])
            elif child['type'] == 'Type':
                var_type = child['value'][0]
                for var_name in indet:
                    put = (var_name[1],var_type)
                    send.append(put)
                indet = []
            else:
                raise TypeError(f"Нельзя повторно объявить переменную {child['value']}")
        self.address =  assembler_writer.write_variable_addresses(send, './semantic/DataObj.txt', self.address)

    def handle_compound(self, node):
        for child in node['children']:
            self.visit(child)
    def handle_assignment(self, node):
        if len(node['children']) != 2:
            raise ValueError("Некорректная структура Assignment")

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
            raise TypeError(f"Переменная не инициализирована {var_id}")
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
            raise TypeError("Ошибка: условие должно быть булевым.")

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

    def handle_output(self, node):
        self.evaluate_expression(node['children'][0])


    def handle_input(self, node):
        for child in node['children']:
            var_name = child['value'][1]
            if self.variable_types.get(var_name, None) is None:
                raise TypeError(f"Неизвестная переменная {child['value']}")
            self.variable_init.add(var_name)
            print(var_name, self.variable_types[var_name], type(self.variable_types[var_name]))
            assembler_writer.input_variable(var_name,self.variable_types[var_name])
