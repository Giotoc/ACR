#!/usr/bin/env python
# -*- coding: utf-8 -*-

#returns value from dict hierarchy based on "a.b.c" paths
# path is a list eg ['an', 'example', 'path']
def getObject(obj,path,exception=True):
	try:
		ret=obj
		i=0
		for o in path:
			ret=ret[o]
			i+=1
	except (AttributeError, KeyError, TypeError):
		#if D: log.warning("%s",e)
		if exception:
			return False
		return (ret,i)
	if exception:
		return ret
	return (ret, i)

# inserts object o into obj, path is a list , like above
def setObject(obj, path, o):
	try:
		d = obj
		for s in path[:-1]:
			if not d.has_key(s):
				d[s] = {}
			d = d[s]
		d[path[-1]] = o
	except:
		return False
	return o