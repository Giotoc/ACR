#!/usr/bin/python
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

from ACR.utils.xmlextras import unescapeQuotes
from ACR.errors import Error
from ACR.utils import str2obj
import re

class Default(object):
	def __init__(self,value=None,default=None,config=None):
		if default:
			self.default=self.setDefault(default)
		if value:
			self.set(value,config)

	def set(self,value,config=None):
		if not value:
			return
		value=value.strip()
		if self.validate(value,config):
			self.value=self._prepareValue(value)
		else:
			raise Error("ValueNotVaild")

	def setDefault(self,default):
		self.default=default

	def get(self,acenv=None,value=None):
		D=acenv and acenv.doDebug
		if D:acenv.start("Type.get")
		# "" is valid so "is not None" is needed!
		if value is not None:
			try:
				value=value.strip()
			except:
				pass
			if D: acenv.end("Type.get value was set, returning with: '%s'",value)
			v=self._prepareValue(value)
			self.validate(v) # raises Error on invalid
			return v
		try:
			if D and self.value: acenv.debug("END Type.get with self.value: '%s'",self.value)
			return self.value
		except:
			if self.__dict__.has_key("default"):
				if D: acenv.end("Type.get with self.default: '%s'",self.default.execute(acenv))
				return self.default.execute(acenv)
			else:
				if D: acenv.end("Type.get with error ValueNotVaild")
				raise Error("NotValidValue", "Validation failed and no default value was set.")

	def reset(self):
		self._value=None

	def validate(self,value,config=None):
		if config:
			ml=config.get("minLenght")
			if ml and len(value)<int(ml):
				raise Error("ValueTooShort", "Value should be string of at least %s but is '%s'",len(value),type(value))
			ml=config.get("maxLenght")
			if ml and len(value)>int(ml):
				raise Error("ValueTooLong", "Value should be string of at most %s but is '%s'",len(value),type(value))
		return True

	def _prepareValue(self,value):
		return value

	def __repr__(self):
		return type(self).__name__+"Type(default="+str(self.__dict__.get("default","ErrorOnInvalid"))+")"

class XML(Default):
	pass

XSSCleaner=None

class safeHTML(Default):
	RE_ESCAPE=re.compile(r'<|(j\s*a\s*v\s*a\s*s\s*c\s*r\s*i\s*p\s*t\s*:|\s*iframe|\s*frame|)',re.IGNORECASE | re.MULTILINE )
	def _prepareValue(self,value):
		global XSSCleaner
		if not XSSCleaner:
			from ACR.utils.XSSCleaner import XssCleaner
			XSSCleaner=XssCleaner()
		return XSSCleaner.strip(value)

class Text(Default):
	def validate(self,value,config=None):
		if not type(value) is str:
			raise Error("NotString", "Should be string but is %s",type(value))
		return True

	def _prepareValue(self,value):
		return unescapeQuotes(value.strip())

class Number(Default):
	def validate(self,value,config=None):
		tv=type(value)
		if value is None or tv not in (int,float) or tv in (str,unicode) and not value.isdigit():
			raise Error("NotNumber", "Should be number, but is %s"%value)
		return True

	def _prepareValue(self,value):
		if value=='':
			return 0
		else:
			return int(value)

class Boolean(Default):
	def validate(self,value,config=None):
		return value in (True,False)

	def _prepareValue(self,value):
		return str2obj(value)

class Email(Default):
	EMAIL_RE=re.compile("^[a-zA-Z0-9._%\-\+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$")
	def validate(self,value,config=None):
		if not type(value) is str:
			raise Error("NotString", "Should be string but is %s",type(value))
		# shortest is a@a.pl == 6 letters
		if not (len(value)>5 and self.EMAIL_RE.match(value)):
			raise Error("NotValidEmailAddress", "Suplied value is not a valid e-mail address")
		return True

class URL(Default):
	URL_RE=re.compile(
		"(((https?|ftp)\:)?\/\/)?" + #SCHEME
    "([a-z0-9+!*(),;?&=\$_.-]+(\:[a-z0-9+!*(),;?&=\$_.-]+)?@)?"+ #User and Pass
    "([a-z0-9-.]*)\.([a-z]{2,3})" + # Host or IP
    "(\:[0-9]{2,5})?" + # Port
    "(\/([a-z0-9+\$_-]\.?)+)*\/?" + # Path
    "(\?[a-z+&\$_.-][a-z0-9;:@&%=+\/\$_.-]*)?" + # GET Query
    "(#[a-z_.-][a-z0-9+\$_.-]*)?" # Anchor
	)
	def validate(self,value,config=None):
		if not type(value) is str:
			raise Error("NotString", "Should be string but is %s",type(value))
		# shortest is a.pl == 4 letters
		if not (len(value)>3 and self.URL_RE.match(value)):
			raise Error("NotValidURL", "Suplied value is not a valid URL")
		return True

class Empty(Default):
	def validate(self,value,config=None):
		if not type(value) is str:
			raise Error("NotString", "Should be string but is %s",type(value))
		if len(value) is 0:
			return True
		else:
			raise Error("NotEmptyString", "Should be an empty string")

class NonEmpty(Default):
	def validate(self,value,config=None):
		if not type(value) is str:
			raise Error("NotString", "Should be string but is %s",type(value))
		if len(value)>0:
			return True
		else:
			raise Error("EmptyString", "Should not be an empty string")

class HEXColor(Default):
	COLOR_RE=re.compile("^([a-f]|[A-F]|[0-9]){3}(([a-f]|[A-F]|[0-9]){3})$")
	def validate(self,value,config=None):
		if not type(value) is str:
			raise Error("ShouldBeString", "Should be string but is %s",type(value))
		if not (len(value) in [3,6] and self.COLOR_RE.match(value)):
			raise Error("NotValidHEXColor", "Should be valid HEX color (xxx or xxxxxx where x is 1-9 or a-f)")
		return True

#DATETIME
class date(Default):
	def validate(self,value,config=None):
		if type(str2obj(value)) in [str,unicode]:
			raise Error("NotNumber", "Should be number, but is %s",value)
		return True

	def _prepareValue(self,value):
		return datetime.date(value.y,value.m,value.d)

#COMPLEX TYPES

class List(Default):
	RE_DELIMITER=re.compile("\s*,\s*")
	def validate(self,value,config=None):
#		if not type(value) in :
#			raise Error("NotList", "Should be List but is '%s'",type(value))
		return True

	def _prepareValue(self,value):
		return self.RE_DELIMITER.split(value)

class CSV(List):
	RE_DELIMITER=re.compile("\s*,\s*")
	pass

# file type

class File(Default):
	def set(self,value):
		self.value=self._prepareValue(value)

	def validate(self,value,config=None):
		return True

	def _prepareValue(self,value):
		return value

#JSON type
from ACR.utils.json_compat import loads

class JSON(Default):
	def set(self,value):
		self.value=self._prepareValue(value)

	def validate(self,value,config=None):
		return True

	def _prepareValue(self,value):
		return loads(value)
