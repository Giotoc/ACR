#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import sys,os
from wsgiref.simple_server import make_server
#from wsgiref.handlers import CGIHandler
from ACF.backends.standalone import standalone_server
from ACF import globals
import getpass
username=getpass.getuser()
print username
username=getpass.getuser()
try:
	__import__(username+"_conf")
except:
	raise Exception("This is development version of ACF! You should download the ACF GA.")
sys.argv[0] = 'acf'
apps=filter(os.path.isdir, map(lambda f: os.path.join(globals.appsDir,f),os.listdir(globals.appsDir)))
print apps
#this is ugly but we need to set the absolute path so whole system knows where get files from
#TODO export settings to /etc/ACF/config
#globals.ACFconf="/home/adrian/ACF/ACFconf.xml"
#one app run
#globals.appDir="/home/adrian/ACF/adrian/doc/"
#for multiple apps run - NotImplementedYet
#globals.appsDir="/home/adrian/ACF/project/"
host=""
port=9999
if len(sys.argv)>1:
	port=sys.argv[1]
print os.getpid()
httpd=make_server(host, port, standalone_server)
httpd.serve_forever()
# TWISTED.WEB

#from twisted.web import server
#from twisted.web.wsgi import WSGIResource
#from twisted.python.threadpool import ThreadPool
#from twisted.internet import reactor
#
## Create and start a thread pool,
## ensuring that it will be stopped when the reactor shuts down
#thread_pool=ThreadPool()
#thread_pool.start()
#reactor.addSystemEventTrigger('after', 'shutdown', thread_pool.stop)
#
## Create the WSGI resource
#wsgi_app_as_resource=WSGIResource(reactor, thread_pool, standalone_server)
#
#site=server.Site(wsgi_app_as_resource)
#reactor.listenTCP(port, site)
#reactor.run()
