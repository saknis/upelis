#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
import cgi
import email.Utils
import os
import re
import sys
import urllib
import urlparse
#import wsgiref.handlers
import zipfile
import datetime
import time
from time import mktime
from StringIO import StringIO


#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2 as webapp
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.api import users
#output=output+('-----<br>%s<br>-----<br>' % cgi.escape(greeting.content))

class MainHandler(webapp.RequestHandler):
	def get(self):
		if users.is_current_user_admin():
			output = ''
			zb = StringIO()
			zip = zipfile.ZipFile(zb, "w")
			now = time.localtime(time.time())[:6]
			greetings = db.GqlQuery("SELECT * FROM Page ")
			query = Page.all()
			co = query.count()
			for greeting in greetings:
#			date2 = time.localtime(greeting.modified)[:6]
				fname = greeting.name
				info = zipfile.ZipInfo(fname.encode('utf-8'))
				t=greeting.modified
				info.date_time = time.localtime(mktime(t.timetuple()))[:6]
				info.compress_type = zipfile.ZIP_DEFLATED
				out1=''
				out1 = greeting.content
				zip.writestr(info, out1.encode('utf-8'))
				output=output+("Name: %s\n" % greeting.name)
				if greeting.user:
					output=output+("Nick: %s\n" % greeting.user.nickname())
				else:
					output=output+"Nick: Anonimas\n"
				output=output+("Created: %s\n" % greeting.created)
				output=output+("Modified: %s\n" % greeting.modified)
				output=output+"\n-----\n"
			info = zipfile.ZipInfo("info.txt")
			info.date_time = now
			info.compress_type = zipfile.ZIP_DEFLATED
			zip.writestr(info, output.encode('utf-8'))
			zip.close()
			output=zb.getvalue()
#			max_age = 600
#			self.response.headers['Expires'] = email.Utils.formatdate(time.time() + max_age, usegmt=True)
#			cache_control = []
#			cache_control.append('public')
#			cache_control.append('max-age=%d' % max_age) 
#			self.response.headers['Pragma'] = 'public'
#			self.response.headers['Cache-Control'] = ', '.join(cache_control)
			self.response.headers['Cache-Control'] = 'public, max-age=60'
#			self.response.headers['Last-Modified'] = lastmod.strftime("%a, %d %b %Y %H:%M:%S GMT")
			expires = datetime.datetime.now() + datetime.timedelta(minutes=1)
			self.response.headers['Expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT") 
			ffdate = datetime.datetime.now()
			fdate = ffdate.strftime("%d-%b-%Y_%H-%M-%S")
			self.response.headers['Content-Type'] ='application/zip; name="zipcont_%s.zip"' % fdate 
			self.response.headers['Content-Disposition'] = 'attachment; filename="zipcont_%s.zip"' % fdate
			self.response.out.write(output)
		else:
			self.response.headers['Content-Type'] = 'text/html'
			self.response.out.write("<a href=\"%s\">You must be admin</a>." % users.create_login_url("/zipcont.zip"))


class Page(db.Model):
	content = db.TextProperty()
	created = db.DateTimeProperty(auto_now_add=True)
	modified = db.DateTimeProperty(auto_now_add=True)
	user = db.UserProperty(required=True)
	name = db.StringProperty()


#def main():
app = webapp.WSGIApplication([('/zipcont', MainHandler)], debug=True)
#	wsgiref.handlers.CGIHandler().run(application)
#	run_wsgi_app(application)

#if __name__ == '__main__':
#	main()


