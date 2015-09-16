#!/usr/bin/env python
# .- coding: utf-8 -.
__author__ = 'Nerijus Terebas'


import cgi
import os

#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2 as webapp
#from datetime import datetime
from email.utils import formatdate
from datetime import datetime, timedelta, tzinfo
from google.appengine.api import datastore
from google.appengine.api import datastore_types
#import googledatastore as datastore
#from core.stateMessageHub import createPropertyOnEntity
#from googledatastore.helper import set_property
import PyRSS2Gen
import sys
import re
from HTMLParser import HTMLParser  
from upelis_settings import *
cmsname2=CMSNAME
cmspath2=CMSPATH
cmstrans2=CMSTRANS
rsstitle2=RSSTITLE

_DEBUG = True
def urlhost2():
	if os.environ['HTTPS']=="off":
		return str('http://'+os.environ['HTTP_HOST'])
	else:
		return str('https://'+os.environ['HTTP_HOST'])

class MyHTMLParser(HTMLParser):

  def __init__(self):
    HTMLParser.__init__(self)
    self.recording = 0 
    self.data = []
  def handle_starttag(self, tag, attrs):
    if tag == 'h1':
      self.recording = 1 


  def handle_endtag(self, tag):
    if tag == 'h1':
      self.recording -=1 
#      print "Encountered the end of a %s tag" % tag 

  def handle_data(self, data):
    if self.recording:
      self.data.append(data)

class Sitemap(webapp.RequestHandler):

  def get(self):

    baseurl=urlhost2()+"/"+cmspath2+"-"
    query = datastore.Query('Page').Order(('created', datastore.Query.DESCENDING),'name');
#    order = query.order.add()
#    order.property.name = 'created'
#    order.direction = datastore.PropertyOrder.DESCENDING
    entities = query.Get(1000)
#    req = datastore.RunQueryRequest()
#    query = req.query
#    height_desc = datastore.Query()
#    height_desc.kind.add().name = 'Page'
#    order = height_desc.order.add()
#    order.property.name = 'created'
#    order.direction = datastore.PropertyOrder.DESCENDING
#    query.limit = 1000
#    entities = self.datastore.run_query(req)
    nowdt = datetime.now()
    rss = PyRSS2Gen.RSS2( 
        title = rsstitle2,
        link = urlhost2()+"/rss",
        description = rsstitle2,
        lastBuildDate = formatdate(float(nowdt.strftime('%s')))
    )
    for entity in entities:
        content=entity['content']
#        sss1=datetime.strptime(str(entity['created']).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')(entity['created']).strftime("%a, %d %b %Y %H:%M:%S")
        nowdt = entity['created']
        sss1=formatdate(float(nowdt.strftime('%s')))
        sss2=entity['rssrodyti']
        sss3=entity['name']
        langget=self.request.get('lang')
        if langget:
            sss3a = sss3.split("-")
            sss3aa=sss3a[-1]
            sss3b = sss3aa.split(".")
            sss3b.reverse()
            sss3b.append('')
            sss3b.append('')
            sss3b.append('')
            [ext,lang,aps]=sss3b[:3]
            if not langget == lang:
                sss2 = False
        parser = HTMLParser()
        content_un = parser.unescape(content)
        
        match = re.search (r'<h1>(\w+)</h1>', content_un)
        pav="----------"
        if match and len(match.group(0))>0:
            pav=match.group(0)


        if sss2:
            sss4=""
            try:
                p = MyHTMLParser()
                p.feed(p.unescape(entity['content']))
                sss4=p.data[0]
                p.close()
            except:
                sss4=""
            m = PyRSS2Gen.RSSItem( 
                title = sss3,
                description = sss4,
                guid = PyRSS2Gen.Guid( urlhost2()+"/"+cmspath2+"-" + sss3),
                pubDate = sss1, # XXX: 
            )
            rss.items.append( m ) 
#    self.response.headers['Content-Type'] = 'application/rss+xml'
    self.response.headers['Content-Type'] ='application/rss+xml; name="nt.xml"' 
    self.response.headers['Content-Disposition'] = 'filename="nt.xml"'
    res = rss.to_xml(encoding='utf-8')
    self.response.out.write(res)

#def main():

url_map = [('/rss', Sitemap),('/rss.xml', Sitemap)]
app = webapp.WSGIApplication(url_map,debug=True)
#  run_wsgi_app(application)

#if __name__ == '__main__':
#  main()
