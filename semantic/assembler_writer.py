import os

import globals


def write_to_asm(code, filename="./semantic/ASMoutput.asm"):
    # Флаг, указывающий, что первый вызов функции
    if not hasattr(write_to_asm, "has_been_called"):
        write_to_asm.has_been_called = False

    # Определяем режим записи: очищаем файл при первом вызове, добавляем данные при последующих
    mode = 'w' if not write_to_asm.has_been_called else 'a'

    with open(filename, mode) as f:
        f.write(code + "\n")
    write_to_asm.has_been_called = True


def declare_variable(var_name, var_type):
    asm_code = f"    ; Declare {var_name} as {var_type}"
    write_to_asm(asm_code)


def write_variable_addresses(variables, filename, address):
    """
    Записывает переменные с адресами в файл. Увеличивает адрес в зависимости от типа переменной.
    При первом вызове очищает файл, далее добавляет данные.

    :param variables: Список переменных вида [(имя, тип)]
    :param filename: Имя файла для записи
    """
    # Флаг, указывающий, что первый вызов функции
    if not hasattr(write_variable_addresses, "has_been_called"):
        write_variable_addresses.has_been_called = False

    # Определяем режим записи: очищаем файл при первом вызове, добавляем данные при последующих
    mode = 'w' if not write_variable_addresses.has_been_called else 'a'

    # Открываем файл в нужном режиме
    with open(filename, mode) as f:
        for var_name, var_type in variables:
            # Проверяем тип и определяем размер
            if var_type == '$':  # boolean
                size = 1
            else:  # int или float
                size = 4

            # Записываем переменную в файл
            f.write(f"{globals.reversed_identifiers[var_name]}: {hex(address)}\n")
            globals.identifiers_address[var_name] = hex(address)

            # Увеличиваем адрес на размер переменной
            address += size

        # Устанавливаем флаг, что файл уже был записан
        write_variable_addresses.has_been_called = True
    return address


def assign_variable():
    operations = {
        1:handle_notEqual(),
        2:handle_equal(),
        3:handle_lessThan(),
        4:handle_lessEqual(),
        5:handle_greaterThan(),
        6:handle_greaterEqual(),
        7:handle_plus(),
        8:handle_minus(),
        9:handle_or(),
        10:handle_mult(),
        11:handle_div(),
        12:handle_and(),
        13:handle_not()
    }



def output_variable(var_name):
    asm_code = f"    ; Output {var_name}"
    write_to_asm(asm_code)
    write_to_asm(f"    call output  ; Output value of {var_name}")


def input_variable(var_name, var_type):
    print('input_variable')
    asm_code = f"   MOV RDI, input_prompt"
    write_to_asm(asm_code)
    type_choose = {
        "int": "read_int",
        "float": "read_float",
        "boolean": "read_boolean"
    }
    asm_code = f"   CALL {type_choose[var_type]}"
    write_to_asm(asm_code)


def generate_condition(condition):
    asm_code = f"    ; Evaluate condition: {condition}"
    write_to_asm(asm_code)
    write_to_asm(f"    cmp eax, 0  ; Compare with 0")
    write_to_asm(f"    je condition_end  ; Jump if condition is false")


def loop_start(loop_type):
    if loop_type == 'while':
        write_to_asm("    ; Start while loop")
        write_to_asm("    loop_start:")
    elif loop_type == 'for':
        write_to_asm("    ; Start for loop")
        write_to_asm("    for_start:")


def loop_end(loop_type):
    if loop_type == 'while':
        write_to_asm("    ; End while loop")
        write_to_asm("    jmp loop_start  ; Continue while loop")
        write_to_asm("    condition_end:")
    elif loop_type == 'for':
        write_to_asm("    ; End for loop")
        write_to_asm("    jmp for_start  ; Continue for loop")
