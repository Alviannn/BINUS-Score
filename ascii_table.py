from typing import List, Tuple


class TableColHeader:

    def __init__(self, title: str, length: int, end_align: bool = False):
        self.title = title
        self.length = length
        self.end_align = end_align


class Table:

    def __init__(self, headers: List[TableColHeader]):
        row_format = header_format = '|'
        line = '+'

        header_names = []
        for header in headers:
            line += '-' + ('-' * header.length) + '-+'

            header_format += f' %-{header.length}s |'
            row_format += f' %{"-" if not header.end_align else ""}{header.length}s |'

            header_names.append(header.title)

        self.header = header_format % tuple(header_names)
        self.row_format = row_format
        self.line = line
        self.rows: List[Tuple[str]] = []

    def add_row(self, row: Tuple[str]):
        self.rows.append(tuple(row))

    def print_table(self):
        print(self.line)
        print(self.header)
        print(self.line)

        for row in self.rows:
            print(self.row_format % row)

        print(self.line)