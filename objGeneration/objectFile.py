import struct
import io

class ELF64ObjectFile:
    def __init__(self):
        # Инициализация пустых секций
        self.text_section = b''  # Секция кода (пока пустая)
        self.data_section = b''  # Секция данных (инициализированные данные, пока пустая)
        self.bss_section = b''   # Секция BSS (неинициализированные данные)

    def create_elf_header(self):
        # ELF заголовок для x86_64 в формате ELF64
        e_ident = b'\x7fELF'        # Магическая строка ELF
        e_ident += b'\x02'          # 64-битный ELF
        e_ident += b'\x01'          # Little-endian
        e_ident += b'\x01'          # ELF версии
        e_ident += b'\x00' * 9      # Оставшиеся байты e_ident, зарезервированные

        e_type = 1                  # ET_REL (релятивный объектный файл)
        e_machine = 0x3E            # EM_X86_64 для архитектуры x86-64
        e_version = 1               # ELF текущая версия
        e_entry = 0                 # Начальная точка (для объектов не требуется)
        e_phoff = 0                 # Нет таблицы программ (релятивный файл)
        e_shoff = 0x40              # Смещение до таблицы секций (за заголовком ELF)
        e_flags = 0                 # Флаги (не требуются)
        e_ehsize = 0x40             # Размер ELF заголовка
        e_phentsize = 0             # Размер записи программы (отсутствует)
        e_phnum = 0                 # Число записей программы (отсутствует)
        e_shentsize = 0x40          # Размер записи секции
        e_shnum = 4                 # Число секций (NULL, .text, .data, .bss)
        e_shstrndx = 3              # Индекс секции с именами секций

        # Упаковка заголовка ELF в бинарный формат
        elf_header = struct.pack(
            '<16sHHIQQQIHHHHHH',
            e_ident, e_type, e_machine, e_version, e_entry,
            e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize,
            e_phnum, e_shentsize, e_shnum, e_shstrndx
        )
        return elf_header

    def create_section_headers(self):
        # Таблица имен секций (.shstrtab) для имен `.text`, `.data`, `.bss`
        shstrtab = b'\x00.text\x00.data\x00.bss\x00.shstrtab\x00'
        shstrtab_offset = 0x200  # Смещение до начала шизтаб в файле

        # Заголовок NULL секции (нулевая запись)
        sh_null = struct.pack('<IIQQQQIIQQ', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        # Заголовок секции .text (код)
        sh_text = struct.pack(
            '<IIQQQQIIQQ',
            1,               # Имя (смещение в .shstrtab)
            1,               # Тип секции (SHT_PROGBITS)
            6,               # Флаги (бинарный код)
            0,               # Адрес загрузки (н/д для объекта)
            0x100,           # Смещение секции
            len(self.text_section), # Размер секции
            0,               # Связи (link)
            0,               # Инфо (info)
            16,              # Адресная единица выравнивания
            0                # Размер записи (н/д)
        )

        # Заголовок секции .data
        sh_data = struct.pack(
            '<IIQQQQIIQQ',
            7,               # Имя (смещение в .shstrtab)
            1,               # Тип секции (SHT_PROGBITS)
            3,               # Флаги (чтение + запись)
            0,               # Адрес загрузки (н/д для объекта)
            0x100 + len(self.text_section), # Смещение секции
            len(self.data_section), # Размер секции
            0,               # Связи (link)
            0,               # Инфо (info)
            8,               # Выравнивание
            0                # Размер записи
        )

        # Заголовок секции .bss
        sh_bss = struct.pack(
            '<IIQQQQIIQQ',
            13,              # Имя (смещение в .shstrtab)
            8,               # Тип секции (SHT_NOBITS)
            3,               # Флаги (чтение + запись)
            0,               # Адрес загрузки (н/д для объекта)
            0x100 + len(self.text_section) + len(self.data_section), # Смещение секции
            len(self.bss_section), # Размер секции
            0,               # Связи (link)
            0,               # Инфо (info)
            8,               # Выравнивание
            0                # Размер записи
        )

        # Заголовок секции .shstrtab (таблица имен секций)
        sh_shstrtab = struct.pack(
            '<IIQQQQIIQQ',
            18,              # Имя (смещение в .shstrtab)
            3,               # Тип секции (SHT_STRTAB)
            0,               # Флаги
            0,               # Адрес загрузки
            shstrtab_offset, # Смещение секции
            len(shstrtab),   # Размер секции
            0,               # Связи
            0,               # Инфо
            1,               # Выравнивание
            0                # Размер записи
        )

        return sh_null + sh_text + sh_data + sh_bss + sh_shstrtab, shstrtab

    def save_to_file(self, filename):
        # Создание ELF заголовка
        elf_header = self.create_elf_header()

        # Создание заголовков секций и таблицы строк
        section_headers, shstrtab = self.create_section_headers()

        # Смещение для секций .text и .data (заполнение секций пока пустыми)
        padding = b'\x00' * (0x100 - len(elf_header))

        # Собираем финальный объектный ELF-файл
        with open(filename, 'wb') as f:
            f.write(elf_header)            # Заголовок ELF
            f.write(padding)               # Пустое пространство до 0x100
            f.write(self.text_section)     # Секция .text (пустая)
            f.write(self.data_section)     # Секция .data (пустая)
            f.write(self.bss_section)      # Секция .bss (пустая)
            f.write(shstrtab)              # Таблица имен секций
            f.write(section_headers)       # Заголовки секций
if __name__ == "__main__":
    # Использование
    elf_file = ELF64ObjectFile()
    elf_file.save_to_file("output.o")
