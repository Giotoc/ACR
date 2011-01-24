#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Asyncode Runtime - XML framework allowing developing internet
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.#@marcin: docstrings
from ACR.utils.generations import *

def get(d,path,falseOnNotFound=True):
	"""
	Returns value from dict/object hierarchy.
	input: dict, path which is a list eg ['an', 'example', 'path'],
	returns: False or deepest dict/object found
	"""
	#if isinstance(d, Generation):
	#	d=d.__dict__
	try:
		ret=d
		i=0
		for o in path:
			#if isinstance(ret, Generation):
			#	ret=ret.__dict__
			if o[0]=="@":
				ret=getattr(ret, o[1:])
				break
			else:
				ret=ret[o]
				i+=1
	except (AttributeError, KeyError, TypeError):
		if falseOnNotFound:
			return False
		return (ret,i)
	if falseOnNotFound:
		return ret
	return (ret, i)

# TODO add param for overwriting
def set(d, path, o):
	"""
	Inserts object o into dict d.
	input: dict, path which is a list eg ['an', 'example', 'path'], object might be inserted into d
	returns: None
	"""
	for key in path[:-1]:
		if not d.has_key(key) or type(d[key]) is not dict:
			d[key]={}
		d=d[key]
	d[path[-1]]=o
