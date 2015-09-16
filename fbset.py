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
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

class MainHandler(webapp.RequestHandler):

  def get(self):
    fbset1 = ""
    fbset2 = ""
    fbset3 = ""
    fbset4 = ""
    try:
        codelist = db.GqlQuery("SELECT * FROM FBSettings WHERE codename = :1", "fbsettings")
        for code in codelist:
            fbset1 = code.fbset1
            fbset2 = code.fbset2
            fbset3 = code.fbset3
            fbset4 = code.fbset4
    except:
        klaida=True
    if not users.is_current_user_admin():
        self.response.out.write("<html><body>Login as Admin</body></html>")
    else:
        path = os.path.join(os.path.dirname(__file__), "fbset.html")
        args = dict(fbset1=fbset1,fbset2=fbset2,fbset3=fbset3,fbset4=fbset4)
        self.response.out.write(template.render(path, args))
  def post(self):
    if users.is_current_user_admin():
        try:
            codelist = db.GqlQuery("SELECT * FROM FBSettings WHERE codename = :1", "fbsettings")
            for code in codelist:
                code.delete()
        except:
            klaida=True
        now = datetime.datetime.now()
        code = FBSettings(codename="fbsettings")
        code.time = now
        code.ipadresas = os.environ['REMOTE_ADDR']
        code.fbset1 = self.request.get("fbset1")
        code.fbset2 = self.request.get("fbset2")
        code.fbset3 = self.request.get("fbset3")
        code.fbset4 = self.request.get("fbset4")
        code.user = users.get_current_user()
        code.put()
        self.response.out.write("<html><body>Ok</body></html>")
    else:
        self.response.out.write("<html><body>Login as Admin</body></html>")
 
class FBSettings(db.Model):
  user = db.UserProperty()
  time = db.DateTimeProperty(auto_now_add=True)
  ipadresas = db.StringProperty()
  codename = db.StringProperty(required=True)
  fbset1 = db.StringProperty()
  fbset2 = db.StringProperty()
  fbset3 = db.StringProperty()
  fbset4 = db.StringProperty()


#def main():
app = webapp.WSGIApplication([('/fbsettings', MainHandler)],
                                       debug=True)
#  wsgiref.handlers.CGIHandler().run(application)
#  run_wsgi_app(application)


#if __name__ == '__main__':
#  main()


