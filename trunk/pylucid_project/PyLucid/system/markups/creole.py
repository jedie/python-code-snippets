# -*- coding: iso-8859-1 -*-
"""
    Creole wiki markup parser

    See http://wikicreole.org/ for latest specs.

    Notes:
    * No markup allowed in headings.
      Creole 1.0 does not require us to support this.
    * No markup allowed in table headings.
      Creole 1.0 does not require us to support this.
    * No (non-bracketed) generic url recognition: this is "mission impossible"
      except if you want to risk lots of false positives. Only known protocols
      are recognized.
    * We do not allow ":" before "//" italic markup to avoid urls with
      unrecognized schemes (like wtf://server/path) triggering italic rendering
      for the rest of the paragraph.

    PyLucid Updates by the PyLucid team:
        - Bugfixes and better html code style
        - Make the image tag match more strict, so it doesn't clash with
            django template tags
        - Add a passthrough for all django template blocktags
        - Add a passthrough for html code lines

    @copyright: 2007 MoinMoin:RadomirDopieralski (creole 0.5 implementation),
                2007 MoinMoin:ThomasWaldmann (updates)
                2008 PyLucid:JensDiemer (PyLucid patches)
    @license: GNU GPL, see COPYING for details.
"""

import re


class Rules:
    """Hold all the rules for generating regular expressions."""

    # For the inline elements:
    proto = r'http|https|ftp|nntp|news|mailto|telnet|file|irc'
    url =  r'''(?P<url>
            (^ | (?<=\s | [.,:;!?()/=]))
            (?P<escaped_url>~)?
            (?P<url_target> (?P<url_proto> %s ):\S+? )
            ($ | (?=\s | [,.:;!?()] (\s | $)))
        )''' % proto
    link = r'''(?P<link>
            \[\[
            (?P<link_target>.+?) \s*
            ([|] \s* (?P<link_text>.+?) \s*)?
            ]]
        )'''

#    link = r'''(?P<link1>
#            \[\[
#            (?P<link_target1>.+?)\|(?P<link_text1>.+?)
#            ]]
#        )|(?P<link2>
#            \[\[
#            (?P<link_target2> (%s)://[^ ]+) \s* (?P<link_text2>.+?)
#            ]]
#        )|
#            \[\[(?P<internal_link>.+)\]\]
#        ''' % proto

    #--------------------------------------------------------------------------
    # The image rule should not match on django template tags! So we make it
    # more restricted.
    # It matches only if...
    # ...image target ends with a picture extention
    # ...separator >|< and the image text exist
    image = r'''(?P<image>
            {{
            (?P<image_target>.+?\.jpg|\.jpeg|\.gif|\.png) \s*
            (\| \s* (?P<image_text>.+?) \s*)?
            }}
        )(?i)'''
    #--------------------------------------------------------------------------

    macro_block = r'''(?P<macro_block>
            \s* << (?P<macro_block_start>\w+) \s* (?P<macro_block_args>.*?) >>
            (?P<macro_block_text>(.|\n)+?)
            <</(?P=macro_block_start)>> \s*
        )'''
        
    macro = r'''(?P<macro>
            <<
            (?P<macro_name> \w+) (?P<macro_args>.*?)
            >>
        )'''
    code = r'(?P<code> {{{ (?P<code_text>.*?) }}} )'
    emph = r'(?P<emph> (?<!:)// )' # there must be no : in front of the //
                                   # avoids italic rendering in urls with
                                   # unknown protocols
    strong = r'(?P<strong> \*\* )'
    linebreak = r'(?P<linebreak> \\\\ )'
    escape = r'(?P<escape> ~ (?P<escaped_char>\S) )'
    char =  r'(?P<char> . )'

    # For the block elements:
    separator = r'(?P<separator> ^ \s* ---- \s* $ )' # horizontal line
    line = r'''(?P<line> ^\s*$ )''' # empty line that separates paragraphs
    head = r'''(?P<head>
            ^
            (?P<head_head>=+) \s*
            (?P<head_text> .*? )
            =*$
        )'''
    text = r'(?P<text> .+ ) (?P<break> (?<!\\)$\n(?!\s*$) )?'
    list = r'''(?P<list>
            ^ [ \t]* ([*][^*\#]|[\#][^\#*]).* $
            ( \n[ \t]* [*\#]+.* $ )*
        )''' # Matches the whole list, separate items are parsed later. The
             # list *must* start with a single bullet.
    item = r'''^ \s* (?P<item>
            (?P<item_head> [\#*]+) \s*
            (?P<item_text> .*?)
        ) \s* $''' # Matches single list items
    pre = r'''(?P<pre>
            ^{{{ \s* $
            (\n)?
            (?P<pre_text>
                ([\#]!(?P<pre_kind>\w*?)(\s+.*)?$)?
                (.|\n)+?
            )
            (\n)?
            ^}}} \s*$
        )'''
    pre_escape = r' ^(?P<indent>\s*) ~ (?P<rest> \}\}\} \s*) $'

    # Pass-through all django template blocktags       
    pass_block = r'''(?P<pass_block>
            {% \s* (?P<pass_block_start>.+?) \s* (?P<pass_block_args>.*?) \s* %}
            (\n|.)*?
            {% \s* end(?P=pass_block_start) \s* %}
        )'''
        
    pass_line = r'''\n(?P<pass_line>
            (\n|\s)*
            ({%.*?%})|
            ({{.*?}})
            (\n|\s)*
        )'''
    pass_inline = r'''(?P<pass_inline>
            ({%.*?%})|
            ({{.*?}})
        )'''
        
    #Pass-through html code lines
    html = r'''(?P<html>
            ^[ \t]*<[a-zA-Z].*?<(/[a-zA-Z ]+?)>[ \t]*$
        )'''

    table = r'''^ \s*(?P<table>
            [|].*? \s*
            [|]?
        ) \s* $'''

    # For splitting table cells:
    cell = r'''
            \| \s*
            (
                (?P<head> [=][^|]+ ) |
                (?P<cell> (  %s | [^|])+ )
            ) \s*
        ''' % '|'.join([link, macro, image, code])

    #--------------------------------------------------------------------------
#    blockelements = (
#        "head", "list", "pre", "code", "table", "separator", "macro",
#        "pass_block", "pass_line", "html"
#    )

class Parser:
    """
    Parse the raw text and create a document object
    that can be converted into output using Emitter.
    """
    # For pre escaping, in creole 1.0 done with ~:
    pre_escape_re = re.compile(Rules.pre_escape, re.M | re.X)
    # for link descriptions:
    link_re = re.compile(
        '|'.join([Rules.image, Rules.linebreak, Rules.char]),
        re.X | re.U
    )
    item_re = re.compile(Rules.item, re.X | re.U | re.M) # for list items
    cell_re = re.compile(Rules.cell, re.X | re.U) # for table cells
    # For block elements:
    block_re = re.compile(
        '|'.join([
            Rules.pass_block,
            Rules.pass_line,
            Rules.macro_block,
            Rules.html,
            Rules.line, Rules.head, Rules.separator, Rules.pre, Rules.list,
            Rules.table, Rules.text,
        ]),
        re.X | re.U | re.M
    )
    # For inline elements:
    inline_re = re.compile(
        '|'.join([
            Rules.link, Rules.url, Rules.macro,
            Rules.code, Rules.image,
            Rules.pass_inline,
            Rules.strong, Rules.emph, Rules.linebreak,
            Rules.escape, Rules.char
        ]),
        re.X | re.U
    )

    def __init__(self, raw):
        self.raw = raw
        self.root = DocNode('document', None)
        self.cur = self.root        # The most recent document node
        self.text = None            # The node to add inline characters to
        self.last_text_break = None # Last break node, inserted by _text_repl()

    #--------------------------------------------------------------------------

    def cleanup_break(self, old_cur):
        """
        remove unused end line breaks.
        Should be called before a new block element.
        e.g.:
          <p>line one<br />
          line two<br />     <--- remove this br-tag
          </p>
        """
        if self.cur.children:
            last_child = self.cur.children[-1]
            if last_child.kind == "break":
                del(self.cur.children[-1])

    def _upto(self, node, kinds):
        """
        Look up the tree to the first occurence
        of one of the listed kinds of nodes or root.
        Start at the node node.
        """
        self.cleanup_break(node) # remove unused end line breaks.
        while node.parent is not None and not node.kind in kinds:
            node = node.parent
        
        return node

    def _upto_block(self):
        self.cur = self._upto(self.cur, ('document',))# 'section', 'blockquote'))

    #__________________________________________________________________________
    # The _*_repl methods called for matches in regexps. Sometimes the
    # same method needs several names, because of group names in regexps.

    def _pass_block_repl(self, groups):
        """ Pass-through all django template blocktags """          
        self._upto_block()
        self.cur = self.root
        DocNode("pass_block", self.cur, groups["pass_block"])
        self.text = None
    _pass_block_start_repl = _pass_block_repl
    _pass_block_end_repl = _pass_block_repl

    def _pass_line_repl(self, groups):
        """ Pass-through all django tags witch is alone in a code line """
        self._upto_block()
        self.cur = self.root
        DocNode("pass_line", self.cur, groups["pass_line"])
        self.text = None
        
    def _pass_inline_repl(self, groups):
        """ Pass-through all inline django tags"""
        DocNode("pass_inline", self.cur, groups["pass_inline"])
        self.text = None

    def _html_repl(self, groups):
        """ Pass-through html code """
        self._upto_block()
        DocNode("html", self.root, groups["html"])
        self.text = None

    def _text_repl(self, groups):
#        print "_text_repl()", self.cur.kind, groups.get('break') != None
        if self.cur.kind in ('table', 'table_row', 'bullet_list',
                                                                'number_list'):
            self._upto_block()

        if self.cur.kind in ('document', 'section', 'blockquote'):
            self.cur = DocNode('paragraph', self.cur)

        self.parse_inline(groups.get('text', u""))

        if groups.get('break') and self.cur.kind in ('paragraph',
            'emphasis', 'strong', 'code'):
            self.last_text_break = DocNode('break', self.cur, u"")

        self.text = None
    _break_repl = _text_repl

    def _url_repl(self, groups):
        """Handle raw urls in text."""
        if not groups.get('escaped_url'):
            # this url is NOT escaped
            target = groups.get('url_target', u"")
            node = DocNode('link', self.cur)
            node.content = target
            DocNode('text', node, node.content)
            self.text = None
        else:
            # this url is escaped, we render it as text
            if self.text is None:
                self.text = DocNode('text', self.cur, u"")
            self.text.content += groups.get('url_target')
    _url_target_repl = _url_repl
    _url_proto_repl = _url_repl
    _escaped_url = _url_repl

    def _link_repl(self, groups):
        """Handle all kinds of links."""
        target = groups.get('link_target', u"")
        text = (groups.get('link_text', u"") or u"").strip()
        parent = self.cur
        self.cur = DocNode('link', self.cur)
        self.cur.content = target
        self.text = None
        re.sub(self.link_re, self._replace, text)
        self.cur = parent
        self.text = None
    _link_target_repl = _link_repl
    _link_text_repl = _link_repl

    def _add_macro(self, macro_name, macro_args, macro_text=u""):
#        self._upto_block()
        node = DocNode("macro", self.cur, macro_text.strip())
        node.macro_name = macro_name
        node.macro_args = macro_args.strip()
        self.text = None

    def _macro_block_repl(self, groups):
        """Handles macros using the placeholder syntax."""
        #self.debug_groups(groups)
        self._upto_block()
        self.cur = self.root
        self._add_macro(
            macro_name = groups['macro_block_start'],
            macro_text = groups.get('macro_block_text', u""),
            macro_args = groups.get('macro_block_args', u""),
        )
        self.text = None
    _macro_block_start_repl = _macro_block_repl
    _macro_block_args_repl = _macro_block_repl
    _macro_block_text_repl = _macro_block_repl

    def _macro_repl(self, groups):
        """Handles macros using the placeholder syntax."""
        macro_name = groups.get('macro_name', u"")
        macro_args = groups.get('macro_args', u"")
        self._add_macro(macro_name, macro_args)
        self.text = None

#        text = (groups.get('macro_text', u"") or u"").strip()
#        node = DocNode('macro', self.cur, name)
#        node.args = groups.get('macro_args', u"") or ''
#        DocNode('text', node, text or name)
#        self.text = None
    _macro_name_repl = _macro_repl
    _macro_args_repl = _macro_repl
#    _macro_text_repl = _macro_repl

    def _image_repl(self, groups):
        """Handles images and attachemnts included in the page."""
        target = groups.get('image_target', u"").strip()
        text = (groups.get('image_text', u"") or u"").strip()
        node = DocNode("image", self.cur, target)
        DocNode('text', node, text or node.content)
        self.text = None
    _image_target_repl = _image_repl
    _image_text_repl = _image_repl

    def _separator_repl(self, groups):
        self._upto_block()
        DocNode('separator', self.cur)

    def _item_repl(self, groups):
        bullet = groups.get('item_head', u"")
        text = groups.get('item_text', u"")
        if bullet[-1] == '#':
            kind = 'number_list'
        else:
            kind = 'bullet_list'
        level = len(bullet)-1
        lst = self.cur
        # Find a list of the same kind and level up the tree
        while (lst and
                   not (lst.kind in ('number_list', 'bullet_list') and
                        lst.level == level) and
                    not lst.kind in ('document', 'section', 'blockquote')):
            lst = lst.parent
        if lst and lst.kind == kind:
            self.cur = lst
        else:
            # Create a new level of list
            self.cur = self._upto(self.cur,
                ('list_item', 'document', 'section', 'blockquote'))
            self.cur = DocNode(kind, self.cur)
            self.cur.level = level
        self.cur = DocNode('list_item', self.cur)
        self.cur.level = level+1
        self.parse_inline(text)
        self.text = None
    _item_text_repl = _item_repl
    _item_head_repl = _item_repl

    def _list_repl(self, groups):
        self.item_re.sub(self._replace, groups["list"])

    def _head_repl(self, groups):
        self._upto_block()
        node = DocNode('header', self.cur, groups['head_text'].strip())
        node.level = len(groups['head_head'])
        self.text = None
    _head_head_repl = _head_repl
    _head_text_repl = _head_repl

    def _table_repl(self, groups):
        row = groups.get('table', '|').strip()
        self.cur = self._upto(self.cur, (
            'table', 'document', 'section', 'blockquote'))
        if self.cur.kind != 'table':
            self.cur = DocNode('table', self.cur)
        tb = self.cur
        tr = DocNode('table_row', tb)

        for m in self.cell_re.finditer(row):
            cell = m.group('cell')
            if cell:
                text = cell.strip()
                self.cur = DocNode('table_cell', tr)
                self.text = None
            else:
                text = m.group('head').strip('= ')
                self.cur = DocNode('table_head', tr)
                self.text = DocNode('text', self.cur, u"")
            self.parse_inline(text)

        self.cur = tb
        self.text = None

    def _pre_repl(self, groups):
        self._upto_block()
        kind = groups.get('pre_kind', None)
        text = groups.get('pre_text', u"")
        def remove_tilde(m):
            return m.group('indent') + m.group('rest')
        text = self.pre_escape_re.sub(remove_tilde, text)
        node = DocNode('preformatted', self.cur, text)
        node.sect = kind or ''
        self.text = None
    _pre_text_repl = _pre_repl
    _pre_head_repl = _pre_repl
    _pre_kind_repl = _pre_repl

    def _line_repl(self, groups):
        """ Transfer newline from the original markup into the html code """
        self._upto_block()
        DocNode('line', self.cur, u"")

    def _code_repl(self, groups):
        DocNode('code', self.cur, groups.get('code_text', u"").strip())
        self.text = None
    _code_text_repl = _code_repl
    _code_head_repl = _code_repl

    def _emph_repl(self, groups):
        if self.cur.kind != 'emphasis':
            self.cur = DocNode('emphasis', self.cur)
        else:
            self.cur = self._upto(self.cur, ('emphasis', )).parent
        self.text = None

    def _strong_repl(self, groups):
        if self.cur.kind != 'strong':
            self.cur = DocNode('strong', self.cur)
        else:
            self.cur = self._upto(self.cur, ('strong', )).parent
        self.text = None

    def _linebreak_repl(self, groups):
        DocNode('break', self.cur, None)
        self.text = None

    def _escape_repl(self, groups):
        if self.text is None:
            self.text = DocNode('text', self.cur, u"")
        self.text.content += groups.get('escaped_char', u"")

    def _char_repl(self, groups):
        if self.text is None:
            self.text = DocNode('text', self.cur, u"")
        self.text.content += groups.get('char', u"")

    #--------------------------------------------------------------------------

    def _replace(self, match):
        """Invoke appropriate _*_repl method. Called for every matched group."""
        groups = match.groupdict()
        for name, text in groups.iteritems():
            if text is not None:
                #if name != "char": print "%15s: %r" % (name, text)
                #print "%15s: %r" % (name, text)
                replace = getattr(self, '_%s_repl' % name)
                replace(groups)
                return

    def parse_inline(self, raw):
        """Recognize inline elements inside blocks."""
        re.sub(self.inline_re, self._replace, raw)

    def parse_block(self, raw):
        """Recognize block elements."""
        re.sub(self.block_re, self._replace, raw)

    def parse(self):
        """Parse the text given as self.raw and return DOM tree."""
        self.parse_block(self.raw)
        return self.root


    #--------------------------------------------------------------------------
    def debug(self, start_node=None):
        """
        Display the current document tree
        """
        print "_"*80
                
        if start_node == None:
            start_node = self.root
            print "  document tree:"
        else:
            print "  tree from %s:" % start_node
            
        print "="*80
        def emit(node, ident=0):
            for child in node.children:
                print u"%s%s: %r" % (u" "*ident, child.kind, child.content)
                emit(child, ident+4)
        emit(start_node)
        print "*"*80

    def debug_groups(self, groups):
        print "_"*80
        print "  debug groups:"
        for name, text in groups.iteritems():
            if text is not None:
                print "%15s: %r" % (name, text)
        print "-"*80



#------------------------------------------------------------------------------


class DocNode:
    """
    A node in the document.
    """
    def __init__(self, kind='', parent=None, content=None):
        self.children = []
        self.parent = parent
        self.kind = kind

        if content:
            content = unicode(content)
        self.content = content

        if self.parent is not None:
            self.parent.children.append(self)

    def __str__(self):
#        return "DocNode kind '%s', content: %r" % (self.kind, self.content)
        return "<DocNode %s: %r>" % (self.kind, self.content)
    def __repr__(self):
        return u"<DocNode %s: %r>" % (self.kind, self.content)

    def debug(self):
        print "_"*80
        print "\tDocNode - debug:"
        print "str(): %s" % self
        print "attributes:"
        for i in dir(self):
            if i.startswith("_"):
                continue
            print "%20s: %r" % (i, getattr(self, i, "---"))


#------------------------------------------------------------------------------


if __name__=="__main__":
    txt = r"""== a headline

Here is [[a internal]] link.
This is [[http://domain.tld|external links]].
A [[internal links|different]] link name.

Basics: **bold** or //italic//
or **//both//** or //**both**//
Force\\linebreak.

The current page name: >{{ PAGE.name }}< great?
A {% lucidTag page_update_list count=10 %} PyLucid plugin

{% sourcecode py %}
import sys

sys.stdout("Hello World!")
{% endsourcecode %}

A [[www.domain.tld|link]].
a {{/image.jpg|My Image}} image

no image: {{ foo|bar }}!
picture [[www.domain.tld | {{ foo.JPG | Foo }} ]] as a link

END

==== Headline 1

{% a tag 1 %}

==== Headline 2

{% a tag 2 %}

the end
"""

    txt = r"""
==== Headline 1

The current page name: >{{ PAGE.name }}< great?

{% a tag 1 %}

==== Headline 2

{% a tag 2 %}

some text

{% something arg1="foo" arg2="bar" arg2=3 %}
foobar
{% endsomething %}

the end
"""

    txt = r"""A {% lucidTag page_update_list count=10 %} PyLucid plugin

{% sourcecode py %}
import sys

sys.stdout("Hello World!")
{% endsourcecode %}
A [[www.domain.tld|link]]."""

    txt = r"""
==== Headline 1

On {% a tag 1 %} line
line two

==== Headline 2

{% a tag 2 %}

A block:
{% block %}
<Foo:> {{ Bar }}
{% endblock %}
end block

{% block1 arg="jo" %}
eofjwqp
{% endblock1 %}

A block without the right end block:
{% block1 %}
111
{% endblock2 %}
BBB

A block without endblock:
{% block3 %}
222
{% block3 %}
CCC

the end"""
#    txt = r'''
#<<jojo>>
#owrej
#<<code>>
#some code
#<</code>>
#a macro:
#<<code ext=.css>>
#/* Stylesheet */
#form * {
#  vertical-align:middle;
#}
#<</code>>
#the end
#<<code>>
#<<code>>
#jup
#<</code>>
#'''


    print "-"*80
    p = Parser(txt)
    document = p.parse()
    p.debug()
    
    def test_rules(rules, txt):
        def display_match(match):
            groups = match.groupdict()
            for name, text in groups.iteritems():
                if name != "char" and text != None:
                    print "%13s: %r" % (name, text)
        re.sub(rules, display_match, txt)

#    print "_"*80
#    print "plain block rules match:"
#    test_rules(Parser("").block_re, txt)
#
#    print "_"*80
#    print "plain inline rules match:"
#    test_rules(Parser("").inline_re, txt)

    print "---END---"