#!/usr/bin/env python
#
 
import webapp2 as webapp
import wsgiref.handlers
import os, sys
import cgi
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.api import users
import datetime

class Button(db.Model):
  author = db.UserProperty()
  filename = db.StringProperty(multiline=False)
  fileext = db.StringProperty(multiline=False)
  filedata = db.BlobProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  ipadresas = db.StringProperty()


class DelButton(webapp.RequestHandler):
	def get(self):
		try:
			imgcodes = db.GqlQuery("SELECT * FROM Button WHERE date < :1", datetime.datetime.now() + datetime.timedelta(days=-7))
			for imgcode in imgcodes:
				imgcode.delete()
			self.response.out.write('ok')

		except:
			klaida=True
			self.response.out.write('error')

url_map = [('/delbutton', DelButton)]
app = webapp.WSGIApplication(url_map, debug=True)
