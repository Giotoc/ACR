#!/usr/bin/env python
from ACR.errors import Error

try:
	import json
except:
	try:
		import simplejson as json
	except:
		raise Error("JSONNotFound")

def loads(s,object_hook=None):
	if s.find("u'")!=-1:
		s=s.replace("u'","'")
	s=s.replace("'",'"')
	try:
		return json.loads(s,object_hook=object_hook)
	except ValueError,e:
		raise Error(str(e)+" "+s)

load=json.load
def dumps(s,default=None):
	return json.dumps(s,default=default, separators=(',',':'))
dump=json.dump
