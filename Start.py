#!/usr/bin/env python
#
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.api import users
import datetime
import os

class Codeimagereg(db.Model):
  code = db.StringProperty(multiline=False)
  date = db.DateTimeProperty(auto_now_add=True)
  ipadresas = db.StringProperty()

class AppVer(db.Model):
  timestart = db.DateTimeProperty(auto_now_add=True)
  timelast = db.DateTimeProperty(auto_now_add=True)
  enable = db.BooleanProperty()
  appsoftver = db.StringProperty()
  appver = db.StringProperty(required=True)
  appid = db.StringProperty()
  hostname = db.StringProperty()
class DinCode(db.Model):
  user = db.UserProperty()
  time = db.DateTimeProperty(auto_now_add=True)
  ipadresas = db.StringProperty()
  codename = db.StringProperty(required=True)
  codetext = db.TextProperty()

      
class Start(object):
  def first(self):
    try:
        imgcodes = db.GqlQuery("SELECT * FROM Codeimagereg WHERE date < :1", datetime.datetime.now() + datetime.timedelta(minutes=-15))
        for imgcode in imgcodes:
            imgcode.delete()
    except:
        klaida=True

    
#    redir = False
#    if os.environ['HTTP_HOST']=='www.upe.lt' or os.environ['HTTP_HOST']=='lt.upe.lt' or os.environ['HTTP_HOST']=='us.upe.lt' or os.environ['HTTP_HOST']=='upe.lt':
#      redir = True
#    redir2 = False
#    if os.environ['HTTP_HOST']=='google5353c7992b3833b7.nerij.us':
#      redir2 = True
    
    
    
    buvoapp = False
    try:
        thisappver = os.environ['CURRENT_VERSION_ID']
        thisappid = os.environ['APPLICATION_ID']
        thisappsoftver = os.environ['SERVER_SOFTWARE']
        thishostname = os.environ['DEFAULT_VERSION_HOSTNAME']

        if True:
          try:
            buvesapp = db.GqlQuery("SELECT * FROM AppVer WHERE appver = :1", thisappver)
            for app in buvesapp:
              app.timelast = datetime.datetime.now()
              app.put()
              buvoapp = True
          except:
            klaida=True

#      db.put(buves_vart)
          if not buvoapp:
            app = AppVer(appver=thisappver)
            app.timestart = now
            app.timelast = now
            app.enable = False
            app.appsoftver = thisappsoftver
            app.appid = thisappid
            app.hostname = thishostname
            app.put()
    except:
        klaida=True

#    try:
#        codedb = db.GqlQuery("SELECT * FROM DinCode WHERE codename = :1", "start")
#        for thiscode in codedb:
#            thiscode = thiscode.codetext
#        appon = eval(thiscode)
#    except:
#        appon=False
