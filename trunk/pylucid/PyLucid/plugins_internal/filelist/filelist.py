#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid media file manager
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    TODO:
        *
        *

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev:  $
    $Author: $

    :copyleft: Ibon, Jens Diemer
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= ""

import time, cgi
import os,sys,datetime,stat
from time import gmtime, strftime,time,localtime,strftime

from django import newforms as forms
from django.utils.translation import ugettext as _

from PyLucid import settings
from PyLucid.models import Page
from PyLucid.system.BasePlugin import PyLucidBasePlugin


ABSPATH = os.path.abspath(settings.MEDIA_ROOT)


def _action(dir_string, filename, action, dest=''):
    """
    Diferent actions over file or dir
    """
    filerel=os.path.normpath(os.path.join(dir_string, filename))
    fileabs=os.path.abspath(os.path.join(ABSPATH, filerel))

    if not fileabs.startswith(ABSPATH):
        WrongDirectory(fileabs)

    if action=='del':
        os.remove(fileabs)
        return os.path.normpath(dir_string)
    if action=='deldir':
        os.rmdir(fileabs)
        return os.path.normpath(os.path.join(filerel, './../'))
    if action=='rename':
        os.rename(fileabs, dest)
        return filerel
    elif action=='mdir':
        if fileabs.startswith("."):
            os.mkdir(fileabs)
            return os.path.normpath(dir_string)



def make_dirlist(path, result=[]):
    """
    >>> make_dirlist("/data/one/two")
    [('data/one/two', 'two'), ('data/one', 'one'), ('data', 'data')]
    """
    path = path.strip("/")

    head, tail = os.path.split(path)
    result.append((path, tail))

    if head:
        # go recusive deeper
        return make_dirlist(head, result)
    else:
        result.reverse()
        return result




class filelist(PyLucidBasePlugin):

    def getFilesList(self, rel_dir):
        """
        Returns all file in dir current_dir
         'relative' to url root

        """
        listFile=[]

        if not rel_dir:
            # current dir it the media Root
            listDir=[]
        else:
            # Add the ".." dir item
            updir = os.path.split(rel_dir)[0]
            listDir = [{
                "name": "..",
                "dir_link": self.URLs.methodLink(
                    method_name="lucidTag", args=updir
                ),
            }]

        # convert the relative path to absolute filesystem path
        abs_fs_path=os.path.abspath(os.path.join(ABSPATH, rel_dir))

        if not abs_fs_path.startswith(ABSPATH):
            raise WrongDirectory(abs_fs_path)
            #return listDir,listFile


        for item in os.listdir(abs_fs_path):
            if item.startswith("."):
                # skip hidden files or dirs
                continue

    #        try:

            item_rel_dir = os.path.join(rel_dir, item)
            item_abs_fs_path = os.path.join(abs_fs_path, item)
            statinfo = os.stat(item_abs_fs_path)
#            accestime = statinfo[stat.ST_ATIME]

            item_dict={
                'name': item,
                'time': strftime('%Y:%m:%M',localtime(statinfo[stat.ST_MTIME])),
                'size': statinfo[stat.ST_SIZE],
                'statinfo': statinfo,
            }
            if stat.S_ISDIR(statinfo[stat.ST_MODE]):
                item_dict["dir_link"] = self.URLs.methodLink(
                    method_name="lucidTag", args=item_rel_dir
                )
                listDir.append(item_dict)
            else:
                listFile.append(item_dict)
    #        except:
    #            theFile={
    #                'name': f+"_error",
    #                'statinfo': ''
    #            };
    #            listFile.append(theFile)

        return listDir,listFile


    def make_dir_links(self, path):
        """
        path: /data/one/two

        return [('/data/one/two','two'), ('/data/one','one'),('/data','data')]
        """
        dir_links = [{
            "name": "<root>",
            "link": self.URLs.methodLink(method_name="lucidTag"),
        }]
        if path:
            # Not in the root
            dirlist = make_dirlist(path, [])
            for path, name in dirlist:
                dir_links.append({
                    "name": name,
                    "link": self.URLs.methodLink(
                        method_name="lucidTag", args=path
                    ),
                })

        return dir_links

#    def createdirtuple(self, dirfinal, allpath):
#        """
#        Creates a tuble (dirname, hispath)
#        """
#        return (dirfinal, os.path.join(allpath,dirfinal))


    def lucidTag(self, rest=''):
        """
        List dir and file. Some actions.
        rest: path to dir or file
        """
        # Change the global page title:
        self.context["PAGE"].title = _("File list")
        context = {}
        dir_list = []
        files_list = []

        dir_string=''

        if rest!='':
            dir_string=os.path.normpath(rest)

        if self.request.method == 'POST':
            if self.request.has_key('action'):
                dir_string=os.path.normpath(self.request['dir_string'])
                filename=os.path.normpath(self.request['filename'])

                newdir = _action(dir_string, filename, self.request['action'])
                dir_string = newdir

            elif self.request.FILES.has_key('ufile'):
                """
                uploading a file
                """
                files=self.request.FILES['ufile']
                dir_string = os.path.normpath(self.request['dir_string'])
                filename = os.path.normpath(files['filename'])
                pathFile = os.path.abspath(
                    os.path.join(ABSPATH, os.path.join(dir_string, filename))
                )
                try:
                    fileLike = file(pathFile,'wb') #if it exists, overwrite
                    fileLike.write(files['content'])
                    fileLike.close()
                except Exception, e:
                    self.page_msg.red("Can't write file: '%s'" % e)
                else:
                    self.page_msg.green(
                        "File '%s' written successfull." % filename
                    )

        dir_list,files_list = self.getFilesList(dir_string)

        context = {
            "url": self.URLs.methodLink("lucidTag"),
            "dir": dir_string,
            "dir_links": self.make_dir_links(dir_string),
            "files_list": files_list,
            "dir_list": dir_list,
            "media_url": settings.MEDIA_URL,
            "messages": self.page_msg,
        }

#        self._render_template("file_form", context, debug=True)
        self._render_template("file_form", context)#, debug=True)




class WrongDirectory(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)





