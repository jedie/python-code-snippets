#!/usr/bin/env python3

"""
    Python Skript zum neutralen Verlosen:
    https://www.classic-computing.org/alte-computer-immer-her-damit/
    https://github.com/jedie/python-code-snippets/blob/master/CodeSnippets/VzEkC-verlosung.py
"""

import difflib
import hashlib
import random
from collections import Counter


class VzEkC:
    def __init__(self, drawings, post_timestamp):
        assert isinstance(drawings, list)
        assert isinstance(post_timestamp, str)  # Timestamp muss ein String sein.

        self.drawings = sorted(drawings, key=lambda x: x['text'])  # Sortiert nach Paketnamen
        self.rnd = self._get_random(post_timestamp)  # Pseudo random basiert auf Zeitstempel

    def out(self, *args):
        print(*args)

    def _get_random(self, post_timestamp):
        """
        Erstelle ein pseudo-random objekt basierend auf dem Timestamp und den Teilnehmer Namen.
        """
        # Starte Hash mit dem Timestamp aus dem "letzten" Beitrag:
        m = hashlib.sha3_512()
        m.update(bytes(post_timestamp, encoding='ASCII'))

        # Alle Teilnehmer Namen (sortiert) in den Hash Wert einbeziehen:
        all_names = set()
        for data in self.drawings:
            for name in sorted(data['names']):
                all_names.add(name)
                m.update(bytes(name, encoding='UTF-8'))

        # Namen aller Teilnehmer sortiert ausgeben:
        all_names = sorted(all_names)
        self.out(f'Alle Teilnehmer: {", ".join(all_names)}')

        # Info zum SEED Wert zur Nachvollziehbarkeit ausgeben:
        seed = m.hexdigest()
        self.out(
            f'(Use pseudo-random number generator'
            f' Version {random.Random.VERSION} with seed={seed!r})'
        )
        return random.Random(seed)

    def _print_result(self, *, text, names):
        """
        Gibt die Gewinner eines Pakets aus.
        """
        self.out('_' * 100)
        self.out(f'Verlosung von: *** {text} ***')

        names.sort()  # Alle Namen sortieren

        # Auflisten der "Lose":
        c = Counter(names)
        for user, count in c.items():
            self.out(f' * {user} hat {count} Lose gekauft')

        self.out('Alle Lose/Namen im Topf:', names)
        self.out(f'Gewinner ist: *** {self.rnd.choice(names)} ***')

    def print_drawing(self):
        """
        Gib die Gewinner aller Pakete aus.
        """
        for drawings in self.drawings:
            self._print_result(**drawings)


def test_lottery():
    """

    """
    class TestVzEkC(VzEkC):
        buffer = []

        def out(self, *args):
            self.buffer.append(' '.join(str(arg) for arg in args))

    def unified_diff(txt1, txt2):
        return '\n'.join(
            difflib.unified_diff(txt1.splitlines(), txt2.splitlines())
        )

    lottery = TestVzEkC(
        drawings=[
            {
                'text': 'Paket Nr. 1',
                'names': [
                    'Mr.Bar',
                    'Mr.Foo', 'Mr.Foo', 'Mr.Foo',
                    'Mr.Schmidt', 'Mr.Schmidt',
                ]
            },
            {'text': 'Paket Nr. 2', 'names': ['Mr.Schmidt', 'Mr.Foo', 'Mr.Bar']},
            {'text': 'Paket Nr. 3', 'names': ['Mr.Schmidt', 'Mr.Foo', 'Mr.Bar']},
            # Pakete werden automatisch nach Namen sortiert:
            {'text': 'Paket Nr. 5', 'names': ['Mr.Schmidt', 'Mr.Foo', 'Mr.Bar']},
            {'text': 'Paket Nr. 4', 'names': ['Mr.Schmidt', 'Mr.Foo', 'Mr.Bar']},
        ],
        post_timestamp='1601933809'
    )
    lottery.print_drawing()
    output = '\n'.join(lottery.buffer)
    diff = unified_diff(output, """
Alle Teilnehmer: Mr.Bar, Mr.Foo, Mr.Schmidt
(Use pseudo-random number generator Version 3 with seed='2ed05778e97b0f4497673ac0994c05964c0df25ae92e5f0cf97dbb02ef06850829b74f2e2c3cce0edb2454efaa6e3c5ac228a219a3cc838cff9db81765c02386')
____________________________________________________________________________________________________
Verlosung von: *** Paket Nr. 1 ***
 * Mr.Bar hat 1 Lose gekauft
 * Mr.Foo hat 3 Lose gekauft
 * Mr.Schmidt hat 2 Lose gekauft
Alle Lose/Namen im Topf: ['Mr.Bar', 'Mr.Foo', 'Mr.Foo', 'Mr.Foo', 'Mr.Schmidt', 'Mr.Schmidt']
Gewinner ist: *** Mr.Bar ***
____________________________________________________________________________________________________
Verlosung von: *** Paket Nr. 2 ***
 * Mr.Bar hat 1 Lose gekauft
 * Mr.Foo hat 1 Lose gekauft
 * Mr.Schmidt hat 1 Lose gekauft
Alle Lose/Namen im Topf: ['Mr.Bar', 'Mr.Foo', 'Mr.Schmidt']
Gewinner ist: *** Mr.Bar ***
____________________________________________________________________________________________________
Verlosung von: *** Paket Nr. 3 ***
 * Mr.Bar hat 1 Lose gekauft
 * Mr.Foo hat 1 Lose gekauft
 * Mr.Schmidt hat 1 Lose gekauft
Alle Lose/Namen im Topf: ['Mr.Bar', 'Mr.Foo', 'Mr.Schmidt']
Gewinner ist: *** Mr.Schmidt ***
____________________________________________________________________________________________________
Verlosung von: *** Paket Nr. 4 ***
 * Mr.Bar hat 1 Lose gekauft
 * Mr.Foo hat 1 Lose gekauft
 * Mr.Schmidt hat 1 Lose gekauft
Alle Lose/Namen im Topf: ['Mr.Bar', 'Mr.Foo', 'Mr.Schmidt']
Gewinner ist: *** Mr.Schmidt ***
____________________________________________________________________________________________________
Verlosung von: *** Paket Nr. 5 ***
 * Mr.Bar hat 1 Lose gekauft
 * Mr.Foo hat 1 Lose gekauft
 * Mr.Schmidt hat 1 Lose gekauft
Alle Lose/Namen im Topf: ['Mr.Bar', 'Mr.Foo', 'Mr.Schmidt']
Gewinner ist: *** Mr.Schmidt ***
    """.strip())
    if diff:
        raise AssertionError(diff)
    print("\nSelf test OK\n")


if __name__ == '__main__':
    test_lottery()

    # Wichtige Hinweise zur reproduzierbaren Benutzung:
    #
    #  * Pakete ohne verkauftes Los *nicht* einfügen.
    #  * Immer alle Pakete mit mindestens *einen* Los Verkauf eingefügen
    #    (Bei nur einem Los Verkauf müsste man nicht Losen, ändert aber alle anderen Auslosungen!)
    #

    lottery = VzEkC(
        drawings=[
            # Ein Paket mit unterschiedlicher Anzahl an Losen.
            # Der Nickname aus dem Forum wird pro Los aufgelistet.
            # Die Reihenfolge der Namen ist egal, weil immer sortiert wird.
            {
                'text': 'Paket Nr. 1',
                'names': [
                    'Mr.Bar',  # << ein Los gekauft
                    'Mr.Foo', 'Mr.Foo', 'Mr.Foo',  # << Drei Lose gekauft
                    'Mr.Schmidt', 'Mr.Schmidt',  # << Zwei Lose gekauft
                ]
            },
            # Beispiel mit immer gleichen Namen führen zu unterschiedlichen Ergebnissen:
            {'text': 'Paket Nr. 2', 'names': ['Mr.Schmidt', 'Mr.Foo', 'Mr.Bar']},
            {'text': 'Paket Nr. 3', 'names': ['Mr.Schmidt', 'Mr.Foo', 'Mr.Bar']},
            {'text': 'Paket Nr. 4', 'names': ['Mr.Schmidt', 'Mr.Foo', 'Mr.Bar']},
            {'text': 'Paket Nr. 5', 'names': ['Mr.Schmidt', 'Mr.Foo', 'Mr.Bar']},
        ],
        # Zeitstempel aus dem ersten Beitrag des Kassenwarts nach dem Ende des Loskauf-Zeitraumes:
        post_timestamp='1601933809'
    )
    lottery.print_drawing()
