#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys


text = """
#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pocoo_highlight.lexers import PythonLexer

print True, None

l = PythonLexer(ctx = None)

help(l)

print l.get_tokens(text)
"""


from lexers import PythonLexer
from styles import SimpleHighlightingStyle
from base import highlight

style = SimpleHighlightingStyle()
#~ help(style);sys.exit()
lexer = PythonLexer(ctx = None)
#~ help(lexer)

tokens = lexer.get_tokens(text)
print highlight(tokens, style)

for token in tokens:
    token_type, txt = token
    print highlight(token, style)
    #~ print token_type, style.get_style_for(token_type)
    #~ sys.stdout.write(txt)