#!/usr/bin/env python

# code from http://effbot.org/zone/simple-top-down-parsing.htm
# licence of original code was public domain
# relicenced to AGPL v3 by Asyncode Ltd. and:
# - specialized to work with ACR,
# - added interpreter,
# - optimized

# !!!NOT THREAD SAFE!!!

import sys
from cStringIO import StringIO
from ACR.utils import getStorage, dicttree,Object

class ProgrammingError(Exception):
	pass

symbol_table={}
#TODO optimization ('-',1) -> -1
class symbol_base(object):
	id=None
	value=None
	first=second=third=None

	def nud(self):
		raise SyntaxError("Syntax error (%r)." % self.id)

	def led(self, left):
		raise SyntaxError("Unknown operator (%r)." % self.id)

	def getTree(self):
		if self.id == "(name)":
			val=self.value.lower()
			if val in ["true","t"]:
				return True
			elif val in ["false","f"]:
				return False
			elif val in ["none","null","n","nil"]:
				return None
			return (self.id[1:-1], self.value)
		elif self.id == "(literal)":
			fstLetter=self.value[0]
			if fstLetter is "'":
				return self.value[1:-1]
			elif fstLetter.isdigit():
				try:
					return int(self.value)
				except:
					return float(self.value)
			else:
				if self.value=="True":
					return True
				elif self.value=="False":
					return False
				elif self.value=="None":
					return None
		out=[self.id, self.first, self.second, self.third]
		ret=[]
		for i in filter(None, out):
			if type(i) is str:
				ret.append(i)
			elif type(i) in [dict,tuple,list]:
				t=[]
				for j in i:
					try:
						t.append(j.getTree())
					except:
						t.append(j)
				if self.id=="(":
					return (self.id,ret[1],len(t) is 1 and t[0] or t)
				if self.id=="[":
					return ret[1:]
				ret.append(t)
				#return (self.id,ret[1:])
			else:
				ret.append(i.getTree())
		return tuple(ret)

	def __repr__(self):
		if self.id == "(name)" or self.id == "(literal)":
			return "(%s %s)" % (self.id[1:-1], self.value)
		out=[self.id, self.first, self.second, self.third]
		out=map(str, filter(None, out))
		return "(" + " ".join(out) + ")"

def symbol(id, bp=0):
		try:
				s=symbol_table[id]
		except KeyError:
				class s(symbol_base):
						pass
				s.__name__="symbol-" + id # for debugging
				s.id=id
				s.value=None
				s.lbp=bp
				symbol_table[id]=s
		else:
				s.lbp=max(bp, s.lbp)
		return s

# helpers

def infix(id, bp):
	def led(self, left):
		self.first=left
		self.second=expression(bp)
		return self
	symbol(id, bp).led=led

def infix_r(id, bp):
	def led(self, left):
		self.first=left
		self.second=expression(bp-1)
		return self
	symbol(id, bp).led=led

def prefix(id, bp):
	def nud(self):
		self.first=expression(bp)
		return self
	symbol(id).nud=nud

def advance(id=None):
	global token
	if id and token.id != id:
		raise SyntaxError("Expected %r" % id)
	token=next()

def method(s):
	# decorator
	assert issubclass(s, symbol_base)
	def bind(fn):
		setattr(s, fn.__name__, fn) #
	return bind

# python expression syntax

#symbol("lambda", 20)
#symbol("if", 20); symbol("else") # ternary form
infix_r("or", 30); infix_r("and", 40); prefix("not", 50)
infix("in", 60); infix("not", 60) # not in
infix("is", 60);
infix("<", 60); infix("<=", 60)
infix(">", 60); infix(">=", 60)
#infix("<>", 60); infix("!=", 60); infix("==", 60)
#infix("|", 70); infix("^", 80); infix("&", 90)
#infix("<<", 100); infix(">>", 100)
infix("+", 110); infix("-", 110)
infix("*", 120); infix("/", 120); infix("//", 120)
#infix("%", 120)
prefix("-", 130); prefix("+", 130); #prefix("~", 130)
#infix_r("**", 140)
symbol(".", 150); symbol("[", 150); symbol("(", 150)
# additional behaviour
symbol("(name)").nud=lambda self: self
symbol("(literal)").nud=lambda self: self
symbol("(end)")
symbol(")")

@method(symbol("("))
def nud(self):
	# parenthesized form; replaced by tuple former below
	expr=expression()
	advance(")")
	return expr

#symbol("else")

#@method(symbol("if"))
#def led(self, left):
#		self.first=left
#		self.second=expression()
#		advance("else")
#		self.third=expression()
#		return self

@method(symbol("."))
def led(self, left):
	attr=False
	if token.id==".":
		self.id=".."
		advance()
	if token.id=="@":
		attr=True
		advance()
	if token.id not in ["(name)","*"]:
		raise SyntaxError("Expected an attribute name.")
	self.first=left
	if attr:
		token.value="@"+token.value
	self.second=token
	advance()
	return self

#@method(symbol("@"))
#def led(self, left):
#	if token.id != "(name)":
#		raise SyntaxError("Expected an attribute name.")
#	self.first=left
#	self.second=token
#	advance()
#	return self

#symbol(":")
#symbol("$")
#symbol("}")
#@method(symbol("{"))
#def nud(self):
#	global token
#	advance("$")
#	t=token # storage name or variable name
#	token=next()
#	if token.id == ':': #there is a storage name
#		advance(':')
#		advance(':')
#		if t.value.lower() not in ["ss","rs","session","request"]:   #
#			raise SyntaxError("Wrong storage name '"+t.value+"'.")
#		self.first=t.value
#		self.second=""
#	else: #there is not a storage name
#		self.first="rs"
#		self.second=t.value
#	self.id="(variable)"
#	while token.id in [".","(name)"]:
#		if token.id=="(name)":
#			self.second+=token.value
#		else:
#			self.second+="."
#		advance()
#	advance("}")
#	return self

# handling variables; e.g storage::a.b.c
# default storage is request storage
symbol("$",160)
@method(symbol("$"))
def nud(self):
	global token
	self.id="(storage)"
	if token.id==".":
		self.first="rs"
	else:
		self.first=token.value
		advance()
	return self
symbol("]")

@method(symbol("["))
def led(self, left):
	self.first=left
	self.second=expression()
	advance("]")
	return self

symbol(")"); symbol(",")

@method(symbol("("))
def led(self, left):
	self.first=left
	self.second=[]
	if token.id != ")":
		while 1:
			self.second.append(expression())
			if token.id != ",":
				break
			advance(",")
	advance(")")
	return self

#symbol(":");
symbol("=")

#@method(symbol("lambda"))
#def nud(self):
#		self.first=[]
#		if token.id != ":":
#				argument_list(self.first)
#		advance(":")
#		self.second=expression()
#		return self

#def argument_list(list):
#		while 1:
#				if token.id != "(name)":
#						SyntaxError("Expected an argument name.")
#				list.append(token)
#				advance()
#				if token.id == "=":
#						advance()
#						list.append(expression())
#				else:
#						list.append(None)
#				if token.id != ",":
#						break
#				advance(",")

# constants

def constant(id):
	@method(symbol(id))
	def nud(self):
		self.id="(literal)"
		self.value=id
		return self

constant("None")
constant("True")
constant("False")

# multitoken operators

@method(symbol("not"))
def led(self, left):
	if token.id != "in":
		raise SyntaxError("Invalid syntax")
	advance()
	self.id="not in"
	self.first=left
	self.second=expression(60)
	return self

@method(symbol("is"))
def led(self, left):
	if token.id == "not":
		advance()
		self.id="is not"
	self.first=left
	self.second=expression(60)
	return self

@method(symbol("("))
def nud(self):
	self.first=[]
	comma=False
	if token.id != ")":
		while 1:
			if token.id == ")":
				break
			self.first.append(expression())
			if token.id != ",":
				break
			comma=True
			advance(",")
	advance(")")
	if not self.first or comma:
		return self # tuple
	else:
		return self.first[0]

symbol("]")

@method(symbol("["))
def nud(self):
	self.first=[]
	if token.id != "]":
		while 1:
			if token.id == "]":
				break
			self.first.append(expression())
			if token.id not in SELECTOR_OPS+[","]:
				break
			advance(",")
	advance("]")
	return self

#symbol("}")
#
#@method(symbol("{"))
#def nud(self):
#		self.first=[]
#		if token.id != "}":
#				while 1:
#						if token.id == "}":
#								break
#						self.first.append(expression())
#						advance(":")
#						self.first.append(expression())
#						if token.id != ",":
#								break
#						advance(",")
#		advance("}")
#		return self

import tokenize as tokenizer
type_map={
	tokenizer.NUMBER: "(literal)",
	tokenizer.STRING: "(literal)",
	tokenizer.OP: "(operator)",
	tokenizer.NAME: "(name)",
	tokenizer.ERRORTOKEN: "(operator)" # '$ ' is recognized in python tokenizer as error token!
}

# python tokenizer
def tokenize_python(program):
	for t in tokenizer.generate_tokens(StringIO(program).next):
		try:
			#change this to output python values in correct type
			yield type_map[t[0]], t[1]
		except KeyError:
			if t[0] == tokenizer.NL:
				continue
			if t[0] == tokenizer.ENDMARKER:
				break
			else:
				raise SyntaxError("Syntax error")
	yield "(end)", "(end)"

def tokenize(program):
	if isinstance(program, list):
		source=program
	else:
		source=tokenize_python(program)
	for id, value in source:
		if id == "(literal)":
			symbol=symbol_table[id]
			s=symbol()
			s.value=value
		else:
			# name or operator
			symbol=symbol_table.get(value)
			if symbol:
				s=symbol()
			elif id=="(name)":
				symbol=symbol_table[id]
				s=symbol()
				s.value=value
			else:
				raise SyntaxError("Unknown operator (%s)" % id)
		yield s

# parser engine
def expression(rbp=0):
	global token
	t=token
	token=next()
	left=t.nud()
	while rbp < token.lbp:
		t=token
		token=next()
		left=t.led(left)
	return left

def make_tree(expr):
	if type(expr) is not str:
		return Tree(expr)
	expr=expr.strip()
	if not len(expr):
		return Tree(True)
	global token, next
	next=tokenize(expr).next
	token=next()
	return Tree(expression().getTree())

SELECTOR_OPS=["is",">","<","is not",">=","<=","in","not in"]

class Tree(object):
	def __init__(self,tree):
		self.tree=tree

	def __str__(self):
		return "TreeObject(%s)"%str(self.tree)

	def __repr__(self):
		return self.__str__()

	def execute(self,acenv):
		D=acenv.doDebug
		if D: acenv.debug("START Tree.execute")
		def exe(node):
			"""
				node[0] - operator name
				node[1:] - params
			"""
			if D: acenv.debug("executing node '%s'", node)
			if type(node) in [str,int,float] or node in [True,False,None]:
				return node
			op=node[0]
			if op=="or":
				return exe(node[1]) or exe(node[2])
			elif op=="and":
				return exe(node[1]) and exe(node[2])
			elif op=="+":
				if len(node)>2:
					return exe(node[1]) + exe(node[2])
				else:
					return exe(node[1])
			elif op=="-":
				#TODO move -N to tree builder!
				if len(node)>2:
					return exe(node[1]) - exe(node[2])
				else:
					return - exe(node[1])
			elif op=="*":
				return exe(node[1]) * exe(node[2])
			elif op=="/":
				return exe(node[1]) / exe(node[2])
			elif op==">":
				return exe(node[1]) > exe(node[2])
			elif op=="<":
				return exe(node[1]) < exe(node[2])
			elif op==">=":
				return exe(node[1]) >= exe(node[2])
			elif op=="<=":
				return exe(node[1]) <= exe(node[2])
			elif op=="not":
				return not exe(node[1])
			elif op=="in":
				return exe(node[1]) in exe(node[2])
			elif op=="not in":
				return exe(node[1]) not in exe(node[2])
			elif op=="is" or op=="is not":
				if D: acenv.debug("found operator '%s'",op)
				fst=exe(node[1])
				snd=exe(node[2])
				if type(fst) is str or type(snd) is str  or type(fst) is Object:
					if D: acenv.debug("doing string comparison '%s'=='%s'",fst,snd)
					ret=str(fst) == str(snd)
				else:
					ret=fst is snd
				if op=="is not":
					return not ret
				else:
					return ret
			elif op=="(literal)":
				fstLetter=node[1][0]
				if fstLetter is "'":
					return node[1][1:-1]
				elif fstLetter.isdigit:
					return int(node[1])
				else:
					evaluatePath()
			elif op=="(storage)":
				return getStorage(acenv,node[1])
			elif op=="name":
				return node[1]
			elif op==".":
				fst=exe(node[1])
				if type(fst) is list:
					ret=[]
					for i in fst:
						ret.append(i[exe(node[2])])
					return ret
				return fst[exe(node[2])]
			elif op=="..":
				first=dicttree.flatten(exe(node[1]))
				if node[2][0]=="*":
					return first
				ret=[]
				second=exe(node[2])
				for i in first:
					try:
						ret.append(i[second])
					except:
						pass
				return ret
			elif op=="[":
				if len(node) is 2: # list
					return map(exe,node[1])
				if len(node) is 3: # operator []
					first=exe(node[1])
					s=node[2]
					if s[0] in SELECTOR_OPS:
						nodeList=[]
						nodeList_append=nodeList.append
						for i in first:
							try:
								if exe((s[0],i[s[1]],s[2])):
									nodeList_append(i)
							except:
								pass
						return nodeList
					second=exe(node[2])
					if type(first) in [list,tuple,str]:
						return first[int(second)]
					else:
						return first[second]
				raise ProgrammingError("Wrong usage of '[' operator")
			elif op=="(":
				""" The built-in functions """
				fnName=node[1][1]
				args=exe(node[2])
				if fnName=="sum":
					if type(args) in [int,float]:
						return args
					return sum(map(lambda x:type(x) in [int,float] and x or exe(x), args))
				if fnName=="int":
					return int(args)
				if fnName=="float":
					return float(args)
				if fnName=="str":
					return str(args)
				else:
					raise ProgrammingError("Function '"+fnName+"' does not exist.")

		D=acenv.doDebug
		if type(self.tree) is not tuple:
			return self.tree
		import time
		t=time.clock()
		ret=exe(self.tree)
		t2=time.clock()
		print t
		print t2
		print t2-t
		if D: acenv.debug("END Tree.execute with: '%s'", ret)
		return ret
