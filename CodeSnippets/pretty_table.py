#!/usr/bin/python3

class PrettyTable:
    """
    Created 21.11.2018 by Jens Diemer <code@jensdiemer.de>
    GNU General Public License v3 or above - https://opensource.org/licenses/gpl-license.php

    >>> pt=PrettyTable(headings=("1", "The two headline", "3"))
    >>> pt.add_row(row=("first row", "a", "b"))
    >>> pt.add_row(row=("second row", "c", "d"))
    >>> pt.add_row(row=("third row", "e", "f"))

    >>> pt.print_table()
    1          The two headline 3
    first row  a                b
    second row c                d
    third row  e                f

    >>> pt.print_table(prefix="| ", join_str=" | ", suffix=" |")
    | 1          | The two headline | 3 |
    | first row  | a                | b |
    | second row | c                | d |
    | third row  | e                | f |
    """

    def __init__(self, *, headings):
        assert isinstance(headings, (list, tuple))
        self.rows = [headings]
        self.column_count = len(headings)
        self.widths = [len(i) for i in headings]

    def add_row(self, *, row):
        assert isinstance(row, (list, tuple))
        assert len(row) == self.column_count
        self.rows.append(row)

        for no, cell in enumerate(row):
            self.widths[no] = max(self.widths[no], len(cell))

    def iter_lines(self, *, prefix="", join_str=" ", suffix=""):
        for row in self.rows:
            line = []
            for width, cell in zip(self.widths, row):
                line.append("{:<{width}}".format(cell, width=width))

            yield prefix + join_str.join(line) + suffix

    def print_table(self, *, prefix="", join_str=" ", suffix=""):
        for line in self.iter_lines(prefix=prefix, join_str=join_str, suffix=suffix):
            print(line)


if __name__ == "__main__":
    import doctest

    print(
        "Doctest:",
        doctest.testmod(
            # verbose=True
            verbose=False
        ),
    )
