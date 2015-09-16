#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
##########################################################################
ZipMe : GAE Content Downloader
##########################################################################
Just add this lines in your app.yaml :

- url: /zipme
  script: zipme.py

##########################################################################
"""                                                             # manatlan

#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2 as webapp
from google.appengine.api import users

#import wsgiref.handlers
import zipfile
import datetime
import os,re,sys,stat
from cStringIO import StringIO

def createZip(path):

    def walktree (top = ".", depthfirst = True):
        names = os.listdir(top)
        if not depthfirst:
            yield top, names
        for name in names:
            try:
                st = os.lstat(os.path.join(top, name))
            except os.error:
                continue
            if stat.S_ISDIR(st.st_mode):
                for (newtop, children) in walktree (os.path.join(top, name),
                                                    depthfirst):
                    yield newtop, children
        if depthfirst:
            yield top, names

    list=[]
    for (basepath, children) in walktree(path,False):
          for child in children:
              f=os.path.join(basepath,child)
              if os.path.isfile(f):
                    f = f.encode(sys.getfilesystemencoding())
                    list.append( f )

    f=StringIO()
    file = zipfile.ZipFile(f, "w")
    for fname in list:
        nfname=os.path.join(os.path.basename(path),fname[len(path)+1:])
        file.write(fname, nfname , zipfile.ZIP_DEFLATED)
    file.close()

    f.seek(0)
    return f


class ZipMaker(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin():
            folder = os.path.dirname(__file__)
            self.response.headers['Cache-Control'] = 'public, max-age=60'
#			self.response.headers['Last-Modified'] = lastmod.strftime("%a, %d %b %Y %H:%M:%S GMT")
            expires = datetime.datetime.now() + datetime.timedelta(minutes=1)
            self.response.headers['Expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT") 
            ffdate = datetime.datetime.now()
            fdate = ffdate.strftime("%d-%b-%Y_%H-%M-%S")
            self.response.headers['Content-Type'] ='application/zip; name="zipme_%s_%s.zip"' % (fdate, os.path.basename(folder)) 
            self.response.headers['Content-Disposition'] = 'attachment; filename="zipme_%s_%s.zip"' % (fdate, os.path.basename(folder))
            fid=createZip(folder)
            while True:
                buf=fid.read(2048)
                if buf=="": break
                self.response.out.write(buf)
            fid.close()
        else:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write("<a href=\"%s\">You must be admin</a>." %
                                    users.create_login_url("/zipme"))

#def main():
app = webapp.WSGIApplication(
                                       [('/zipme', ZipMaker)],
                                       debug=False)
#    wsgiref.handlers.CGIHandler().run(application)
#    run_wsgi_app(application)

#if __name__ == "__main__":
#    main()
