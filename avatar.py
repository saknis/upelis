#!/usr/bin/env python

import re
import cgi
import urllib
import datetime
import os
import sys
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import urlfetch_errors
#from template import header, footer
from Picasa import Picasa
#import wsgiref.handlers
#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2 as webapp
from UserAdd import UserAdd
from UserAdd import Vartotojai

UserAdd()

class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>')
    self.response.out.write("""
          <h1>Find Google Plus URL by Email</h1>
          <form action="/avatar2" method="get">
                <div>Google user Email: <INPUT name=user size=80 value=""> </div>
                <div><INPUT name=Submit type=submit value="      Send      "> <INPUT name=Submit2 type=reset value="     Reset     "> </div>
          </form>
        </body>
      </html>""")

class MainHandler(webapp.RequestHandler):

  def get(self):
    user = self.request.get("user")
    user = user.strip()
    avatar=getphoto(user)
    plid=getplius(user)
    self.response.out.write(user+"<br>");
    if avatar:
      self.response.out.write("<img src=\""+str(avatar)+"\" border=\"0\"><br>");
    if plid:
      entitiesRx  = re.compile("[^0-9]")
      plid09 = entitiesRx.sub("", plid)
      self.response.out.write("<br><a href=\"http://plus."+str(plid)+"\">"+"plus."+str(plid)+ "</a>");
      if checkurl("http://code.google.com/u/"+str(plid09)+"/"):
        self.response.out.write("<br><a href=\"http://code.google.com/u/"+str(plid09)+"/\">"+"code.google.com/u/"+str(plid09)+ "/</a>");
    if checkurl("http://code.google.com/u/"+str(user)+"/"):
      self.response.out.write("<br><a href=\"http://code.google.com/u/"+str(user)+"/\">"+"http://code.google.com/u/"+str(user)+ "/</a>");


def checkurl(url):
    try:
        yra=False
        fol=False
        result = urlfetch.fetch(url=url,
                        	method=urlfetch.GET,
                        	follow_redirects=fol)
        yra=True
        if result.status_code == 404:
            return False
        if yra:
            return url
    except urlfetch_errors.InvalidURLError, message:
            return False
    except urlfetch_errors.DownloadError, message:
            return False
    except urlfetch_errors.ResponseTooLargeError, message:
            return False
    except urlfetch_errors.Error, message:
            return False

def getphoto(useris):
    try:
        yra=False
        if True:
            f = urllib.urlopen("http://picasaweb.google.com/data/feed/api/user/%s?kind=album" % useris)
            list = Picasa().albums(f.read())
            for name in list.keys():
                album = list[name]
                if name.find('ProfilePhotos') == 0:
                    f = urllib.urlopen("http://picasaweb.google.com/data/feed/api/user/%s/album/%s?kind=photo" % (useris,name))
                    list = Picasa().photos(f.read())
                    for photo in list:
                        phototurim = photo.thumbnail #photo.webpage
                        yra=True
                        break
                    break
                if name == "Profile_photosActive":
                    f = urllib.urlopen("http://picasaweb.google.com/data/feed/api/user/%s/album/%s?kind=photo" % (useris,"Profile_photosActive"))
                    list = Picasa().photos(f.read())
                    for photo in list:
                        phototurim = photo.thumbnail #photo.webpage
                        yra=True
                        break
                    break
        else:
            yra=False
        if yra:
            return phototurim
        else:
            return False
    except:
       return False

      

def getplius(useris):
    try:
        yra=False
        if True:
            f = urllib.urlopen("http://picasaweb.google.com/data/feed/api/user/%s?kind=album" % useris)
            data=f.read()
#        r = re.compile("(user'/><title.*>)([\s\S]*)(</title>)")
#        plusid = r.search(data).group(2)
            r = re.compile("(alternate.*)(google.com/[\d]*)(\'/)")
#        r = re.compile("(<link rel=\x27alternate\x27 type=\x27text/html\x27 href=\x27https://picasaweb.google.com/)(.*)(\x27/>)")
            plusid = r.search(data).group(2)
            yra=True
        if yra:
            return plusid
        else:
            return False
    except:
       return False

      
#def main():
app = webapp.WSGIApplication([('/avatar', MainPage),('/avatar2', MainHandler)],
                                       debug=True)
#  wsgiref.handlers.CGIHandler().run(application)
#    run_wsgi_app(application)


#if __name__ == '__main__':
#    main()
