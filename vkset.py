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
    vkset1 = ""
    vkset2 = ""
    vkset3 = ""
    vkset4 = ""
    try:
        codelist = db.GqlQuery("SELECT * FROM VKSettings WHERE codename = :1", "vksettings")
        for code in codelist:
            vkset1 = code.vkset1
            vkset2 = code.vkset2
            vkset3 = code.vkset3
            vkset4 = code.vkset4
    except:
        klaida=True
    if not users.is_current_user_admin():
        self.response.out.write("<html><body>Login as Admin</body></html>")
    else:
        path = os.path.join(os.path.dirname(__file__), "vkset.html")
        args = dict(vkset1=vkset1,vkset2=vkset2,vkset3=vkset3,vkset4=vkset4)
        self.response.out.write(template.render(path, args))
  def post(self):
    if users.is_current_user_admin():
        try:
            codelist = db.GqlQuery("SELECT * FROM VKSettings WHERE codename = :1", "vksettings")
            for code in codelist:
                code.delete()
        except:
            klaida=True
        now = datetime.datetime.now()
        code = VKSettings(codename="vksettings")
        code.time = now
        code.ipadresas = os.environ['REMOTE_ADDR']
        code.vkset1 = self.request.get("vkset1")
        code.vkset2 = self.request.get("vkset2")
        code.vkset3 = self.request.get("vkset3")
        code.vkset4 = self.request.get("vkset4")
        code.user = users.get_current_user()
        code.put()
        self.response.out.write("<html><body>Ok</body></html>")
    else:
        self.response.out.write("<html><body>Login as Admin</body></html>")
 
class VKSettings(db.Model):
  user = db.UserProperty()
  time = db.DateTimeProperty(auto_now_add=True)
  ipadresas = db.StringProperty()
  codename = db.StringProperty(required=True)
  vkset1 = db.StringProperty()
  vkset2 = db.StringProperty()
  vkset3 = db.StringProperty()
  vkset4 = db.StringProperty()


#def main():
app = webapp.WSGIApplication([('/vksettings', MainHandler)],
                                       debug=True)
#  wsgiref.handlers.CGIHandler().run(application)
#  run_wsgi_app(application)


#if __name__ == '__main__':
#  main()


