#!/usr/bin/python
# coding: utf-8

"""
    kippo tools
    ~~~~~~~~~~~

    :copyleft: 2012 by Jens Diemer
    :license: GNU GPL v3 or above
"""


import argparse
import re
import os
import pprint
import sys


LOGIN_FAILED = "failed"
LOGIN_SUCCEEDED = "succeeded"
LOGIN_INFO_RE = re.compile(r".*? login attempt \[(?P<name>.*?)/(?P<pass>.*?)\] (?P<status>.*?)$")
REMOTE_IP_RE = re.compile(r".*? New connection: (?P<ip>.*?):(?P<port>.*?) .*?$")
SSH_CLIENT_RE = re.compile(r".*? Remote SSH version: (?P<client>.*?)$")


def bool_status(groupdict):
    status = groupdict.pop("status")
    if status == LOGIN_FAILED:
        groupdict["login_succeed"] = False
    elif status == LOGIN_SUCCEEDED:
        groupdict["login_succeed"] = True
    else:
        raise AssertionError("Status %r unknown." % status)


def _increase_dict_key(d, key):
    if not key in d:
        d[key] = 1
    else:
        d[key] += 1
        

def get_login_data(logfile):
    ip_data = {}
    client_data = {}
    login_data = []
    lines = 0
    f = file(logfile, "r")
    for line in f:
        lines += 1
        if "login attempt" in line:     
            match = LOGIN_INFO_RE.match(line)
            if match:          
                groupdict = match.groupdict()
                bool_status(groupdict)    
                login_data.append(groupdict)
        elif "New connection" in line:
            match = REMOTE_IP_RE.match(line)
            if match:
                groupdict = match.groupdict()
                _increase_dict_key(ip_data, groupdict["ip"])
        elif "Remote SSH version:" in line:
            match = SSH_CLIENT_RE.match(line)
            if match:
                groupdict = match.groupdict()
                _increase_dict_key(client_data, groupdict["client"])
                
    if verbosity >= 2:
        print "%i lines readed." % lines
    return login_data, ip_data, client_data


def stat_login_data(login_data):
    login_stats = {
        "count": 0,
        "succeed_count": 0,
        "fail_count": 0,
        
        "succeed_user_name_stats": {},
        "succeed_password_stats": {},
        
        "fail_user_name_stats": {},
        "fail_password_stats": {},
    }
    for login in login_data:
        login_stats["count"] += 1
        if login["login_succeed"]:
            login_stats["succeed_count"] += 1
            _increase_dict_key(login_stats["succeed_user_name_stats"], login["name"])
            _increase_dict_key(login_stats["succeed_password_stats"], login["pass"])
        else:
            login_stats["fail_count"] += 1
            _increase_dict_key(login_stats["fail_user_name_stats"], login["name"])
            _increase_dict_key(login_stats["fail_password_stats"], login["pass"])
    return login_stats          


def print_count_list(stats_dict, max_count):
    print "(total: %i)" % len(stats_dict)
    stats_list = [(count, value) for value, count in stats_dict.items()]
    stats_list.sort(reverse=True)#cmp=None, key=None, reverse=False)
    for item in stats_list[:max_count]:
        print "\t%3i - %r" % item


def print_login_stats(login_stats, max_count):
    print "total logins: %i - successful: %i - failed: %i" % (
        login_stats["count"], login_stats["succeed_count"], login_stats["fail_count"]
    )
    print
    
    print " * most %i successful names" % max_count,
    print_count_list(login_stats["succeed_user_name_stats"], max_count)
    
    print " * most %i failed names" % max_count,
    print_count_list(login_stats["fail_user_name_stats"], max_count)
    
    print " * most %i successful passwords" % max_count,
    print_count_list(login_stats["succeed_password_stats"], max_count)
    
    print " * most %i failed passwords" % max_count,
    print_count_list(login_stats["fail_password_stats"], max_count)   


def print_ip_data(ip_data, max_count):
    print " * most %i remote IPs" % max_count,
    print_count_list(ip_data, max_count)  


def print_client_data(client_data, max_count):
    print " * most %i use SSH client" % max_count,
    print_count_list(client_data, max_count)  


def get_cli_arguments():
    parser = argparse.ArgumentParser(
        description="simple kippo login statistics",
        epilog="kippo tools copyleft by Jens Diemer, GNU GPL v3 or above"
    )
    parser.add_argument("--logfile", help="path to kippo logfile",
        default = "~/kippo/log/kippo.log"
    )
    parser.add_argument(
        "-m", "--max", type=int, default=20,
        help="maximum number of items to display."
    )
    parser.add_argument(
        "-v", "--verbosity", type=int, choices=[0, 1, 2], default=1,
        help="increase output verbosity"
    )

    cli_arguments = parser.parse_args()
    if cli_arguments.verbosity >= 2:
        print cli_arguments
        
    return cli_arguments


if __name__ == "__main__":
    cli_arguments = get_cli_arguments()
    verbosity = cli_arguments.verbosity
    logfile = os.path.expanduser(cli_arguments.logfile)
    
#    logfile = "kippo.log"
#    verbosity = 2
    
    if verbosity >= 2:
        print "Analyse %r..." % logfile
    
    if not os.path.isfile(logfile):
        msg = (
            "Logfile %r can't read: doesn't exist.\n"
            " Please add/change --logfile parameter!\n"
        ) % logfile
        sys.stderr.write(msg)
        sys.exit(1)
        
    login_data, ip_data, client_data = get_login_data(logfile)
    if verbosity >= 2:
        print login_data
        pprint.pprint(ip_data)
        pprint.pprint(client_data)
    login_stats = stat_login_data(login_data)
    if verbosity >= 2:
        pprint.pprint(login_stats)
    
    print_login_stats(login_stats, cli_arguments.max)
    print_ip_data(ip_data, cli_arguments.max)
    print_client_data(client_data, cli_arguments.max)