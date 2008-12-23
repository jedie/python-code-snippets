# -*- coding: utf-8 -*-

"""
    unittest
    ~~~~~~~~
    
    unittest for data_eval.py and pyconfig.py
    
    :copyleft: 2008 by Jens Diemer, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import unittest
import tempfile

from pyconfig import PyConfig
from data_eval import data_eval, DataEvalError, UnsafeSourceError, \
                                                                EvalSyntaxError


class TestDataEval(unittest.TestCase):
    def assert_eval(self, data):
        data_string = repr(data)
        result = data_eval(data_string)
        #print data, type(data), result, type(result)
        self.assertEqual(result, data)

    def testNone(self):
        self.assert_eval(None)

    def testBool(self):
        self.assert_eval(True)
        self.assert_eval(False)
        self.assert_eval([True, False])

    def testConst(self):
        self.assert_eval(1)
        self.assert_eval(1.01)
        self.assert_eval("FooBar")
        self.assert_eval(u"FooBar")

    def testNegativeValues(self):
        self.assert_eval(-1)
        self.assert_eval(-2.02)

    def testTuple(self):
        self.assert_eval(())
        self.assert_eval((1,2))
        self.assert_eval(("1", u"2", None, True, False))

    def testList(self):
        self.assert_eval([])
        self.assert_eval([1,2,-3,-4.41])
        self.assert_eval(["foo", u"bar", None, True, False])

    def testDict(self):
        self.assert_eval({})
        self.assert_eval({1:2, "a":"b", u"c":"c", "d":-1, "e":-2.02})
        self.assert_eval({"foo":"bar", u"1": None, 1:True, 0:False})

    def testDate(self):
        from datetime import date
        self.assert_eval(date.today())
        self.assert_eval({"dt": date.today()})
        
    def testDatetime(self):
        from datetime import datetime, timedelta
        self.assert_eval(datetime.now())
        self.assert_eval({"dt": datetime.now()})
        self.assert_eval(timedelta(seconds=2))
        
    def testSets(self):
        self.assert_eval(set([1,2,3]))
        self.assert_eval(frozenset([4,5,6]))

    def testLineendings(self):
        data_eval("\r\n{\r\n'foo'\r\n:\r\n1\r\n}\r\n")
        data_eval("\r{\r'foo'\r:\r1\r}\r")

    def testNoString(self):
        self.assertRaises(DataEvalError, data_eval, 1)

    def testQuoteErr(self):
        self.assertRaises(UnsafeSourceError, data_eval, "a")
        self.assertRaises(DataEvalError, data_eval, "a")

    def testUnsupportedErr(self):
        self.assertRaises(UnsafeSourceError, data_eval, "a+2")
        self.assertRaises(UnsafeSourceError, data_eval, "eval()")
        self.assertRaises(DataEvalError, data_eval, "eval()")

    def testSyntaxError(self):
        self.assertRaises(EvalSyntaxError, data_eval, ":")
        self.assertRaises(EvalSyntaxError, data_eval, "import os")
        self.assertRaises(DataEvalError, data_eval, "import os")


#------------------------------------------------------------------------------


class TestPyConfig(unittest.TestCase):
    tempfilename = os.path.join(tempfile.gettempdir(), "PyConfigUnittest.txt")
    
    def _delete_tempfile(self):
        def exist():
            return os.path.isfile(self.tempfilename)
         
        if exist():
            os.remove(self.tempfilename)
            
        self.assertEqual(exist(), False)
       
    def setUp(self):
        self._delete_tempfile()
        
    def tearDown(self):
        self._delete_tempfile()
        
    def _get_pyconf(self, defaults={}):
        return PyConfig(
            filename=self.tempfilename, verbose=0, defaults=defaults
        )
    
    def test1(self):
        pc = self._get_pyconf()
        self.assertEqual(pc, {})
        pc.save()
        
        pc = self._get_pyconf()
        self.assertEqual(pc, {})
        pc["foo"] = "bar"
        pc.save()
        
        pc = self._get_pyconf()
        self.assertEqual(pc["foo"], "bar")
        
    def test2(self):
        pc = self._get_pyconf()
        self.assertEqual(pc, {})
        pc[1] = 1234567890
        pc.save()
        
        pc = self._get_pyconf()
        self.assertEqual(pc[1], 1234567890)
        
        pc[1] = 2
        pc.save()
        pc[2] = 3
        pc.save()
        
        pc = self._get_pyconf()
        self.assertEqual(pc[1], 2)
        self.assertEqual(pc[2], 3)
        
    def test_string_update(self):
        pc = self._get_pyconf({"Foo1":"bar1"})
        self.assertEqual(pc, {"Foo1":"bar1"})
        
        pc.string_update(dict_string="{'Foo2':'bar2'}")
        self.assertEqual(pc, {"Foo1":"bar1", "Foo2":"bar2"})
        
    def test_string_new(self):
        pc = self._get_pyconf({"Foo1":"bar1"})
        self.assertEqual(pc, {"Foo1":"bar1"})
        
        pc.string_new(dict_string="{'Foo2':'bar2'}")
        self.assertEqual(pc, {"Foo2":"bar2"})
        


if __name__ == '__main__':
    unittest.main()
