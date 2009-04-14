#!/usr/bin/env python2.5
"""Attempt to parse "For Translators:" docstrings from a Python file
This is currently incomplete, but "almost" there:

Given the following in file f.py :

"For Translators: some useful info about the sentence below"
_("Some string blah blah")

print "hi"
def blah(self):
    "For Translators: Hello again"
    pass

"For Translators: Goodbye"
print "hi again"

This script currently produces:

[line 3] For Translators: some useful info about the sentence below
[line 8] For Translators: Hello again

"""

import re
import compiler

def getLineNo(s):
    """"Recurses into first bit of list until we can get a line number
    Kind of horrible, but it works"""
    if s.lineno is None:
        return getLineNo(s.asList()[0])
    else:
        return s.lineno

def parse(mod):
    docstring = None
    for s in mod:
        if isinstance(s, basestring):
            # a simple string
            if s.startswith("For Translators:"):
                docstring = s
                continue
        elif isinstance(s, compiler.ast.Const):
            # a Const()
            cur_string = s.value
            if cur_string.startswith("For Translators:"):
                docstring = cur_string
                continue
        
        if docstring is not None:
            # We found a docstring, then statement, 
            print "[line %s] %s" % (
                getLineNo(s),
                docstring
            )
            docstring = None

        if s.__class__ in [getattr(compiler.ast, x) for x in dir(compiler.ast)]:
            for sub_s in s.asList():
                if sub_s is not None:
                    parse(sub_s)
    


def main():
    mod = compiler.parseFile("f.py")
    parse(mod)

if __name__ == '__main__':
    main()
