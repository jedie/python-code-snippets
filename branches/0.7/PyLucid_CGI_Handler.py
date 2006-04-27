#!/usr/bin/python
# -*- coding: UTF-8 -*-

import cgitb;cgitb.enable()


from colubrid.server import CGIServer
from colubrid.debug import DebuggedApplication

if __name__ == "__main__":
    app = DebuggedApplication('PyLucid_app:app')
    CGIServer(app).run()
