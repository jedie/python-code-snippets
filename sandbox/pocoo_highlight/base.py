# -*- coding: utf-8 -*-
"""
    pocoo.pkg.highlight.base
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Pocoo source highlighting engine.

    :copyright: 2006 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

import re

#~ from pocoo.pkg.core.bbcode import BBCodeTagProvider, escape_html
import cgi
escape_html = cgi.escape

# TODO: document TokenType

class TokenType(tuple):
    def __getattr__(self, val):
        return TokenType(self + (val,))

Token     = TokenType()

# Special token types
Text      = Token.Text
Error     = Token.Error

# Common token types
Keyword   = Token.Keyword
Name      = Token.Name
Literal   = Token.Literal
String    = Literal.String
Number    = Literal.Number
Operator  = Token.Operator
Comment   = Token.Comment
Other     = Token.Other


class HighlightingStyle(object):
    """
    Defines styles used by the highlighting engine.
    """

    # Name of this style.
    name = ""

    def get_style_for(self, tokentype):
        """
        Return the style information for a token type.
        Return None if no style defined for this token type.
        """


class HighlightingLexer(object):
    """
    Lexer for a specific language.
    """

    # Name of the language this lexer handles. Must be
    # short and should contain only alphanumeric characters.
    name = ""

    def get_tokens(self, text):
        """
        Yield (tokentype, value) pairs generated from ``text``.
        """
        yield None


class RegexLexer(HighlightingLexer):
    """
    Mixin for HighlightingLexer components.
    Simplifies the lexing process so that you need only
    provide a list of regular expressions.
    """

    comptype = HighlightingLexer
    name = ""

    # List of (regex, tokentype) pairs.
    tokens = []

    def __init__(self, ctx):
        self._tokens = [(re.compile(regex, re.DOTALL), ttype)
                        for (regex, ttype) in self.tokens]
        super(RegexLexer, self).__init__(ctx)

    def get_tokens(self, text):
        length = len(text)
        pos = 0
        while pos < length:
            for rex, ttype in self._tokens:
                m = rex.match(text, pos)
                if m:
                    yield ttype, m.group()
                    pos = m.end()
                    break
            else:
                yield Error, text[pos]
                pos += 1


def highlight(tokensource, style):
    """
    Return highlighted HTML for the token source.
    """

    res = []
    for ttype, value in tokensource:
        htmlvalue = escape_html(value)
        if ttype == Text:
            res.append(htmlvalue)
            continue
        spanstyle = style.get_style_for(ttype)
        while spanstyle is None:
            ttype = ttype[:-1]
            if ttype == ():
                spanstyle = ""
            else:
                spanstyle = style.get_style_for(ttype)
        if spanstyle == "":
            res.append(htmlvalue)
        else:
            res.append('<span style="%s">%s</span>' %
                       (spanstyle, htmlvalue))
    return ''.join(res)


