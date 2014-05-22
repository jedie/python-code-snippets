#!/usr/bin/env python3
# coding: utf-8

from pprint import pprint
import argparse
import os
import socket
import sys
import xml.etree.ElementTree as ET


DEFAULT_CFG = "~/.config/syncthing/config.xml"


class Node(object):
    def __init__(self, name, id, raw_address):
        self.name = name
        self.id = id

        self.raw_address = raw_address

        if raw_address == "dynamic":
            self.dynamic = True
        else:
            self.dynamic = False
            self.address, self.port = raw_address.split(":", 1)
            self.port = int(self.port)

    def test_port(self):
        print("\nTest %s (address: '%s'):" % (self.name, self.raw_address))

        if self.dynamic:
            print("\tTODO: 'dynamic' nodes are not supported, yet.")
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        addrinfo = socket.getaddrinfo(self.address, self.port)
        addresses = set()
        for res in addrinfo:
            af, socktype, proto, canonname, sa = res
            addresses.add(sa[0])

        print("\t%s ==> %s" % (self.address, ",".join(addresses)))

        errno = sock.connect_ex((self.address, self.port))
        sock.close()
        if errno == 0:
            print("\tPort %s is open" % self.port)
        else:
            print("\tPort %s is not open (Error no.: %s)" % (self.port, errno))

    def __str__(self):
        if self.dynamic:
            parts = (self.name, "dynamic", self.id)
        else:
            parts = (self.name, self.address, "%s" % self.port, self.id)
        return "\n".join(parts)


class SyncthinConfig(object):
    def __init__(self, cfg_file):
        tree = ET.parse(cfg_file)
        self.root = tree.getroot()

    def get_nodes(self):
        nodes = []
        for item in self.root:
            if item.tag != "node":
                continue

            node = Node(
                name=item.attrib["name"],
                id=item.attrib["id"],
                raw_address=item[0].text
            )
            nodes.append(node)
        return nodes



class FileType2(argparse.FileType):
    def __call__(self, string):
        string = os.path.expanduser(string)
        return super(FileType2, self).__call__(string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Verify nodes in syncthing config')
    parser.add_argument(
        "cfg", nargs='?', default=DEFAULT_CFG, type=FileType2("r"),
        help="Path to syncthing config.xml file. (default: %(default)s)"
    )
    args = parser.parse_args()

    cfg = SyncthinConfig(args.cfg)
    nodes = cfg.get_nodes()

    for node in nodes:
        node.test_port()
        print()
