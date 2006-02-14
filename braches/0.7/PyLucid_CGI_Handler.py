#!/usr/bin/python
# -*- coding: UTF-8 -*-

import cgitb;cgitb.enable()


from PyLucid_app import app

try:
    from PyLucid_app import exports
except ImportError:
    exports = {}

from colubrid.execute import CGIServer


if __name__ == "__main__":
    CGIServer(app, exports).run()
