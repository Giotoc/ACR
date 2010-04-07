#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AsynCode Framework - XML framework allowing developing internet
# applications without using programming languages.
# Copyright (C) 2008-2010  Adrian Kalbarczyk

# This program is free software: you can redistribute it and/or modify
# it under the terms of the version 3 of GNU General Public License as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ACF.utils import replaceVars
from ACF import globals
from ACF.errors import *
import logging
import sys

log = logging.getLogger('ACF.component')

#dict of component modules
MODULE_CACHE={}

def get(name):
	"""
		Returns component of given name. Manages components cache.
	"""
	module=MODULE_CACHE.get(name,None)
	if module:
		return module
	path="ACF.components."+name
	try:
		__import__(path)
	except Error,e:
		raise e
		raise Error("ComponentNotFound",str(e))
	m=sys.modules[path]
	MODULE_CACHE[name]=m
	return m

#abstract class
class Component(object):
	def __init__(self, config):
		self.config=config

	def generate(self,env,conf):
		raise AbstractClass()

	def parseAction(self,root):
		return root
