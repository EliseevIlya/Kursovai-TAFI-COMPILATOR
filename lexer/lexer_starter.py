import globals
import time

from lexer.lexeme import Lexer


def run_lexer(input_file='..//input.txt', output_file='..//output.txt'):
    start_time = time.time()
    lexer = Lexer()
    lexer.tokenize(input_file, output_file)
    #print(globals.numbers_type)
    print("Лексический анализ завершен успешно. Время выполнения ",time.time() - start_time)
    #print("time", time.time() - start_time)

if __name__ == "__main__":
    run_lexer()
'''
keywords - 1
delimiters -2
identifiers -3
numbers -4
'''
