#! /usr/bin/env python
# -*- coding: utf-8 -*-


import webapp2 as webapp
import wsgiref.handlers
import os, sys
import cgi
import re
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types
import datetime
import urllib
from google.appengine.api import urlfetch
from google.appengine.api import urlfetch_errors
from google.appengine.api import urlfetch_service_pb
import socket
urlfetch.set_default_fetch_deadline(300)

class Prog(webapp.RequestHandler):
  def get(self):
    z="localhost"
    bil=True
    try:
    	host = socket.gethostbyname(z)
    except Exception, e:
    	ee = "%s" % (e)
    	if ee.find('billing') <> 0:
    		bil=False
    terr=''
    try:
#    if True:
        buvesip = db.GqlQuery("SELECT * FROM SpamIP WHERE check = :1", False)
        for app in buvesip:
            ipadresas = app.ipadresas
            lastserver = int(app.lastserver)+1
            spamcount = int(app.spamcount)
            if lastserver<84:
                if bil:
                	url = "http://%s/bl3?ip=%s&nr=%s" % (os.environ['HTTP_HOST'],ipadresas,lastserver)
                else:
                	url = "http://www.procentai.lt/bl3.php?ip=%s&nr=%s" % (ipadresas,lastserver)
                result = urlfetch.fetch(url=url,method=urlfetch.GET,follow_redirects=True)
                cont=result.content
                cont=cont.lstrip()
                cont=cont[:4]
                zzz=urllib.quote(cont)
                if cont=='true':
                    app.lastserver = str(lastserver)		  
                    app.spam=True			  
                    app.spamcount=str(spamcount+1)	
                elif cont=='fals':
                    app.lastserver = str(lastserver)		  
            else:
                app.check=True
            app.date = datetime.datetime.now()		  			  
            app.put()
            break	
    except urlfetch_errors.DeadlineExceededError, message:
        klaida=True
        terr='timeout'
    except:
        klaida=True
    self.response.out.write("ok %s" % (terr))
      

class SpamIP(db.Model):
  ipadresas = db.StringProperty()
  lastserver = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  check = db.BooleanProperty()
  spamcount = db.StringProperty()
  spam = db.BooleanProperty()


url_map = [('/checkspamip', Prog)]
app = webapp.WSGIApplication(url_map, debug=True)
