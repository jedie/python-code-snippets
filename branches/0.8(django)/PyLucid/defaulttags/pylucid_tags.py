
"""
Custom PyLucid Tags

to use this tags, the template must load it with: {% load pylucid_tags %}

_______________________________________________________________________________
copyright info:

recurse Tag is taken from the greenpeace custard project (GPL).
Matthew Savage wrote the recurse node.
https://svn.greenpeace.org/projects/custard/browser/production/trunk/melt/apps/custard/templatetags/customtags.py
https://svn.greenpeace.org/projects/custard/browser/production/trunk/melt/COPYING
"""

from django.conf import settings
from django.core.cache import cache

from django import template

from django.template import Node, NodeList, Template, Context, resolve_variable
from django.template import VariableDoesNotExist
from django.template import TemplateSyntaxError
from django.utils import translation

import re, os, array

register = template.Library()

class RecurseNode(Node):
    def __init__(self, filter_expr):#child_attr_name, starting_var_name, recurse_var_name):
        self.filter_expr = filter_expr
#        self.child_attr_name = child_attr_name
#        self.starting_var_name = starting_var_name
#        self.recurse_var_name = recurse_var_name

        self.start_instance_nodelist = NodeList([])
        self.start_children_nodelist = NodeList([])
        self.start_child_nodelist = NodeList([])
        self.end_child_nodelist = NodeList([])
        self.end_children_nodelist = NodeList([])
        self.end_instance_nodelist = NodeList([])

    def __repr__(self):
        return "<Recurse Node: recurse %s for each item in , starting at: %s>" % \
            (self.loop_var, self.child_collection_name, child_collection_name)

    def __iter__(self):
        for node in self.nodelist_loop:
            yield node

    def get_nodes_by_type(self, nodetype):
        nodes = []
        if isinstance(self, nodetype):
            nodes.append(self)
        nodes.extend(self.start_instance_nodelist.get_nodes_by_type(nodetype))
        nodes.extend(self.start_children_nodelist.get_nodes_by_type(nodetype))
        nodes.extend(self.start_child_nodelist.get_nodes_by_type(nodetype))
        nodes.extend(self.end_child_nodelist.get_nodes_by_type(nodetype))
        nodes.extend(self.end_children_nodelist.get_nodes_by_type(nodetype))
        nodes.extend(self.end_instance_nodelist.get_nodes_by_type(nodetype))
        return nodes

    def render(self, context):
        try:
#            base = resolve_variable_with_filters(self.starting_var_name, context)
            base = self.filter_expr.resolve(context)
        except VariableDoesNotExist:
            base = None
        if base is None:
            pass
        return self.render_block(base, context, 0, 0)

    def render_block(self, start_object, context, depth, childIndex):
        context[self.recurse_var_name] = start_object
        context["recurseloop"] = {"depth" : depth, "childindex" : childIndex}
        return_value = ""

        return_value += render_node_list(self.start_instance_nodelist, context)
        return_value += self.render_children(start_object, context, depth)
        return_value += render_node_list(self.end_instance_nodelist, context)

        return return_value


    def render_children(self, item, context, depth):
        return_value = ""
        values = resolve_variable(self.child_attr_name, item)

        if(len(values) > 0):
            return_value += render_node_list(self.start_children_nodelist, context)

            childIndex = 0
            for item in values:
                return_value += self.render_child(item, context, depth, childIndex)
                childIndex += 1

            return_value += render_node_list(self.end_children_nodelist, context)

        return return_value

    def render_child(self, item, context, depth, childIndex):
        return_value = ""
        return_value += render_node_list(self.start_child_nodelist, context)
        return_value += self.render_block(item, context, depth+1, childIndex)

        return_value += render_node_list(self.end_child_nodelist, context)

        return return_value

def render_node_list(node_list, context):
    return_value = ""
    for node in node_list:
        return_value += node.render(context)
    return return_value

def do_recurse(parser, token):
    "{% recurse through CHILDREN_ACCESSOR_NAME as ITEM_VARIABLE_NAME starting with BASE_VARIABLE %}{% endrecurse %}"
    node = get_empty_recurse_node(token)
    parse_child_blocks_into_recurse_node(node, parser)
    return node

def get_empty_recurse_node(token):
    regexp = re.compile(r"^recurse through (?P<child_attr_name>.*?) as (?P<recurse_var_name>.*?) starting with (?P<starting_var_name>[^ ]*?)$")

    matches = regexp.search(token.contents)
    if not matches:
        raise TemplateSyntaxError, "'recurse' statements should be in the format 'recurse through CHILD_ATTR_NAME as RECURSE_VAR_NAME starting with STARTING_VAR ': '%s'" % token.contents

    child_attr_name = matches.group("child_attr_name")
    starting_var_name = matches.group("starting_var_name")
    recurse_var_name = matches.group("recurse_var_name")

    node = RecurseNode(child_attr_name, starting_var_name, recurse_var_name)
    return node

def parse_child_blocks_into_recurse_node(node, parser):
    node.start_instance_nodelist = parse_and_delete_first_token(parser, ('ifhaschildren'))
    node.start_children_nodelist = parse_and_delete_first_token(parser, ('childblock'))
    node.start_child_nodelist = parse_and_delete_first_token(parser, ('nextrecursionblock'))
    node.end_child_nodelist = parse_and_delete_first_token(parser, ('endchildblock'))
    node.end_children_nodelist = parse_and_delete_first_token(parser, ('endifhaschildren'))
    node.end_instance_nodelist = parse_and_delete_first_token(parser, ('endrecurse'))

def parse_and_delete_first_token(parser, parse_to):
    node_list = parser.parse(parse_to)
    parser.delete_first_token()
    return node_list

# ---------------------------------------------

register.tag("recurse", do_recurse)



