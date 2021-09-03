import random
from collections import Counter

SEED=1

class VzEkC:
    def __init__(self):
        self.rnd = random.Random(SEED)
        print(
            f'(Use pseudo-random number generator'
            f' Version {random.Random.VERSION} with seed={SEED!r})'
        )

    def drawing(self, text, names):
        print('_' * 100)
        print(f'Verlosung von: *** {text} ***')

        names.sort() # Alle Namen sortieren

        # Auflisten der "Lose":
        c = Counter(names)
        for user, count in c.items():
            print(f' * {user} hat {count} Lose gekauft')

        print('Alle Lose/Namen im Topf:', names)
        print(f'Gewinner ist: *** {self.rnd.choice(names)} ***')


if __name__ == '__main__':
    lottery = VzEkC()
    lottery.drawing(
        text='Paket Nr. 1',
        names=[
            'Mr.Bar',  # << ein Los gekauft
            'Mr.Foo', 'Mr.Foo', 'Mr.Foo',  # << Drei Lose gekauft
            'Mr.Schmidt', 'Mr.Schmidt',  # << Zwei Lose gekauft
        ]
    )
    lottery.drawing(
        text='Paket Nr. 2',
        names=[
            'Mr.Schmidt', 'Mr.Foo', 'Mr.Bar'  # << Jeder nur ein Los
        ]
    )
