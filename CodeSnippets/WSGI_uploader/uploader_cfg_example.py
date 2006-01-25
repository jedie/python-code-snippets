#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" uploader config handler

used WSGI colubird by Armin Ronacher <armin.ronacher@active-4.com>
http://wsgiarea.pocoo.org/colubrid/
"""


import uploader

#~ uploader.cfg.only_https = True
uploader.cfg.only_https = False

#~ uploader.cfg.only_auth_users = True
uploader.cfg.only_auth_users = False

#~ uploader.cfg.send_email_notify = True
uploader.cfg.send_email_notify = False

#~ uploader.cfg.notifer_email_from_adress = "uploader@example.com"
#~ uploader.cfg.notifer_email_to_adress = "uploader@example.com"
#~ uploader.cfg.bufsize = 8192
#~ uploader.cfg.upload_dir = "uploads"


#___________________________________________________________________________

app = uploader.uploader

