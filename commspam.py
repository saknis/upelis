#! /usr/bin/env python
# -*- coding: utf-8 -*-


import webapp2 as webapp
import wsgiref.handlers
import cgi
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types
import datetime
import urllib

class Prog(webapp.RequestHandler):
  def get(self):
    spamip = []
#    try:
    if True:
        buvesip = db.GqlQuery("SELECT * FROM SpamIP WHERE spam = :1", True)
        for app in buvesip:
            ipadresas = app.ipadresas
            spamip.append(ipadresas)
        buvescomm = db.GqlQuery("SELECT * FROM Commentsrec WHERE rodyti = :1", True)
        for app in buvescomm:
            ipadresas = app.ipadresas
            if ipadresas in spamip:
                app.rodyti=False
                app.put()
#    except:
#        klaida=True
    self.response.out.write("ok")
      

class SpamIP(db.Model):
  ipadresas = db.StringProperty()
  lastserver = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  check = db.BooleanProperty()
  spamcount = db.StringProperty()
  spam = db.BooleanProperty()
class Commentsrec(db.Model):
#  laikas = db.DateTimeProperty(auto_now_add=True)
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  rname = db.StringProperty(multiline=False)
  avatar = db.BlobProperty()
  avatarmax = db.BlobProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  ipadresas = db.StringProperty()
  rodyti = db.BooleanProperty()


url_map = [('/commspam', Prog)]
app = webapp.WSGIApplication(url_map, debug=True)
