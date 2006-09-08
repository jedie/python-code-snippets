# -*- coding: utf-8 -*-
"""
    pocoo.pkg.highlight.lexers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Lexers for highlighting package.

    :copyright: 2006 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

#~ from pocoo.pkg.highlight.base import RegexLexer, \
from base import RegexLexer, \
     Text, Comment, Operator, Keyword, Name, String, Number


class PythonLexer(RegexLexer):
    name = "python"
    tokens = [
        (r'\s+', Text),
        (r'#.*?\n', Comment),
        (r'[]{}:(),.[]', Text),
        (r'\\\n', Text),
        (r'in\b|is\b|and\b|or\b|not\b|!=|==|[-+/*%=<>]', Operator),
        (r'(assert|break|class|continue|def|del|elif|else|except|exec|'
         r'finally|for|from|global|if|import|lambda|pass|print|raise|'
         r'return|try|while|yield)\b', Keyword),
        (r'@[a-zA-Z0-9.]+', Keyword.Decorator),
        (r'(?<!\.)(__import__|abs|apply|basestring|bool|buffer|callable|'
         r'chr|classmethod|cmp|coerce|compile|complex|delattr|dict|dir|'
         r'divmod|enumerate|eval|execfile|exit|file|filter|float|getattr|'
         r'globals|hasattr|hash|hex|id|input|int|intern|isinstance|'
         r'issubclass|iter|len|list|locals|long|map|max|min|object|oct|'
         r'open|ord|pow|property|range|raw_input|reduce|reload|repr|'
         r'round|setattr|slice|staticmethod|str|sum|super|tuple|type|'
         r'unichr|unicode|vars|xrange|zip)\b', Name.Builtin),
        (r'(?<!\.)(self|None|False|True)\b', Name.Builtin.Pseudokeyword),
        (r'[a-zA-Z_][a-zA-Z0-9_]*', Name),
        (r'[0-9]+', Number),
        (r'""".*?"""', String.Double),
        (r"'''.*?'''", String.Single),
        (r'"(\\\\|\\"|[^"])*"', String.Double),
        (r"'(\\\\|\\'|[^'])*'", String.Single),
    ]


class PHPLexer(RegexLexer):
    name = "php"
    tokens = [
        (r'\s+', Text),
        (r'#.*?\n', Comment),
        (r'//.*?\n', Comment),
        (r'/[*].*?[*]/', Comment),
        (r'[~!%^&*()+=|\[\]:;,.<>/?{}@-]', Text),
        ('('+'|'.join(('and','E_PARSE','old_function','E_ERROR','or','as','E_WARNING',
          'parent','eval','PHP_OS','break','exit','case','extends','PHP_VERSION',
          'cfunction','FALSE','print','class','for','require','continue','foreach',
          'require_once','declare','function','return','default','static','do',
          'switch','die','stdClass','echo','else','TRUE','elseif','var','empty','if',
          'xor','enddeclare','include','virtual','endfor','include_once','while',
          'endforeach','global','__FILE__','endif','list','__LINE__','endswitch',
          'new','__sleep','endwhile','not','__wakeup','E_ALL','NULL'))+r')\b', Keyword),
        ('(true|false|null)\b', Keyword.Constant),
        ('\$[a-zA-Z_][a-zA-Z0-9_]*', Name.Variable),
        ('[a-zA-Z_][a-zA-Z0-9_]*', Name.Other),
        (r"[0-9](\.[0-9]*)?(eE[+-][0-9])?[flFLdD]?|0[xX][0-9a-fA-F]+[Ll]?", Number),
        (r'"(\\\\|\\"|[^"])*"', String.Double),
        (r"'(\\\\|\\'|[^'])*'", String.Single),
    ]


class CppLexer(RegexLexer):
    name = "cplusplus"
    tokens = [
        (r'\s+', Text),
        (r'\\\n', Text),
        (r'//.*?\n', Comment),
        (r'/[*].*?[*]/', Comment),
        (r'(?<=\n)\s*#.*?(\n|(?=/[*]))', Comment.Preproc),
        (r'[~!%^&*()+=|\[\]:;,.<>/?-]', Text),
        (r'[{}]', Keyword),
        (r'"(\\\\|\\"|[^"])*"', String),
        (r"'\\.'|'[^\\]'", String.Char),
        (r"[0-9](\.[0-9]*)?(eE[+-][0-9])?[flFLdD]?|0[xX][0-9a-fA-F]+[Ll]?", Number),
        ('('+'|'.join(('struct','class','union','enum',
          'int','float','double','signed','unsigned','char','short','void','bool',
          'long','register','auto','operator',
          'static','const','private','public','protected','virtual','explicit',
          'new','delete','this',
          'if','else','while','for','do','switch','case','default','sizeof',
          'dynamic_cast','static_cast','const_cast','reinterpret_cast','typeid',
          'try','catch','throw','throws','return','continue','break','goto')) + r')\b',
         Keyword),
        ('('+'|'.join(('extern', 'volatile', 'typedef', 'friend',
                       '__declspec', 'inline','__asm','thread','naked',
                       'dllimport','dllexport','namespace','using',
                       'template','typename','goto')) + r')\b', Keyword.Reserved),
        (r'(true|false|NULL)\b', Keyword.Constant),
        (r'[a-zA-Z_][a-zA-Z0-9_]*', Name),
    ]
