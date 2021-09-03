#!/usr/bin/env python3

"""
    Python Skript zum neutralen Verlosen, siehe:
    https://forum.classic-computing.de/forum/index.php?thread/21625-kleines-python-skript-zum-verlosen/
"""

import hashlib
import random
from collections import Counter


class VzEkC:
    def __init__(self, drawings, post_timestamp):
        assert isinstance(drawings, list)
        assert isinstance(post_timestamp, str)  # Timestamp muss ein String sein.

        self.drawings = drawings
        self.rnd = self._get_random(post_timestamp)

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
        print(f'Alle Teilnehmer: {", ".join(all_names)}')

        # Info zum SEED Wert zur Nachvollziehbarkeit ausgeben:
        seed = m.hexdigest()
        print(
            f'(Use pseudo-random number generator'
            f' Version {random.Random.VERSION} with seed={seed!r})'
        )
        return random.Random(seed)

    def _print_result(self, *, text, names):
        """
        Gibt die Gewinner eines Pakets aus.
        """
        print('_' * 100)
        print(f'Verlosung von: *** {text} ***')

        names.sort()  # Alle Namen sortieren

        # Auflisten der "Lose":
        c = Counter(names)
        for user, count in c.items():
            print(f' * {user} hat {count} Lose gekauft')

        print('Alle Lose/Namen im Topf:', names)
        print(f'Gewinner ist: *** {self.rnd.choice(names)} ***')

    def print_drawing(self):
        """
        Gib die Gewinner aller Pakete aus.
        """
        for drawings in self.drawings:
            self._print_result(**drawings)


if __name__ == '__main__':
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
