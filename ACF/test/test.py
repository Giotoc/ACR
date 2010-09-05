#!/usr/bin/env python


import ACF.test.test_utils___init__
import ACF.test.test_utils_interpreter
import ACF.test.test_utils_objecttree

def doTests():
	print "Started running tests.\n"
	ACF.test.test_utils___init__.doTests()
	ACF.test.test_utils_interpreter.doTests()
	ACF.test.test_utils_objecttree.doTests()
	print "Ended running tests."