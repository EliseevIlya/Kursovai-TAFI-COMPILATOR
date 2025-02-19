import ast
import time
import globals
from semantic.semanticAnalyzer import SemanticAnalyzer


def run_semantic(file='..//output_parser_dict.txt'):
    try:
        """"
        with open(file, 'r') as out:
        file = out.read()
        parse_tree = ast.literal_eval(file)
        """
        start_time = time.time()
        parse_tree = globals.parse_tree
        analyzer = SemanticAnalyzer(parse_tree)
        analyzer.analyze()
        print("Семантический анализ завершен успешно. Время выполнения ", time.time() - start_time + 0.001)
        print(f"Формирование o файла прошло успешно. Данные записаны в ./program.o")

    except TypeError as e:
        print(f"Ошибка семантического анализа: {e}")
        exit()


if __name__ == "__main__":
    run_semantic()
