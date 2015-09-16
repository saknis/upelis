#!/usr/bin/env python
#
import os
import re
#import wsgiref.handlers
from google.appengine.api import users
#from google.appengine.ext import webapp
import webapp2 as webapp

class MainHandler(webapp.RequestHandler):

  def get(self, album_key1, album_key2, album_key3):

    parts = album_key2.split(".")
    parts.reverse()
    parts.append('')
    parts.append('')
    parts.append('')
#    parts = ['html','lt','aps']
    [ext,lang,aps]=parts[:3]
    greeting = album_key1+"   "+album_key2+"   plet: "+ext+"   kalba: "+lang+"   apsaug: "+aps+"   "+album_key3
    self.response.out.write("<html><body> %s </body></html>" % (greeting))
 
class MainHandler1(webapp.RequestHandler):

  def get(self, album_key2, album_key3):

    parts = album_key2.split(".")
    parts.reverse()
    parts.append('')
    parts.append('')
    parts.append('')
#    parts = ['html','lt','aps']
    [ext,lang,aps]=parts[:3]
    album_key1='a'
    greeting = "1 "+album_key1+"   "+album_key2+"   plet: "+ext+"   kalba: "+lang+"   apsaug: "+aps+"   "+album_key3
    self.response.out.write("<html><body> %s </body></html>" % (greeting))
 


#def main():
app = webapp.WSGIApplication([('/upelis-aaa-(.*)/([-\w]+)', MainHandler1),('/upelis-([-\w]+)-(.*)/([-\w]+)', MainHandler)],
                                       debug=True)
#  wsgiref.handlers.CGIHandler().run(application)


#if __name__ == '__main__':
#  main()


