# -*- coding: utf-8 -*-
"""
    Colubrid WSGI Toolkit
    ---------------------
"""

__version__ = '0.8'
__author__ = 'Armin Ronacher <armin.ronacher@active-4.com>'
__license__ = 'GNU General Public License (GPL)'

from colubrid.application import *
from colubrid.execute import register
register()
