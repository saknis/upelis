#!/usr/bin/env python

__author__ = 'Nerijus Terebas'


import cgi
import os

#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2 as webapp
from datetime import datetime
from google.appengine.api import datastore
from google.appengine.api import datastore_types
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

class Sitemap(webapp.RequestHandler):

  def get(self):

    baseurl=urlhost2()+"/"+cmspath2+"-"
    query = datastore.Query('Page')
    entities = query.Get(1000)
    bbb="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
    for entity in entities:
        sss1=str(entity['modified'])
        sss2=entity['sitemaprodyti']
        sss3=str(entity['sitemapfreq'])
        sss4=str(entity['sitemapprio'])
        if sss2:
            ttt = datetime.strptime(sss1.split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            aaa="\t<url>\n\t\t<loc>%s%s</loc>\n\t\t<lastmod>%s</lastmod>\n\t\t<changefreq>%s</changefreq>\n\t\t<priority>%s</priority>\n\t</url>\n" % (baseurl,entity['name'],ttt,sss3,sss4)
            bbb=bbb+aaa
    bbb=bbb+"</urlset>\n"
    self.response.headers['Content-Type'] = ' text/xml'
    self.response.out.write(bbb)

#def main():

url_map = [('/sitemap.xml', Sitemap)]
app = webapp.WSGIApplication(url_map,debug=True)
#  run_wsgi_app(application)

#if __name__ == '__main__':
#  main()
