#!/usr/bin/env python
# coding: utf-8

"""
    simple unittest for 'git_date_filter.py'
    
    more info in README:
    https://github.com/jedie/python-code-snippets/tree/master/CodeSnippets/git/#readme
    
    :copyleft: 2012 by Jens Diemer
    :license: GNU GPL v3 or above
    :homepage: https://github.com/jedie/python-code-snippets/tree/master/CodeSnippets/git/
"""

import subprocess
import re
import unittest

SMUDGE_DATE_PREFIX = "$date:"
DATE_REGEX = re.compile(r"\$date:(.*?)\$")

EXAMPLE_CONTENT = """# coding: utf-8

__version__ = (1, 2, 3)
COMMITTER_DATE = "$date$" # will be set via git keyword Expansion

# end
"""



class TestGitFilter(unittest.TestCase):

    def test(self):
        p = subprocess.Popen(["python", "git_date_filter.py", "smudge"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        smudge_content = p.communicate(input=EXAMPLE_CONTENT)[0]
#        print "_"*79
#        print " *** smudge content: ***\n"
#        print smudge_content
        self.assertNotEqual(smudge_content, EXAMPLE_CONTENT)

        test = DATE_REGEX.findall(smudge_content)[0]
        self.assertTrue(test.isdigit(), "%r is is not a number!" % test)

        p = subprocess.Popen(["python", "git_date_filter.py", "clean"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        clean_content = p.communicate(input=smudge_content)[0]
#        print "_"*79
#        print " *** clean content: ***\n"
#        print clean_content

        self.assertEqual(clean_content, EXAMPLE_CONTENT)


if __name__ == '__main__':
    unittest.main()


