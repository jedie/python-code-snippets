#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" Spytee2 - Simple PYthon TEmplate Engine

a modified Version of the Original SpyTee by Wensheng Wang:
http://www.pytan.com/code/spytee/


modified 10.2005 by Jens Diemer and renamed to spytee2

Changes:
-The Template is expected as a String.
-The Template returned as compiled, serialised byte code.
"""

__version__="2.2"

__history__="""
v2.2
    - changed variable placeholder from {variable} to ${variable}
    - with contribution from: Ian Meyer: conditional patch
v2.1
    - erste Version
"""

__author__  = "Jens Diemer"
__license__ = "GNU General Public License v2 or above"
__url__     = "http://jensdiemer.de/Programmieren/Python/SpyTee2"

import os, sys, marshal


class spytee2:
    """A simple python template engine:
    It take a text template file as input, process the tags and blocks in
    the file, and return the resulted text.  It will compile the input
    into a python program and store it in the cache location if the text is
    newer. On the next request of displaying the same file, it will not read the
    text file, instead it will execute the cached python program to save time.
    In the text template file: tags are enclosed by '{}' and blocks are denoted
    in html comment in the form of '<!-- BEGIN block_name -->' and '<!-- END -->'.
    Users use assign_vars and set_block_vars to specify the value of tag and block
    variables inside their python program.

    Note the BEGIN and END block will take whole line, anything else on the same
    line will be ignored.
    """
    def __init__ (self, template_string):
        """Constructor: language and theme arguments are useless for now.
        """
        self.template_string = template_string
        self.tpldata={}
        self.varlist=[]
        self.tab_dep=1
        self.cur_scope = ['']
        self.page=[]

    def assign_vars(self,dictvar):
        "update top-level var from an dict"
        if type(dictvar) == type({}):
            self.tpldata.update(dictvar)
        else:
            self.errors.append('Error in "assign_vars(%s)", assign_vars accepts only dict'%dictvar)

    def set_block_vars(self, blockname, bdict={}):
        "Assign key value pairs from an dict to a specified block "
        if not type(bdict) == type({}):
            self.errors.append('Error in "set_block_vars(%s)", last argument must be dict'%bdict)
            return

        blocks = blockname.split('.')

        #if not self.tpldata.has_key(blocks[0]):
        if blocks[0] not in self.tpldata:
            self.tpldata[blocks[0]] = []
        curr = self.tpldata[blocks[0]]

        for block in blocks[1:]:
            if not curr:
                curr.append({})
            curr = curr[-1]
            if block not in curr:
                curr[block] = []
            curr = curr[block]

        curr.append(dict(bdict))

    def _find_block(self, textline):
        """This is used to replace following regular expression:
        re.compile(r"<!--\s*BEGIN\s+([a-zA-Z0-9_\-]+)\s+-->")
        re.compile(r"<!--\s*END\s+([a-zA-Z0-9_\-]+)\s+-->")
        """
        block = textline[textline.find('<!--')+4:].lstrip()
        blocktail = block.find('-->')
        if blocktail == -1:
            return [0]
        if block[:5] == 'BEGIN':
            return [1,block[5:blocktail].lstrip().rstrip()]
        elif block[:3] == 'END':
            return [2,block[3:blocktail].lstrip().rstrip()]
        else:
            return [0]

    def _find_tags(self, textline):
        """This is to replace following regular expression:
        re.compile("\${[a-zA-Z0-9_\-\.]+\}")
        """
        tags = []
        remain = textline
        while remain:
            tagb = remain.find('${')
            tage = remain.find('}')
            if not tagb == -1 and tagb < tage:
                tags.append(remain[tagb:tage+1])
                remain=remain[tage+1:]
            else:
                remain = ''
        return tags

    def _find_conditional (self, text):
        """Find IF, ELIF, ELSE, ENDIF"""
        #should we provide 'AND' 'OR'?
        cond_beg = text[text.find('<!--')+4:].lstrip()
        cond_end = cond_beg.find('-->')

        if cond_end == -1:
            return [0]
        if cond_beg[:2] == "IF":
            return [1,cond_beg[2:cond_end].lstrip().rstrip()]
        elif cond_beg[:4] == "ELIF":
            return [2,cond_beg[4:cond_end].lstrip().rstrip()]
        elif cond_beg[:4] == "ELSE":
            return [3]
        elif cond_beg[:5] == "ENDIF":
            return [4]
        else:
            return [0]

     def _compile_var_tags(self, text_line):
        "Find and replace tags and blocks variables"
        curr_line = text_line

            #---------------------------------------------------------
        # Find conditionals
        var = self._find_conditional(curr_line)
        if var[0]:
            if var[0] == 1 or var[0] == 2:
                var_length = var[1].find(' ')
                if var_length == -1:
                    cond = ''
                    var_to_test = var[1]
                else:
                    var_to_test = var[1][:var_length]
                    #has EQ ,NE, LT, or GT
                    rest_of_conditional = var[1][var_length:].lstrip()
                    cond = rest_of_conditional.find(' ')
                    if cond == -1:
                        self.error_found = 1
                        return '\t'*self.tab_dep+'pass\n\tappend("Template Error:Wrong conditional syntax at line ' + str(self.lineno) + '")'
                    else:
                        value_to_test = rest_of_conditional[cond:].lstrip()
                        cond = rest_of_conditional[:cond]

                var_to_test = self._get_varname(var_to_test)
                if not var_to_test:
                    self.error_found = 1
                    return '\t'*self.tab_dep+'pass\n\tappend("Template Error:Not in this block :'+ v + " at line " + str(self.lineno) + '")'

                if not cond:
                    condition = var_to_test + ":"
                elif cond == "EQ":
                    #can be numeric or string, string must be quoted
                    condition = var_to_test + " == " + value_to_test + ":"
                elif cond == "NE":
                    condition = var_to_test + " != " + value_to_test + ":"
                elif cond == "LT":
                    condition = var_to_test + " < " + value_to_test + ":"
                elif cond == "GT":
                    condition = var_to_test + " and " + var_to_test + " > " + value_to_test + ":"
                else:
                    self.error_found = 1
                    return '\t'*self.tab_dep+'pass\n\tappend("Template Error:Not in this block :'+ v + " at line " + str(self.lineno) + '")'

                if var[0] == 1:
                    curr_line =  "\t" * self.tab_dep + "if " + condition
                    self.if_dep +=1
                else:
                    if self.if_dep == 0:
                        self.error_found = 1
                        return '\t'*self.tab_dep+'pass\n\tappend("Template Error:ELIF has no matching IF at line ' + str(self.lineno) + '")'
                    self.tab_dep -= 1
                    curr_line =  "\t" * self.tab_dep + "elif " + condition
                self.tab_dep = self.tab_dep + 1
            elif var[0] == 3:
                if self.if_dep == 0:
                    self.error_found = 1
                    return '\t'*self.tab_dep+'pass\n\tappend("Template Error:ELSE has no matching IF at line ' + str(self.lineno) + '")'
                self.tab_dep = self.tab_dep - 1
                curr_line = "\t" * self.tab_dep + "else:"
                self.tab_dep = self.tab_dep + 1
            elif var[0] == 4:
                if self.if_dep == 0:
                    self.error_found = 1
                    return '\t'*self.tab_dep+'pass\n\tappend("Template Error:ENDIF has no matching IF at line ' + str(self.lineno) + '")'
                self.tab_dep = self.tab_dep - 1
                self.if_dep -= 1
                if not self.tab_dep:
                    self.error_found = 1
                    self.tab_dep = 1
                    return '\tappend("Template Error: ENDIF has No matching IF at line %d")' % self.lineno
                curr_line = ''
            return curr_line

            #---------------------------------------------------------
        # Find block
        mstr = self._find_block(curr_line)
        if mstr[0]:
            if mstr[0] == 1:
                #--------------------------------
                # match <!-- BEGIN var --> block
                curr_line = ''
                blocks = mstr[1].split('.')
                curr_scope = self.tplscope
                if len(blocks)==1:
                    dictname = "tpldata"
                else:
                    for b in blocks[:-1]:
                        if b not in curr_scope:
                            return '\tappend("Template Error: No such parent block: %s at line %d")' % (b,self.lineno)
                        curr_scope = curr_scope[b]
                    dictname = "item_"+blocks[-2]
                curr_scope[blocks[-1]]={}

                curr_line = "\t" * self.tab_dep + "for item_" + blocks[-1] + " in " + dictname + ".get('" + blocks[-1] +"',[]):"
                self.tab_dep += 1

                return curr_line
            elif mstr[0] == 2:
                #-----------------------------
                # match <!-- END var --> block
                self.tab_dep -= 1
                if not self.tab_dep:
                    self.error_found = 1
                    self.tab_dep = 1
                    return '\tappend("Template Error: END has No matching BEGIN at line %d")' % self.lineno
                return ""

        #---------------------------------------------------------
        # match ${var} variable
        mstrs = self._find_tags(curr_line)
        varname=''
        for mstr in mstrs:
            if varname:
                varname+=','
            getname = self._get_varname(mstr)
            if not getname:
                self.error_found = 1
                return '\t'*self.tab_dep+'pass\n\tappend("Template Error:Not in this block :'+ v + " at line " + str(self.lineno) + '")'
            else:
                varname += getname

            curr_line = curr_line.replace(mstr, '%s')
        if mstrs:
            curr_line+="' %("+varname+"))"
        else:
            curr_line+="')"

        return curr_line

    #__________________________________________________________________________

    def _make_code(self):
        """
        Generiert aus dem Template Python-Code
        """
        template_code = 'def displayself(tpldata):\n'
        template_code += '\tpage=[]\n'
        lineno = 1
        self.error_found = 0
        for line in template_string.split("\n"):
            if self.error_found:
                break
            else:
                line=line.rstrip()
                #escape special chars
                line=line.replace("\\","\\\\").replace("'","\\'")
                tline = '\t'*self.tab_dep + "append('" + line
                tline=tline.replace('%','%%')
                template_py += self._compile_var_tags(tline)+'\n'
                self.lineno += 1
        template_code += '\treturn page\n'
        return template_code

    def compile(self):
        """
        Liefert serialisiertes python code objekt des Templates zurück
        """
        template_code = self._make_code()

        # Code compilieren zu einem "code object"
        template_code = compile(template_code, "<string>", 'exec')

        # "code object" Serialisieren und zurück geben
        return marshal.dumps(template_code)

    def exec_compiled_template(self, compiled_template):
        """
        Das serialisierte Template ausführen
        """
        exec marshal.loads(compiled_template)
        return "\n".join(displayself(self.tpldata))





if __name__ == '__main__':
    template_string = """<table border=0 cellpadding=0 cellspacing=0>
    <!-- BEGIN colorrow -->
    <tr><td width="10%">${colorrow.color}</td>
      <!-- BEGIN colorcol -->
      <td bgcolor="${colorcol.code}">&nbsp;</td>
      <!-- END -->
    </tr>
    <!-- END -->
    </table>"""

    t = spytee2(template_string)

    #~ # only Debug
    #~ print "-"*80
    #~ print "Sourcecode des kompilierten Templates:"
    #~ print "-"*80
    #~ print t._make_code()

    # Template compilieren
    compiled_code = t.compile()

    ##__________________________________________________________________________

    # Daten für das Template "einfügen"
    colors = {'yellow':'#ffff%(i)02x','green':'#%(i)02xff%(i)02x',\
        'purple':'#ff%(i)02xff','blue':'%(i)02x%(i)02xff'}
    for c in colors.keys():
        t.set_block_vars('colorrow',{'color':c})
        for i in range(0,255,100):
            t.set_block_vars('colorrow.colorcol',{'code':colors[c]%locals()})

    print "-"*80
    print "Ergebniss des Ausgeführen Template:"
    print "-"*80
    print t.exec_compiled_template(compiled_code)
    print "-"*80




