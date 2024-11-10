class Node:
    def __init__(self, node_type, value=None):
        """
        Инициализирует узел с заданным типом и значением.
        :param node_type: Тип узла (например, "Program", "Assignment", "Expression").
        :param value: Опциональное значение узла (например, лексема).
        """
        self.node_type = node_type
        self.value = value
        self.children = []

    def add_child(self, child_node):
        """
        Добавляет дочерний узел к текущему узлу.
        :param child_node: Узел, который будет добавлен в качестве дочернего.
        """
        if child_node is not None:
            self.children.append(child_node)

    def print_tree(self, indent=0):
        """
        Рекурсивно выводит дерево узлов на экран.
        :param indent: Количество отступов для отображения иерархии.
        """
        prefix = ' ' * indent
        if self.value:
            print(f"{prefix}{self.node_type}: {self.value}")
        else:
            print(f"{prefix}{self.node_type}")
        for child in self.children:
            child.print_tree(indent + 2)

    def get_tree_as_string(self, indent=0):
        """
        Рекурсивно создает строковое представление дерева узлов.
        :param indent: Количество отступов для отображения иерархии.
        :return: Строка, представляющая дерево узлов.
        """
        prefix = ' ' * indent
        result = ""
        if self.value:
            result += f"{prefix}{self.node_type}: {self.value}\n"
        else:
            result += f"{prefix}{self.node_type}\n"
        for child in self.children:
            result += child.get_tree_as_string(indent + 2)
        return result

    def to_dict(self):
        """
        Преобразует дерево узлов в словарь для дальнейшего использования.
        :return: Словарь, представляющий текущее дерево узлов.
        """
        node_representation = {
            "type": self.node_type,
            "value": self.value,
            "children": [child.to_dict() for child in self.children] if self.children else None
        }
        return node_representation
