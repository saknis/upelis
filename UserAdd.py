#!/usr/bin/env python
#
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.api import users
import datetime
import os

class Vartotojai(db.Model):
  lankytojas = db.UserProperty(required=True)
  laikas = db.DateTimeProperty(auto_now_add=True)
  administratorius = db.BooleanProperty()
  ipadresas = db.StringProperty()
  narsykle = db.StringProperty()
  userid = db.StringProperty()
  avatarmin = db.BlobProperty()
  avatarmax = db.BlobProperty()
  rodyti = db.BooleanProperty()
  picarodyti = db.BooleanProperty()
  plusrodyti = db.BooleanProperty(default=True)
  commrodyti = db.BooleanProperty()
  content = db.TextProperty()
  pseudonimas = db.StringProperty()
  youtname= db.StringProperty()
      

      
class UserAdd(object):
  def plus(self):
    user = users.get_current_user()
    now = datetime.datetime.now()
    buvo = False
    if user:
      try:
        buves_vart = db.GqlQuery("SELECT * FROM Vartotojai WHERE lankytojas = :1", user)
        for vart in buves_vart:
          vart.ipadresas = os.environ['REMOTE_ADDR']
          vart.narsykle = os.environ['HTTP_USER_AGENT']
          vart.laikas = datetime.datetime.now()
          vart.userid = user.user_id()
          if users.is_current_user_admin():
            vart.administratorius = True
          else:
            vart.administratorius = False
          vart.put()
          buvo = True
      except:
        klaida=True

#      db.put(buves_vart)
      if not buvo:
        vart = Vartotojai(lankytojas=user)
        vart.ipadresas = os.environ['REMOTE_ADDR']
        vart.narsykle = os.environ['HTTP_USER_AGENT']
        vart.laikas = now
        vart.userid = user.user_id()
        if users.is_current_user_admin():
          vart.administratorius = True
        else:
          vart.administratorius = False
        vart.rodyti = False
        vart.plusrodyti = True
        vart.picarodyti = False
        vart.commrodyti = False
        vart.put()

