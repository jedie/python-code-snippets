
"""
Kleine Helferlein
"""

import locale

def spezial_cmp(a,b):
    """
    Abgewandelte Form für sort()
    Sortiert alle mit "_" beginnenen items nach oben
    """
    def get_first_letter(l):
        """
        Einfache Art den ersten Buchstaben in einer verschachtelten
        Liste zu finden. Funktioniert aber nur dann, wenn es nur Listen
        sind und immer [0] irgendwann zu einem String wird!
        """
        if isinstance(l, list):
            get_first_letter(l[0])
        return l[0]

    a = get_first_letter(a)
    b = get_first_letter(b)

    return locale.strcoll(a,b)