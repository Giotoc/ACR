#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ACR.utils.interpreter import *
import readline

class FakeEnv(object):
	requestStorage={}
	doDebug=False

fakeEnv=FakeEnv()

print """AC Runtime BLSL Expression interactive shell
	This interpreter has one storage accessible through "rs" namespace.
	ctrl+c to exit.
"""
debug=True
try:
	while True:
		try:
			tree=make_tree(raw_input(">>> "))
			if debug:
				print tree.tree
			print tree.execute(fakeEnv)
		except Exception,e:
			print e
except KeyboardInterrupt:
	pass
#new line at the end forces command prompt to apear at left
print
