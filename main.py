import ast
import time

from lexer.lexer_starter import run_lexer
from semantic.semantic_starter import run_semantic
from syntax.syntax_starter import run_parser

if __name__ == "__main__":
    # TODO добавить меню выбора действий или через аргументы + help
    #TODO добавить что если в прошлом анализаторе ошибка то следующий не выполнять
    start_time = time.time()
    # Запуск лексера
    run_lexer("testProgram1.txt","output.txt")
    # Запуск синтаксического анализатора
    run_parser("output.txt","output_parser.txt") \
    # Запуск семантического анализатора
    run_semantic()
    print("Анализ завершен успешно. Время выполнения ", time.time() - start_time)

'''
keywords - 1
delimiters -2
identifiers -3
numbers -4
'''
