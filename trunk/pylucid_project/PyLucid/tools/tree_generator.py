# -*- coding: utf-8 -*-
"""
    PyLucid.tools.tree_generator.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Generate a tree of the cms pages, who are orginised in a parent-model.
    usefull for the main menu and the sitemap.

    Original code by Marc 'BlackJack' Rintsch
    see: http://www.python-forum.de/topic-10852.html (de)


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


class MenuNode(object):
    def __init__(self, id, data={}, parent=None):
        self.id = id
        self.data = data
        self.parent = parent
        self.active = False
        self.subnodes = list()
        self.visible = False

    def add(self, node):
        """
        add a new sub node.
        """
        self.subnodes.append(node)
        node.parent = self

    def activate(self):
        """
        activate self + all sub nodes + the parent node
        """
        self.visible = True
        self.active = True
        
        # Activate all subnodes:
        for subnode in self.subnodes:
            subnode.visible = True
            
        # activate the parent node
        if self.parent is not None:
            self.parent.activate()
    
    def activate_expanded(self, group_key, group_value):
        """
        enlarged the visible group.
        Same as 'activate', but makes only self node, sub nodes and parent node 
        visible, if data[group_key] == group_value
        """
        def conditional_activate(node):
            if node.data[group_key] == group_value:
                node.visible = True
            else:
                node.visible = False
        
        conditional_activate(self)
        for subnode in self.subnodes:
            conditional_activate(subnode)
            
        if self.parent is not None:
            conditional_activate(self.parent)
        

    def _get_current_entry(self, level):
        current_entry = self.data.copy()
        current_entry["level"] = level
        current_entry["active"] = self.active
        return current_entry

    def to_dict(self, level=0):
        """
        built the tree dict of all active nodes and insert a level info
        """
        current_entry = self._get_current_entry(level)

        subitems = [subnode.to_dict(level + 1)
                    for subnode in self.subnodes
                    if subnode.visible]
        if subitems:
            current_entry['subitems'] = subitems

        return current_entry

    def get_flat_list(self, level=0):
        """
        genrate a flat list for all visible pages and insert a level info
        """
        flat_list=[]

        current_entry = self._get_current_entry(level)
        flat_list.append(current_entry)

        for subnode in self.subnodes:
            if subnode.visible:
                flat_list += subnode.get_flat_list(level + 1)

        return flat_list




class TreeGenerator(object):
    def __init__(self, flat_data):
        # Create a dict with all pages as nodes
        self.nodes = dict((n['id'], MenuNode(n['id'], n))
                          for n in flat_data)

        # Create the root node
        self.root = MenuNode(id=None)
        self.nodes[None] = self.root

        # built the node tree
        for node_data in flat_data:
            id = node_data['id']
            parent = node_data['parent']
            try:
                self.nodes[parent].add(self.nodes[id])
            except KeyError:
                # If the user is not logged in and there exist a secret area,
                # we have some page how assign to a hidden page. All hidden
                # pages are filtered with the django orm. So we can' assign
                # a page how are a parent of a hidden page
                continue

    def to_dict(self):
        """
        built the tree dict of all visible nodes.
        """
        return self.root.to_dict()['subitems']

    def activate_all(self):
        """
        make all nodes visible (for a sitemap)
        """
        for node in self.nodes.itervalues():
            node.visible = True

    def deactivate_all(self):
        """
        makes all nodes invisible.
        """
        for node in self.nodes.itervalues():
            node.visible = False

    def activate(self, id):
        """
        make one node visible. (for the main menu)
        """
        self.nodes[id].activate()

    #___________________________________________________________________________
    
#    def _get_group_node(self, group_key, id, debug):
#        """
#        activate a coherent group, which have the same value in the 'group_key'.
#        returns the first node with a other group value.
#        """
#        if debug:
#            print "debug _get_group_node() id=%s" % id
#            
#        self.deactivate_all()
#        
#        node = self.nodes[id]
#        group_value = node.data[group_key]
#
#        # go to the first parent node how has a other group value:
#        old_node = node
#        while True:
#            if node.parent == None:
#                break
#            node = node.parent
#            if node.data[group_key] != group_value:
#                break
#            old_node = node
#        first_node = old_node
#        if debug:
#            print "first node with the same group value:\n\t", first_node.data
#        
#        # expand/activate the group:
#        for subnode in first_node.subnodes:
#            if debug:
#                print "subnode:", subnode.data
#            subnode.activate_expanded(group_key, group_value)
#        
#        return first_node
#        
#    def get_group_dict(self, group_key, id, debug=False):
#        """
#        returns a coherent group as a dict
#        """
#        node = self._get_group_node(group_key, id, debug)
#        return node.to_dict()#["subitems"]
#    
#    def get_group_list(self, group_key, id, debug=False):
#        """
#        returns a coherent group as a flat list.
#        """
#        node = self._get_group_node(group_key, id, debug)
#        return node.get_flat_list()#[1:]
        
    #___________________________________________________________________________

    def get_menu_tree(self, id=None):
        """
        generate a tree dirct for the main menu.
        If id==None: Only the top pages are visible!
        """
        self.deactivate_all()
        self.activate(id)
        if id:
            self.nodes[id].data["is_current"] = True
        return self.to_dict()

    def get_sitemap_tree(self):
        """
        generate a tree wih all nodes for a sitemap
        """
        self.activate_all()
        return self.to_dict()

    def get_flat_list(self):
        """
        returns a flat list of all visible pages with the level info.
        """
        return self.root.get_flat_list()[1:]



#_______________________________________________________________________________
# MODULE TEST:



def _test_generator(tree, display_result):
    #
    # Sitemap.
    #
    def print_data(txt, data):
        print '-' * 40
        print "***** %s *****" % txt
        pprint(data)
        
    def check(result, must_be, no):
        failed = result != must_be
        if failed or display_result:
            txt = "No. %s - result:" % no
            print_data(txt, result)
        if failed:
            txt = "ERROR %s - must be:" % no
            print_data(txt, must_be)
            
            try:
                # Display a diff, if PyLucid's diff tool is available
                from PyLucid.tools.Diff import diff_lines
            except ImportError:
                pass
            else:
                print "-"*79
                print diff_lines(pformat(must_be), pformat(result))
                print "-"*79
            
            raise AssertionError("wrong result.")
            

        
    result = tree.get_sitemap_tree()
    must_be = [{'active': False,
  'group': 'one',
  'id': 1,
  'level': 1,
  'name': '1. AAA',
  'parent': None,
  'subitems': [{'active': False,
                'group': 'two',
                'id': 2,
                'level': 2,
                'name': '1.1. BBB',
                'parent': 1},
               {'active': False,
                'group': 'two',
                'id': 3,
                'level': 2,
                'name': '1.2. BBB',
                'parent': 1,
                'subitems': [{'active': False,
                              'group': 'two',
                              'id': 4,
                              'level': 3,
                              'name': '1.2.1. CCC',
                              'parent': 3},
                             {'active': False,
                              'group': 'two',
                              'id': 5,
                              'level': 3,
                              'name': '1.2.2. CCC',
                              'parent': 3}]}]},
 {'active': False,
  'group': 'one',
  'id': 6,
  'level': 1,
  'name': '2. DDD',
  'parent': None,
  'subitems': [{'active': False,
                'group': 'two',
                'id': 7,
                'level': 2,
                'name': '2.1. EEE',
                'parent': 6},
               {'active': False,
                'group': 'two',
                'id': 8,
                'level': 2,
                'name': '2.2. EEE',
                'parent': 6}]}]
    check(result, must_be, no=1)


    #
    # No menu point active
    #   => Display the first Level.
    #
    result = tree.get_menu_tree()
    must_be = [{'active': False,
          'group': 'one',
          'id': 1,
          'level': 1,
          'name': '1. AAA',
          'parent': None},
         {'active': False,
          'group': 'one',
          'id': 6,
          'level': 1,
          'name': '2. DDD',
          'parent': None}]
    check(result, must_be, no=2)


    #
    # Activate the second menu point.
    #
    result = tree.get_menu_tree(2)
    must_be = [{'active': True,
      'group': 'one',
      'id': 1,
      'level': 1,
      'name': '1. AAA',
      'parent': None,
      'subitems': [{'active': True,
                    'group': 'two',
                    'id': 2,
                    'is_current': True,
                    'level': 2,
                    'name': '1.1. BBB',
                    'parent': 1},
                   {'active': False,
                    'group': 'two',
                    'id': 3,
                    'level': 2,
                    'name': '1.2. BBB',
                    'parent': 1}]},
     {'active': False,
      'group': 'one',
      'id': 6,
      'level': 1,
      'name': '2. DDD',
      'parent': None}]
    check(result, must_be, no=3)


    #
    # Activate the sixth menu point.
    #
    result = tree.get_menu_tree(6)
    must_be = [{'active': True,
      'group': 'one',
      'id': 1,
      'level': 1,
      'name': '1. AAA',
      'parent': None},
     {'active': True,
      'group': 'one',
      'id': 6,
      'is_current': True,
      'level': 1,
      'name': '2. DDD',
      'parent': None,
      'subitems': [{'active': False,
                    'group': 'two',
                    'id': 7,
                    'level': 2,
                    'name': '2.1. EEE',
                    'parent': 6},
                   {'active': False,
                    'group': 'two',
                    'id': 8,
                    'level': 2,
                    'name': '2.2. EEE',
                    'parent': 6}]}]
    check(result, must_be, no=4)


    #
    # a flat list for all current active pages
    #
    tree.deactivate_all()
    tree.activate(id=6)
    result = tree.get_flat_list()
    must_be = [{'active': True,
      'group': 'one',
      'id': 1,
      'level': 1,
      'name': '1. AAA',
      'parent': None},
     {'active': True,
      'group': 'one',
      'id': 6,
      'is_current': True,
      'level': 1,
      'name': '2. DDD',
      'parent': None},
     {'active': False,
      'group': 'two',
      'id': 7,
      'level': 2,
      'name': '2.1. EEE',
      'parent': 6},
     {'active': False,
      'group': 'two',
      'id': 8,
      'level': 2,
      'name': '2.2. EEE',
      'parent': 6}]
    check(result, must_be, no=5)


    #
    # generate a flat list from all pages
    #
    tree.activate_all()
    result = tree.get_flat_list()
    must_be = [{'active': True,
      'group': 'one',
      'id': 1,
      'level': 1,
      'name': '1. AAA',
      'parent': None},
     {'active': True,
      'group': 'two',
      'id': 2,
      'is_current': True,
      'level': 2,
      'name': '1.1. BBB',
      'parent': 1},
     {'active': False,
      'group': 'two',
      'id': 3,
      'level': 2,
      'name': '1.2. BBB',
      'parent': 1},
     {'active': False,
      'group': 'two',
      'id': 4,
      'level': 3,
      'name': '1.2.1. CCC',
      'parent': 3},
     {'active': False,
      'group': 'two',
      'id': 5,
      'level': 3,
      'name': '1.2.2. CCC',
      'parent': 3},
     {'active': True,
      'group': 'one',
      'id': 6,
      'is_current': True,
      'level': 1,
      'name': '2. DDD',
      'parent': None},
     {'active': False,
      'group': 'two',
      'id': 7,
      'level': 2,
      'name': '2.1. EEE',
      'parent': 6},
     {'active': False,
      'group': 'two',
      'id': 8,
      'level': 2,
      'name': '2.2. EEE',
      'parent': 6}]
    check(result, must_be, no=6)
    
    
#    #
#    # a coherent group, which have the same value in the 'group_key'
#    #
#    result = tree.get_group_dict(group_key="group", id=5, debug=True)
#    must_be = {'active': False,
#     'group': 'two',
#     'id': 3,
#     'level': 0,
#     'name': '1.2. BBB',
#     'parent': 1,
#     'subitems': [{'active': False,
#                   'group': 'two',
#                   'id': 4,
#                   'level': 1,
#                   'name': '1.2.1. CCC',
#                   'parent': 3},
#                  {'active': False,
#                   'group': 'two',
#                   'id': 5,
#                   'level': 1,
#                   'name': '1.2.2. CCC',
#                   'parent': 3}]}
#    check(result, must_be, no=7)  
#    
#    result = tree.get_group_dict(group_key="group", id=8, debug=True)
#    must_be = {'active': False,
#     'group': 'two',
#     'id': 8,
#     'level': 0,
#     'name': '2.2. EEE',
#     'parent': 6}
#    check(result, must_be, no=8)
#
#    result = tree.get_group_dict(group_key="parent", id=3, debug=True)
#    must_be = {'active': False,
#     'group': 'two',
#     'id': 3,
#     'level': 0,
#     'name': '1.2. BBB',
#     'parent': 1}
#    check(result, must_be, no=9)
    

#_______________________________________________________________________________


if __name__ == "__main__":
    print "module test - START\n"
    from pprint import pprint, pformat

    data = [
        {'id': 1, 'parent': None, 'group': 'one', 'name': '1. AAA'},
        {'id': 2, 'parent': 1,    'group': 'two', 'name': '1.1. BBB'},
        {'id': 3, 'parent': 1,    'group': 'two', 'name': '1.2. BBB'},
        {'id': 4, 'parent': 3,    'group': 'two', 'name': '1.2.1. CCC'},
        {'id': 5, 'parent': 3,    'group': 'two', 'name': '1.2.2. CCC'},
        {'id': 6, 'parent': None, 'group': 'one', 'name': '2. DDD'},
        {'id': 7, 'parent': 6,    'group': 'two', 'name': '2.1. EEE'},
        {'id': 8, 'parent': 6,    'group': 'two', 'name': '2.2. EEE'},
    ]
    print "Source data:"
    pprint(data)

    tree = TreeGenerator(data)
    _test_generator(tree, display_result=False)
#    _test_generator(tree, display_result=True)

    print "\nmodule test - END"



#    data = [
#     {'id': 1, 'parent': None, 'shortcut': u'index', 'template': 1},
#     {'id': 4, 'parent': None, 'shortcut': u'SiteMap', 'template': 1},
#     {'id': 5, 'parent': 1, 'shortcut': u'3dsmax1', 'template': 6},
#     {'id': 6, 'parent': 5, 'shortcut': u'Geschichte', 'template': 6},
#     {'id': 7, 'parent': 6, 'shortcut': u'3D-Studio', 'template': 6},
#     {'id': 8, 'parent': 5, 'shortcut': u'Einsatzgebiete', 'template': 6},
#     {'id': 9, 'parent': 8, 'shortcut': u'Firmen', 'template': 6},
#     {'id': 10, 'parent': 8, 'shortcut': u'Spiele', 'template': 6},
#     {'id': 12, 'parent': 5, 'shortcut': u'Eigenschaften', 'template': 6},
#     {'id': 13, 'parent': 6, 'shortcut': u'Historie', 'template': 6},
#     {'id': 14, 'parent': 5, 'shortcut': u'3D-Allgemein', 'template': 6},
#     {'id': 15, 'parent': 14, 'shortcut': u'Workflow', 'template': 6},
#     {'id': 16, 'parent': 14, 'shortcut': u'Einsatzgebiete-f-r-3D', 'template': 6},
#     {'id': 17, 'parent': 14, 'shortcut': u'Warum-3D', 'template': 6},
#     {'id': 18, 'parent': 12, 'shortcut': u'Produkteigenschaften', 'template': 6},
#     {'id': 19, 'parent': 12, 'shortcut': u'Modeling', 'template': 6},
#     {'id': 20, 'parent': 12, 'shortcut': u'Features', 'template': 6},
#     {'id': 21, 'parent': 5, 'shortcut': u'3D-Software', 'template': 6},
#     {'id': 22, 'parent': 21, 'shortcut': u'Cinema4D', 'template': 6},
#     {'id': 23, 'parent': 21, 'shortcut': u'Maya', 'template': 6},
#     {'id': 24, 'parent': 21, 'shortcut': u'Blender', 'template': 6},
#     {'id': 25, 'parent': 14, 'shortcut': u'Grenzen', 'template': 6},
#     {'id': 26, 'parent': 14, 'shortcut': u'Aufteilung', 'template': 6},
#     {'id': 27, 'parent': 1, 'shortcut': u'test-Pr-sentation', 'template': 6},
#     {'id': 28, 'parent': 27, 'shortcut': u'1', 'template': 6},
#     {'id': 29, 'parent': 28, 'shortcut': u'1-1', 'template': 6},
#     {'id': 30, 'parent': 28, 'shortcut': u'1-2', 'template': 6},
#     {'id': 31, 'parent': 27, 'shortcut': u'2', 'template': 6},
#     {'id': 32, 'parent': 31, 'shortcut': u'2-1', 'template': 6},
#     {'id': 33, 'parent': 31, 'shortcut': u'2-2', 'template': 6}
#    ]
#    pprint(data)
#    print "="*60
#    tree = TreeGenerator(data)
#    result = tree.get_group_list(group_key="template", id=30)
#    pprint(result)
