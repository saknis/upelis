#!/usr/bin/env python

__author__ = 'Nerijus Terebas'

import re
import cgi
import sys
#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2 as webapp
import feedparser

_DEBUG = True

class FeedTest(webapp.RequestHandler):
  def get(self,feednr):

    # Wrapping in a huge try/except isn't the best approach. This is just 
    # an example for how you might do this.
    url=[]	
    url.append('http://googleappengine.blogspot.com/feeds/posts/default?alt=rss')
    url.append('http://www.lrytas.lt/rss/?tema=25')
    url.append('http://www.delfi.lt/rss/feeds/channels/mokslas.xml')
    url.append('http://www.15min.lt/mokslasit/rss')

    entitiesRx  = re.compile("[^0-9]")
    feednr = entitiesRx.sub("", feednr)
    error401 = True
    ooo=""
    try:
        d = feedparser.parse(url[int(feednr)])
        ooo="<h1><a href=\""+d.feed.link+"\">"+d.feed.title+"</a></h1>\n"
        for fff in d['items']:
          ooo=ooo+"<a href=\""+fff.link+"\">"+fff.title+"</a><br>\n"
        error401 = False
    except Exception, e:
      error401 = True
      errtext =  cgi.escape(str(sys.exc_info()[0])) + ' ' + cgi.escape(str(sys.exc_info()[1])) + ' ' + cgi.escape(str(sys.exc_info()[2]))

    if error401:
      self.response.out.write("Error: "+errtext)
    else:
      self.response.out.write(ooo)

#def main():
app = webapp.WSGIApplication([('/appfeed/(.*)', FeedTest)], debug=_DEBUG)
#  run_wsgi_app(application)

