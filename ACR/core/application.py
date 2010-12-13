#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AsynCode Framework - XML framework allowing developing internet
# applications without using programming languages.
# Copyright (C) 2008-2010  Adrian Kalbarczyk, Marcin Radecki

# This program is free software: you can redistribute it and/or modify
# it under the terms of the version 3 of GNU General Public License as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#@marcin: views subdirs implementation

from ACR.utils.xmlextras import *
from ACR.utils import dicttree
from ACR.utils import json_compat
from ACR.session.file import FileSession
from ACR.core.view import View
from ACR.errors import *
from ACR import components,serializers
from ACR.components import *
from ACR.globals import MIMEmapper
import time,os

pjoin=os.path.join
pexists=os.path.exists
pisdir=os.path.isdir
D=False

class Application(object):
	appName=""
	dbg=None
	prefix="ACR_"
	storage=None
	appDir=""
	lang="en"
	immutable=False
	def __init__(self,appDir):
		#cache for component objects
		self.immutable=False
		self.COMPONENTS_CACHE={}
		self.DEFAULT_DB=None
		self.views={}
		self.lang="en"
		self.langs=[]
		self.viewsPath=os.path.join(appDir, "views")
		#if D: log.debug("Creating instance with appDir=%s",appDir)
		try:
			self.configPath=os.path.join(appDir, "config.xml")
			self.timestamp=os.stat(self.configPath).st_mtime
			config=xml2tree(self.configPath)
		except IOError:
			#if D: log.critical("Application config not found!")
			raise Exception("Application config not found at %s!"%(appDir+"\config.xml"))
		self.appDir=appDir
		self.config=config
		try:
			self.appName=config.get("/name/text()")[0]
		except AttributeError,e:
			#if D: log.critical("Application name not set in configuration file!")
			raise Exception("Application name not set in configuration file!")
		#for optimization we get some data from config and add it as object properties
		self.computeLangs()
		self.domain="".join(config.get("/domain/text()") or ["localhost"])
		debug=config.get("/debug")
		if debug:
			self.dbg={
				"enabled":config.get("/debug[@enable]") or False,
				"level":config.get("/debug[@level]") or "error",
				"dbtimer":0,
				"dbcounter":0
			}
		self.output={
			"engine":config.get("/output[@engine]") or None,
			"xsltfile":config.get("/output[@xsltfile]") or None,
			"format":config.get("/output[@format]") or "application/xml"
		}
		#engineConf=config.get("/engine")[0]
		#self.engine=te.get(engineConf[1]["name"]).engine(engineConf)
		self.prefix=(config.get("/prefix") or "ACR")+"_"
		self.sessionDir="".join(config.get("/sessiondir/text()"))
		for component in config.get("/component"):
			#if D: log.debug("setting default configuration to %s component",component[1]["name"])
			self.getComponent(component[1]["name"],component[2])
		#do it or not?
		#self.config=None
		self.immutable=True

	# checks if an application instance should be reloaded
	def checkRefresh(self):
		return self.timestamp < os.stat(self.configPath).st_mtime

	def getDBConn(self):
		if not self.DEFAULT_DB:
			self.DEFAULT_DB=self.getComponent("database").CONNECTIONS["default"]
		return self.DEFAULT_DB

	def getComponent(self,name,conf=None):
		##print "getComponent"
		##print name
		if self.COMPONENTS_CACHE.has_key(name):
			##print "cache"
			return self.COMPONENTS_CACHE[name]
		##print "Component not in cache"
		##print components.get(name)
		o=components.get(name).getObject(conf)
		##print o
		##print "end"
		self.COMPONENTS_CACHE[name]=o
		return o

	#lazy view objects creation
	def getView(self,URLpath):
		#TODO rewrite it:
		# 1. View.isUpToDate - should check its super view and posibly update object internally
		#    when view file is deleted, should raise error
		# 2. here should be try to fileNotFound error which should refresh cache
		# 3. then check for mistakes (eg. now some views are not cached)
		#D=acenv.doDebug
		#if D: acenv.info("Executing View at '%s'"%("/".join(URLpath)))
		(o, i)=dicttree.get(self.views, URLpath, False)
		if i==len(URLpath) and type(o) is dict and o.has_key("default"):
			o=o["default"]
			#if D: acenv.debug("Executing '%s'/default"%("/".join(URLpath)))
		#TODO handle an event when file was deleted; probably raises exception
		if type(o) is View and o.isUpToDate():
			#if D: acenv.info("View '%s' taken from cache"%("/".join(URLpath[:i])))
			return (o, URLpath[i:])
		#if D and type(o) is View and not o.isUpToDate(): acenv.info("View file changed")
		#elif D: acenv.info("View is not cached")
		i=0
		viewPath=pjoin(self.viewsPath, *URLpath[:i])
		#if D: acenv.debug("Searching from '%s'"%(viewPath))
		viewName,inputs=URLpath[:i],URLpath[i:]
		temp=viewPath
		while len(inputs):
			temp=pjoin(temp, inputs[0])
			if not pisdir(temp):
				break
			viewPath=temp
			viewName.append(inputs.pop(0))
		#if D: acenv.debug("viewPath: %s"%(viewName))
		#if D: acenv.debug("inputs: %s"%(inputs))
		if inputs and os.path.exists(pjoin(viewPath,inputs[0])+".xml"):
			viewName.append(inputs.pop(0))
		elif not inputs and os.path.exists(viewPath+".xml"):
			pass
		elif not inputs and os.path.exists(pjoin(viewPath,"default.xml")):
			viewName.append("default")
		else:
			viewName=["notFound"]
		v=View(viewName, self)
		dicttree.set(self.views, viewName, v)
		return (v, inputs)

	#will be generator
	def generate(self,acenv):
		D=acenv.doDebug
		if True: t=time.time()
		prefix=acenv.prefix+"SESS"
		if acenv.cookies.has_key(prefix):
			if D:acenv.info("Session cookie found")
			sessID=acenv.cookies[prefix]
			try:
				acenv.sessionStorage=FileSession(acenv,sessID)
			except:
				sessID=None
		try:
			view, acenv.inputs=self.getView(acenv.URLpath)

		# checking global conditions
		#viewList=[]
		#while view:
		#	viewList.append(view)
		#	view=view.parent
		#viewList.reverse()
		#view=viewList[-1]
		#from super class to deriverativ classes
		#for v in viewList:
		#	if not v.checkConditions(acenv):
		#		if not v.parent:
		#			acenv.output["format"]="text/html"
		#			return "<html><body>Cannot generate view.</body</html>"
		#		view=v.parent
		#		break
			view.generate(acenv)
		except Error,e:
			#print "Error"
			acenv.generations={
				"error":("object",{"name":"GlobalError","status":"error","error":e.name},e.error)
			}
			acenv.output["xsltfile"]=view.output.get("xsltfile")
		#this is little faster than Object
		langs=[]
		for i in acenv.langs:
			langs.append((i,None,None))
		acenv.generations["acf:lang"]=("object",{"name":"acf:lang","current":acenv.lang},langs)
		acenv.generations["acf:domain"]=("object",{"name":"acf:appDetails","domain":acenv.domain,"config":acenv.outputConfig},None)
		#temporary error handling
		if acenv.sessionStorage:
			acenv.info("Session exists")
			sess=acenv.sessionStorage.data
			acenv.generations["acf:user"]=("object",{"ID":str(sess["ID"]),"name":"acf:user","email":sess["email"],"role":sess["role"]},None)
			acenv.sessionStorage.save()
		try:
			s=serializers.get(globals.MIMEmapper.get(acenv.output["format"]))
		except Error, e:
			acenv.output["format"]="text/html"
			return "<html><body>"+str(e)+"</body</html>"
		#if True:
		all=round((time.time()-t)*1000,5)
		dbms=round(acenv.dbg["dbtimer"]*1000,5)
		if True or D:
			print("Generated in %s, where:"%(all))
			print("	DBMS took %s"%(dbms))
			print("	Python took %s"%(all-dbms))
			t=time.time()
		x=s.serialize(acenv)
		if True or D:
			print "Serializer took %s"%(round((time.time()-t)*1000,5))
		return x

	def transform(self,acenv):
		self.getXML(acenv)

	def computeLangs(self):
		attrs=self.config.get("/lang")[0][1]
		try:
			defaultLang=attrs["default"].strip()
		except KeyError:
			#make it log.warning and fall back to en
			raise Exception("Misconfiguration of 'langs' setting in app configuration file.")
		#["","aaa"," dd   "]->["aaa","ddd"]
		self.langs=filter(len, map(str.strip, [defaultLang]+attrs.get("supported", "").split(",")))
		self.lang=self.langs[0]

	def __str__(self):
		return str(self.__dict__)

	def __setattr__(self, name, val):
		if self.immutable and not name=="DEFAULT_DB":
			if D: log.error("%s is read only",name)
			raise Exception("PropertyImmutable")
		self.__dict__[name]=val
