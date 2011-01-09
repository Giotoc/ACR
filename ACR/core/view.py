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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ACR.utils.xmlextras import *
from ACR import acconfig
from ACR import components
from ACR.errors import *
from ACR.utils import getStorage,prepareVars,typesMap
from ACR.utils.interpreter import make_tree
from ACR.components import Object, List
import os,re

DEFINE="define"
SET="set"
COMMAND="command"
INHERITS="inherits"
IMPORT="import"

def parsePosts(nodes):
	if not nodes:
		return (None,None)
	ret={}
	postCount=0
	for i in nodes:
		attrs=i[1]
		typ=typesMap.get(attrs.get("type"),typesMap["default"])()
		if attrs.has_key("default"):
			typ.setDefault(make_tree(attrs["default"]))
			postCount+=1
		ret[attrs["name"]]=typ
	return (ret,postCount)

def parseInputs(nodes):
	if not nodes:
		return None
	ret=[]
	postCount=0
	for i in nodes:
		attrs=i[1]
		typ=typesMap.get(attrs.get("type","default"))()
		if attrs.has_key("default"):
			typ.setDefault(make_tree(attrs["default"]))
		ret.append({
			"name":attrs["name"],
			"type":typ
		})
	return ret

class View(object):
	def __init__(self, name, app):
		#All "static" computations should be here. Don't do it inside handle!
		#setting immutable because of setter
		self.immutable=False
		self.name="/".join(name)
		self.app=app
		self.path=os.path.join(app.viewsPath,*name)+".xml"
		#try:
		self.timestamp=os.stat(self.path).st_mtime
		tree=xml2tree(self.path, True)
		#TODO support more exception classes;
		#except Exception,e:
		#	self.immutable=True
		#	raise ViewNotFound("view '%s' not found"%(name))
		ns={}
		if not tree[1]:
			return
		#parses "xmlns:" attributes and extracts namespaces
		for i in tree[1]:
			if i.startswith("xmlns:"):
				key=i.split(":")[1]
				value=tree[1][i].split("/").pop().lower()
				ns[key]=value
		self.namespaces=ns
		#checks whether view inherits from another view
		try:
			self.parent=app.getView(filter(lambda x: not str.isspace(x) and len(x)!=0,tree[1]["inherits"].split("/")))[0]
		except:
			self.parent=None
		inputSchemas=[]
		conditions=[]
		actions=[]
		postSchemas=[]
		output=[]
		ACTIONS=[SET,DEFINE,IMPORT]
		for node in tree[2]:
			if type(node) is str:
				continue
			name=node[0]
			if name=="param":
				inputSchemas.append(node)
			elif name=="condition":
				conditions.append(node)
			elif name=="output":
				output.append(node)
			elif name=="post":
				postSchemas=filter(lambda x: type(x) is not str, i[2])
			elif name in ACTIONS:
				actions.append(node)
		self.conditions=self.parseConditions(conditions)
		self.actions=self.parseActions(actions)
		self.inputSchemas=parseInputs(inputSchemas) or []
		if self.parent and self.parent.inputSchemas:
			self.inputSchemas=self.parent.inputSchemas+self.inputSchemas
		self.postSchemas, self.postCount=parsePosts(postSchemas)
		self.output={}
		try:
			self.output["format"]=output[0][1]["format"]
		except: pass
		try:
			self.output["xsltfile"]=output[0][1]["xsltfile"]
		except: pass
		try:
			self.outputConfig=output[0][1]["config"]
		except:
			outputConfig="config"
		# TODO check if it is correct
		## output inheritance
		#if self.parent and self.parent.outputFormat:
		#		self.outputFormat=self.parent.outputFormat
		#		self.outputConfig=self.parent.outputConfig
		## posts inheritance
		#if self.parent and self.parent.posts:
		#	self.posts=self.parent.posts
		#if not self.actions:
		#	self.immutable=True
		#	return
		#if D: log.debug("Setting defaults for posts")
		#past here this object MUST be immutable
		self.immutable=True

	def parseConditions(self, a):
		ret=[]
		for i in a:
			attrs=i[1]
			ret.append({
				"name":attrs.get("name"),
				"value":make_tree(attrs.get("value") or "".join(i[2]).strip())
			})
		return ret

	def checkConditions(self, acenv):
		for i in self.conditions:
			if i["value"] and not execute(acenv, i["value"]):
				return False
		return True

	#def importAction(self,action):
	#	path=re.split("/*",action[1].get("path"))
	#	v=self.app.getView(path[:-1])[0]
	#	for a in v.actions:
	#		if a["name"]==path[-1]:
	#			ret.append(a)
	#			ret[-1]["name"]=action[1].get("name", None)
	#			break

	def parseAction(self,action):
		""" Gets tuple representation of action XML element and returns dict-based configuration """
		attrs=action[1]
		ns,cmd=NS2Tuple(attrs.get(COMMAND,"default"))
		params={}
		if ns:
			for attr in attrs:
				if attr.startswith(ns+":") and not attr==ns+cmd:
					params[attr.split(":").pop()]=prepareVars(action[1][attr])
		ret={
			"command":cmd,
			"params":params,
			"content":action[2]
		}
		if action[0]==DEFINE:
			ret["output"]=True
		return ret

	def parseActions(self,actions):
		def findAction(actions,name):
			if not name:
				return None
			i=len(actions)-1
			if i<=0:
				return None
			try:
				while not actions[i]["name"]==name:
					i-=1
				return i
			except:
				return None
			else:
				return len(actions)

		if self.parent:
			ret=self.parent.actions[:]
		else:
			ret=[]
		for action in actions:
			#if i[0]=="import":
			#	self.importAction(i[0])
			#	continue
			typ=action[0]
			attrs=action[1]
			ns,cmd=NS2Tuple(attrs.get(COMMAND,"default"))
			componentName=self.namespaces.get(ns,"default")
			o={
				"type":typ,#DEFINE or SET
				#"command":cmd,#command name
				"name":attrs.get("name",None),
				"component":componentName,
				"condition":make_tree(attrs.get("condition")),
				"default":make_tree(attrs.get("default")),
				"config":self.app.getComponent(componentName).parseAction(self.parseAction(action)),
			}

			# positions the action in the list of actions
			before=attrs.get("before")
			after=attrs.get("after")
			parentPos=findAction(ret,o["name"])
			if before:
				if before=='*':
					ret.insert(0, o)
					ret.pop(parentPos)
				else:
					ret.insert(findAction(ret,before),o)
			elif after:
				if after=='*':
					ret.append(o)
					ret.pop(parentPos)
				else:
					ret.insert(findAction(ret,after)+1,o)
			else:
				if parentPos:
					ret.pop(parentPos)
				ret.append(o)
		return ret

	def fillPosts(self,acenv):
		D=acenv.doDebug
		if D: acenv.info("Create '%s' view",(self.name))
		if not self.postSchemas or not len(self.postSchemas):
			if D: acenv.debug("list of posts is empty. Returning 'True'.")
			return True
		list=acenv.posts
		if not list or len(list)<self.postCount:
			#TODO normalize the Error messages!
			raise Error("Not enough post fields")
		postSchemas=self.postSchemas
		try:
			for i in postSchemas:
				value=list.get(i)
				typ=postSchemas[i]
				typ.set(value)
				acenv.requestStorage[i]=typ.get(acenv)
		except Error,e:
			if e.name=="NotValidValue":
				raise Error("NotValidValue", "Value of %s is invalid"%(i))

	def fillInputs(self,acenv):
		D=acenv.doDebug
		if D: acenv.debug("START fillInputs")
		list=acenv.inputs
		inputSchemas=self.inputSchemas
		if D:
			acenv.debug("inputSchemas are: %s",inputSchemas)
			acenv.debug("inputs are: %s",list)
		if not inputSchemas or not len(inputSchemas):
			if D: acenv.debug("list of inputs is empty. Returning 'True'.")
			return True
		for i in inputSchemas:
			typ=i["type"]
			try:
				typ.set(list.pop(0))
			except:
				pass
			acenv.requestStorage[i["name"]]=typ.get(acenv)
		if D:
			acenv.debug("RS is: %s",acenv.requestStorage)
			acenv.debug("END fillInputs")

	def generate(self,acenv):
		D=acenv.doDebug
		try:
			self.inputSchemas
		except:# inputs is undefined
			acenv.generations.append(("object",{"type":"view","name":self.name},None))
			self.transform(acenv)
			return
		#if D: acenv.debug("Executing with env=%s",acenv)
		self.fillInputs(acenv)
		self.fillPosts(acenv)
		acenv.requestStorage["__lang__"]=acenv.lang
		#print "rs"
		#print acenv.requestStorage
		#print "actions"
		#print self.actions
		for action in self.actions:
			if D: acenv.info("define name='%s'",action["name"])
			if action["condition"] and not action["condition"].execute(acenv):
				#print "condition not meet %s"%(str(action["condition"].tree))
				#print action["name"]
				if D: acenv.warning("Condition is not meet")
				if action["type"]==SET:
					if D: acenv.warning("Set condition is not meet.")
					ns,name=NS2Tuple(action["name"],"::")
					default=action.get("default")
					if default:
						getStorage(acenv,ns or "rs")[name]=default.execute(acenv)
				continue
			component=self.app.getComponent(action["component"])
			#object or list
			generation=component.generate(acenv,action["config"])
			##print "generation"
			##print generation._value
			##print acenv.requestStorage
			if not generation:
				raise Error("ComponentError","Component did not return proper value. Please contact component author.")
			if not action["name"]:
					continue
			if action["type"]==DEFINE:
				if D: acenv.info("Executing action=%s",action)
				generation.name=action["name"]
				generation.view=self.name
				acenv.generations[action["name"]]=generation
			elif action["type"]==SET:
				if D: acenv.info("Executing SET=%s",action)
				ns,name=NS2Tuple(action["name"],"::")
				getStorage(acenv,ns or "rs")[name]=generation

		try:
			acenv.output["format"]=self.output["format"]
		except:
			pass
		try:
			acenv.output["xsltfile"]=self.output["xsltfile"]
		except:
			pass

	def isUpToDate(self):
		return self.timestamp >= os.stat(self.path).st_mtime

	def __setattr__(self, name, val):
		if name!="immutable" and self.immutable:
			#if D: log.error("%s is read only",name)
			raise Exception("PropertyImmutable")
		self.__dict__[name]=val
