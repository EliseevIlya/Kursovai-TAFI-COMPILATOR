class SymbolTable:
    def __init__(self):
        self.table = {}

    def add(self, lexeme):
        """Добавить лексему в таблицу, если её там ещё нет."""
        if lexeme not in self.table:
            self.table[lexeme] = len(self.table) + 1
        return self.table[lexeme]

    def lookup(self, lexeme):
        """Найти лексему в таблице."""
        return self.table.get(lexeme, None)

    def get(self, lexeme):
        """Получить номер лексемы."""
        return self.table[lexeme]


class StaticSymbolTable:
    def __init__(self, symbols):
        self.table = symbols

    def lookup(self, lexeme):
        """Найти лексему в таблице."""
        return self.table.get(lexeme, None)

    def get(self, lexeme):
        """Получить номер лексемы."""
        return self.table[lexeme]
