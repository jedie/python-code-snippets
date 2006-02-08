#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" uploader config handler

used WSGI colubird by Armin Ronacher <armin.ronacher@active-4.com>
http://wsgiarea.pocoo.org/colubrid/
"""


import uploader

cfg = uploader.cfg

cfg.allow_download = True
#~ cfg.allow_download = False

#~ cfg.only_https = True
cfg.only_https = False

#~ cfg.only_auth_users = True
cfg.only_auth_users = False

#~ cfg.send_email_notify = True
cfg.send_email_notify = False

#~ cfg.notifer_email_from_adress = "uploader@example.com"
#~ cfg.notifer_email_to_adress = "uploader@example.com"
#~ cfg.bufsize = 8192
#~ cfg.upload_dir = "uploads"


#___________________________________________________________________________

app = uploader.uploader

