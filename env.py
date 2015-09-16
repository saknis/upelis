#!/usr/bin/env python
#
import os
#import wsgiref.handlers
from google.appengine.api import users
#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2 as webapp

class MainHandler(webapp.RequestHandler):

  def get(self):

    user = users.get_current_user()
    greeting = ''
    if user:
      if users.is_current_user_admin():
        for name, value in os.environ.items():
                 aaa = "%s\t= %s <br/>" % (name, value)
                 greeting = greeting + aaa
      else:
        greeting = "Welcome, " +user.nickname()+"! <a href=\""+users.create_logout_url(self.request.uri)+"\">sign out</a>"
        greeting = greeting + " and <a href=\""+users.create_login_url(self.request.uri)+"\">sign in on Administrator</a>."
    else:
      greeting = "<a href=\""+users.create_login_url(self.request.uri)+"\">Sign in on Administrator</a>."
    self.response.out.write("<html><body> %s </body></html>" % (greeting))
 


#def main():
app = webapp.WSGIApplication([('/env', MainHandler)],
                                       debug=True)
#  wsgiref.handlers.CGIHandler().run(application)
#  run_wsgi_app(application)


#if __name__ == '__main__':
#  main()


