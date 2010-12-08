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

from ACR.utils import replaceVars
from ACR.components import *
from ACR.utils.xmlextras import tree2xml
from xml.sax.saxutils import escape,unescape

class Default(Component):
	def generate(self, env,config):
		return Object(replaceVars(env, config))

	def parseAction(self,config):
		s=[]
		for elem in config["content"]:
			if type(elem) is tuple:
				s.append(tree2xml(elem,True))
			elif type(elem) is str:
				s.append(escape(elem))
		typ=config["params"].get("type","str")
		s="".join(s).strip()
		if typ=="csv":
			return re.split("\s*,\s*",s)
		return s

def getObject(config):
	return Default(config)
