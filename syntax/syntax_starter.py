import time

import globals
from syntax.parserTree import ParserTree


def run_parser(input_file='..//output.txt', parser_file_out='..//output_parser.txt'):
    try:
        start_time = time.time()
        parser = ParserTree(input_file)
        root_node = parser.parse()  # Вернём корневой узел
        print("Синтаксический анализ завершен успешно. Время выполнения ", time.time() - start_time + 0.0001)
        #print("Дерево узлов:")
        print(root_node.print_tree())  # Печатаем дерево узлов
        #print(globals.identifier_type)
        globals.parse_tree = root_node.to_dict()
        with open(parser_file_out, 'w') as outfile:
            outfile.write(root_node.get_tree_as_string())
        with open('.//output_parser_dict.txt', 'w') as outfile:
            outfile.write(str(globals.parse_tree))
    except SyntaxError as e:
        # print(root_node.print_tree())
        print(f"Ошибка синтаксического анализа: {e}")
        exit()


if __name__ == "__main__":
    run_parser()
