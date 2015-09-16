#!/usr/bin/env python
#
import cgi
import os
import re
#import wsgiref.handlers
import datetime
import urllib
import urlparse
#import magic
from google.appengine.api import users
#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2 as webapp
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types
import mimetypes



_DEBUG = True

class UploadFile(webapp.RequestHandler):
  def get(self):
    wtext=""
    pg=self.request.get('pg')
    if pg:
      pg = int(pg)
    else:
      pg=0
  
    try:
      query = db.GqlQuery("SELECT * FROM Files ORDER BY date DESC")
#  query = db.GqlQuery("SELECT * FROM Commentsrec WHERE rodyti = :1, author = :2 ORDER BY date DESC", '1',users.GetCurrentUser())
      greetings = query.fetch(50,pg*50)
      co=query.count()
    except:
      klaida=True
      co=0
      greetings = []
  
    i=0
    ii=0
    bbb=""
    while i<=co:
      i=i+50
      if ii == pg:
        bbb=bbb+' '+str(ii)
      else:
        bbb=bbb+' '+"<a href=\"/upfiles?pg="+ str(ii) +"\">"+ str(ii) +"</a>"
      ii=ii+1
        
    wtext=wtext+"<h1>Files</h1>\n<div><div style=\"text-align: center;\">"+bbb+"</div>\n\n"
    for greeting in greetings:
          fname=os.path.basename(("%s" % greeting.filename))
          wtext = wtext + "\n"+('<div><a href="/src/%s/%s">VIEW</a> <a href="/delfile?id=%s">DELETE</a> /src/%s/%s</div>' % (greeting.key(),fname,greeting.key(),greeting.key(),fname))+"\n"
          wtext = wtext + "\n"+('<div>%s     %s  </div>' % (greeting.date, greeting.filename))+"\n"
    wtext = wtext + "\n</div>\n"+"""
              <div>
              <form action="/upfiles" enctype="multipart/form-data" method="post">
                <div><label>Photo:</label></div>
                <div><input type="file" name="file" /></div>
                <div><input type="submit" value="Submit Comment" /></div>
              </form>
              </div>"""
    self.response.headers['Content-Type'] = "text/html"
    self.response.out.write(wtext)
  
  def post(self):
    thefile = self.request.params.get('file', None) 
    image_data = None 
    if thefile is not None: 
        try: 
            image_data = db.Blob(thefile.value) 
        except: 
            pass 
        greeting = Files()
        if users.get_current_user():
        	greeting.author = users.get_current_user()
        greeting.content = ""
        greeting.filename = cgi.escape(thefile.filename).strip()
        simbsafe  = re.compile("[^0-9a-zA-Z\x2D\x5F\x2E]")
        greeting.filename = simbsafe.sub("", greeting.filename)
        greeting.filedata = image_data
        greeting.rodyti = True
        greeting.ipadresas = os.environ['REMOTE_ADDR']
        greeting.put()
    self.redirect('/upfiles')
class DownFile(webapp.RequestHandler):
  def get(self, viewtype, postkey, dummy_filename, dummy_filename_ext): 
    try:
        greeting = db.get(postkey)
        if greeting.filedata:
          simbsafe  = re.compile("[^0-9a-zA-Z]")
          dummy_filename_ext = simbsafe.sub("", dummy_filename_ext)
          mimetypes.init()
          mim="application/octet-stream"
          dummy_filename_ext2=(".%s" % dummy_filename_ext)
          if dummy_filename_ext2 in mimetypes.types_map:
            mim=mimetypes.types_map[dummy_filename_ext2]
          self.response.headers['Cache-Control'] = 'public, max-age=60'
          expires = datetime.datetime.now() + datetime.timedelta(minutes=1)
          self.response.headers['Expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT") 
          self.response.headers['Content-Type'] = mim
          self.response.out.write(greeting.filedata)
        else:
          self.response.out.write("No image")
    except:
        self.error(404)
        self.response.out.write('Not found')
class DelFile(webapp.RequestHandler):
  def get(self):
    try:
        comm = db.get(self.request.get("id"))
        if (users.GetCurrentUser() and users.get_current_user() == comm.author) or users.is_current_user_admin():
            comm.delete()
    except:
        klaida=True
    self.redirect('/upfiles')

class Files(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  filename = db.StringProperty(multiline=False)
  filedata = db.BlobProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  ipadresas = db.StringProperty()
  rodyti = db.BooleanProperty()

#def main():
app = webapp.WSGIApplication([
      (r'/(cat|thumb|src)/([-\w]+)/([0-9a-zA-Z\x2D\x5F]+)\.([0-9a-zA-Z]+)', DownFile), 
      ('/upfiles', UploadFile),
      ('/delfile', DelFile),
    ], debug=_DEBUG)
#    wsgiref.handlers.CGIHandler().run(application)
#    run_wsgi_app(application)


#if __name__ == '__main__':
#  main()
