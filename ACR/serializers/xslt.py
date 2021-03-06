#!/usr/bin/env python
from ACR.utils.xmlextras import tree2xml
from ACR.errors import Error
import os
#TODO change it to AC CRITICAL error.
try:
	import libxml2
	import libxslt
except:
	raise Error("libxsltError","libxslt not installed")

XSLTCache={}
name="ObjectML+libxslt"
def transform(xml,xslt,forceReload=True):
	try:
		doc=libxml2.parseDoc(xml)
	except Exception,e:
		return "XML parsing Error."
	if forceReload or not XSLTCache.has_key(xslt):
		try:
			#TODO implement checking for change of *ALL* xslt files
			XSLTCache[xslt]=libxslt.parseStylesheetFile(xslt)
	#		raise str(dir(acconfig.XSLTCache))
		except Exception,e:
			return "XSLT parsing Error: %s"%e
	r=XSLTCache[xslt].applyStylesheet(doc, None)
	ret=r.serialize()
	doc.freeDoc()
	r.freeDoc()
	return ret

def serialize(env):
	xml=tree2xml(env.generations)
	if env.output["XSLTFile"]:
		return transform("""<?xml version="1.0" encoding="UTF-8"?><list>%s</list>\n"""%(xml),os.path.join(env.app.appDir,"static/xslt",env.output["XSLTFile"]),env.output.get("XSLTForceReload"))
	return """<?xml version="1.0" encoding="UTF-8"?><list>%s</list>\n"""%(xml)
