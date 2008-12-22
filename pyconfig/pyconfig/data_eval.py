# -*- coding: utf-8 -*-

"""
    Data eval
    ~~~~~~~~~

    Evaluate a Python expression string, but only Python data type objects:
        - Constants, Dicts, Lists, Tuples
        - from datetime: datetime and timedelta

    Error class hierarchy:

        DataEvalError
         +-- EvalSyntaxError (compiler SyntaxError)
         +-- UnsafeSourceError (errors from the AST walker)

    Note
    ~~~~
    Based on "Safe" Eval by Michael Spencer
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/364469

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author: JensDiemer $

    :copyleft: 2008 by Jens Diemer, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import compiler


# For visitName()
NAME_MAP = {
    "None": None,
    "True": True, "False": False,
    "set": set, "frozenset": frozenset
}

# For visitGetattr(): key is the callable name and value is the module name
ALLOWED_CALLABLES = {
    "datetime" : "datetime",
    "timedelta": "datetime",
}


class SafeEval(object):
    """
    walk to compiler AST objects and evaluate only data type objects. If other
    objects found, raised a UnsafeSourceError
    """
    def visit(self, node, **kw):
        node_type = node.__class__.__name__
        method_name = "visit" + node_type
        method = getattr(self, method_name, self.unsupported)
        result = method(node, **kw)
        return result

    def visitExpression(self, node, **kw):
        for child in node.getChildNodes():
            return self.visit(child, **kw)

    #_________________________________________________________________________
    # Errors

    def unsupported(self, node, **kw):
        raise UnsafeSourceError(
            "Unsupported source construct", node.__class__, node
        )

    def visitName(self, node, **kw):
        if node.name in NAME_MAP:
            return NAME_MAP[node.name]

        raise UnsafeSourceError(
            "Strings must be quoted", node.name, node
        )

    #_________________________________________________________________________
    # supported nodes

    def visitConst(self, node, **kw):
        return node.value

    def visitUnarySub(self, node, **kw):
        """ Algebraic negative number """
        node = node.asList()[0]
        number = self.visitConst(node)
        return - number # return the negative number

    def visitDict(self, node, **kw):
        return dict([(self.visit(k),self.visit(v)) for k,v in node.items])

    def visitTuple(self, node, **kw):
        return tuple(self.visit(i) for i in node.nodes)

    def visitList(self, node, **kw):
        return [self.visit(i) for i in node.nodes]

    #_________________________________________________________________________
    # ALLOWED_CALLABLES nodes

    def visitGetattr(self, node, **kw):
        """
        returns the callable object, if its in ALLOWED_CALLABLES.
        """
        attrname = node.attrname
        try:
            callable_name = ALLOWED_CALLABLES[attrname]
        except KeyError:
            raise UnsafeSourceError("Callable not allowed.", attrname, node)

        module = __import__(callable_name, fromlist=[attrname])
        callable = getattr(module, attrname)

        return callable

    def visitCallFunc(self, node, **kw):
        """
        For e.g. datetime and timedelta
        """
        child_node = node.asList()[0]
        callable = self.visit(child_node)
        args = [self.visit(i) for i in node.args]
        return callable(*args)


def data_eval(source):
    """
    Compile the given source string to AST objects and evaluate only data
    type objects.
    """
    if not isinstance(source, basestring):
        raise DataEvalError("source must be string/unicode!")
    source = source.replace("\r\n", "\n").replace("\r", "\n")

    try:
        ast = compiler.parse(source, "eval")
    except SyntaxError, e:
        raise EvalSyntaxError(e)

    return SafeEval().visit(ast)


#_____________________________________________________________________________
# ERROR CLASS

class DataEvalError(Exception):
    """ main error class for all data eval errors """
    pass

class EvalSyntaxError(DataEvalError):
    """ compile raised a SyntaxError"""
    pass

class UnsafeSourceError(DataEvalError):
    """ Error class for the SafeEval AST walker """
    def __init__(self, error, descr = None, node = None):
        self.error = error
        self.descr = descr
        self.node = node
        self.lineno = getattr(node, "lineno", None)

    def __repr__(self):
        return "%s in line %d: '%s'" % (self.error, self.lineno, self.descr)

    __str__ = __repr__
