#!/usr/bin/env python
#
import os
import datetime
#import wsgiref.handlers
from google.appengine.api import users
#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2 as webapp
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types

class MainHandler(webapp.RequestHandler):

  def get(self):
    try:
        codelist = db.GqlQuery("SELECT * FROM DinCode WHERE codename = :1", "start")
        for code in codelist:
            code.delete()
        codelist = db.GqlQuery("SELECT * FROM DinCode WHERE codename = :1", "disable")
        for code in codelist:
            code.delete()
    except:
        klaida=True
    now = datetime.datetime.now()
    code = DinCode(codename="start")
    code.time = now
    code.ipadresas = os.environ['REMOTE_ADDR']
    code.codetext = "True"
    code.user = users.get_current_user()
    code.put()
    coded = DinCode(codename="disable")
    coded.time = now
    coded.ipadresas = os.environ['REMOTE_ADDR']
    coded.codetext = "<html><body>Disable</body><html>"
    coded.user = users.get_current_user()
    coded.put()

    self.response.out.write("<html><body>Site On</body></html>")
 
class DinCode(db.Model):
  user = db.UserProperty()
  time = db.DateTimeProperty(auto_now_add=True)
  ipadresas = db.StringProperty()
  codename = db.StringProperty(required=True)
  codetext = db.TextProperty()


#def main():
app = webapp.WSGIApplication([('/on', MainHandler)],
                                       debug=True)
#  wsgiref.handlers.CGIHandler().run(application)
#  run_wsgi_app(application)


#if __name__ == '__main__':
#  main()


