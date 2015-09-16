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
    liset1 = ""
    liset2 = ""
    liset3 = ""
    liset4 = ""
    try:
        codelist = db.GqlQuery("SELECT * FROM LISettings WHERE codename = :1", "lisettings")
        for code in codelist:
            liset1 = code.liset1
            liset2 = code.liset2
            liset3 = code.liset3
            liset4 = code.liset4
    except:
        klaida=True
    if not users.is_current_user_admin():
        self.response.out.write("<html><body>Login as Admin</body></html>")
    else:
        path = os.path.join(os.path.dirname(__file__), "liset.html")
        args = dict(liset1=liset1,liset2=liset2,liset3=liset3,liset4=liset4)
        self.response.out.write(template.render(path, args))
  def post(self):
    if users.is_current_user_admin():
        try:
            codelist = db.GqlQuery("SELECT * FROM LISettings WHERE codename = :1", "lisettings")
            for code in codelist:
                code.delete()
        except:
            klaida=True
        now = datetime.datetime.now()
        code = LISettings(codename="lisettings")
        code.time = now
        code.ipadresas = os.environ['REMOTE_ADDR']
        code.liset1 = self.request.get("liset1")
        code.liset2 = self.request.get("liset2")
        code.liset3 = self.request.get("liset3")
        code.liset4 = self.request.get("liset4")
        code.user = users.get_current_user()
        code.put()
        self.response.out.write("<html><body>Ok</body></html>")
    else:
        self.response.out.write("<html><body>Login as Admin</body></html>")
 
class LISettings(db.Model):
  user = db.UserProperty()
  time = db.DateTimeProperty(auto_now_add=True)
  ipadresas = db.StringProperty()
  codename = db.StringProperty(required=True)
  liset1 = db.StringProperty()
  liset2 = db.StringProperty()
  liset3 = db.StringProperty()
  liset4 = db.StringProperty()


#def main():
app = webapp.WSGIApplication([('/lisettings', MainHandler)],
                                       debug=True)
#  wsgiref.handlers.CGIHandler().run(application)
#  run_wsgi_app(application)


#if __name__ == '__main__':
#  main()


