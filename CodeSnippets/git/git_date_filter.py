#!/usr/bin/env python
# coding: utf-8

"""
    Supported Keywords are:
		$LastChangedRevision$
		$Author$
		$Date$
		$Hash$
	git filter to change committer date in version info file.
	
	more info in README:
	https://github.com/jedie/python-code-snippets/tree/master/CodeSnippets/git/#readme
	
	:copyleft: 2012 by Jens Diemer, revised 2013 by Daniel Gross
	:license: GNU GPL v3 or above
	:homepage: https://github.com/jedie/python-code-snippets/tree/master/CodeSnippets/git/
Installation:
	Make sure this file is in the path
Add the following 3 lines to ".gitconfig" or to ".git/config":
	[filter "keywords"]
		smudge = git_keywords_filter.py smudge %f
		clean = git_keywords_filter.py clean %f 
Add the next line to ".gitattributes" or ".git/info/attributes"
	*.cpp filter=keywords

Done!
"""

import sys
import os
import subprocess
import time
import datetime
import re

SMUDGE = "smudge"
CLEAN = "clean"
KW_REGEX = re.compile(r"\$(\w+)(:[^$]*)?\$")
SVN_REV_REGEX = re.compile(r"git-svn-id: \S+@(\d+)")

def _error(msg):
	sys.stderr.write(msg + "\n")
	sys.stderr.flush()
	sys.exit(1)

def get_info(filename):
	info={};
	try:
		process = subprocess.Popen(
			# %ct: committer date, UNIX timestamp  
			# %H : hash
			# %cn: committer name
			# %b : commit body (this will contain the git-svn-id tag)
			["git.cmd", "log", '--pretty=%H;%cn;%ct;%b', "-1", "--", filename],
			shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
		)
	except Exception, err:
		return _error("Can't get git hash: %s" % err)
	process.wait()
	returncode = process.returncode
	if returncode != 0:
		return _error(
			"Can't get git hash, returncode was: %r"
			" - git stdout: %r"
			" - git stderr: %r"
			% (returncode, process.stdout.readline(), process.stderr.readline())
		)
	s=process.stdout.readline().split((';'),3);
	if len(s)>=4:
		info["Hash"]=s[0].strip();
		info["Author"]=s[1].strip();
		info["Date"]=datetime.datetime.fromtimestamp(int(s[2].strip()));
		# try to match an svn revision information from the commit body
		svnRevMatch = SVN_REV_REGEX.match(s[3].strip());
		# use this info, or otherwise set this value to the hash
		info["LastChangedRevision"] = int(svnRevMatch.group(1)) if svnRevMatch else info["Hash"]		
	return info

def smudge(filename):
	info = get_info(filename)
	def kwreplace(match):
		kw = match.group(1)
		if kw in info:
			return "$%s: %s$" % (kw, info[kw])
		else:
			return "$%s$" % kw

	for line in sys.stdin:
		sys.stdout.write(KW_REGEX.sub(kwreplace, line))

def clean(filename):
	def cleankw(match):
		return "$%s$" % match.group(1)

	for line in sys.stdin:
		sys.stdout.write(KW_REGEX.sub(cleankw, line))


if __name__ == "__main__":
#    import doctest
#    print doctest.testmod()
#    sys.exit()

	if len(sys.argv) < 3:
		_error("Error: missing commandline parameters %s or %s and filename!" % (SMUDGE, CLEAN))

	if sys.argv[1] == SMUDGE:
		smudge(sys.argv[2])
	elif sys.argv[1] == CLEAN:
		clean(sys.argv[2])
	else:
		_error("Error: first argument must be %s or %s" % (SMUDGE, CLEAN))
