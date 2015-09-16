#!/usr/bin/env python
#
import os
import urllib
import webapp2
import mimetypes

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

class MainHandler(webapp2.RequestHandler):
  def get(self):
    upload_url = blobstore.create_upload_url('/bupload')
    self.response.out.write('<html><body>')
    self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
    self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit"
        name="submit" value="Submit"> </form></body></html>""")
    query = blobstore.BlobInfo.gql("ORDER BY creation DESC")
    wtext="<h1>Files</h1>\n<div>\n\n"
    for greeting in query:
        wtext = wtext + "\n"+('<div><a href="/bserve/%s">VIEW</a> -  <a href="/bservedown/%s">DOWN</a> -  <a href="/bservedel/%s">DELETE</a> -  %s -  %s -  %s -  %s</div>' % (greeting.key(),greeting.key(),greeting.key(),greeting.filename,greeting.content_type,greeting.creation,greeting.size))+"\n"
    wtext = wtext + "\n</div>\n"
    self.response.out.write(wtext)
    self.response.out.write("""</body></html>""")


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
    blob_info = upload_files[0]
    self.response.out.write('<html><body>')
    self.response.out.write('File: <a href="/bserve/%s">/bserve/%s</a>' % (blob_info.key(),blob_info.key()))
#    bl = blob_info.properties()
#    for name in bl.keys():
#        bl2 = bl[name]
#        self.response.out.write('%s: %s' % (name,bl2))
    self.response.out.write("""</body></html>""")
#    self.redirect('/bserve/%s' % blob_info.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    mimetypes.init()
    mim = "text/plain"
    blob_info = blobstore.BlobInfo.get(resource)
    mim2 = blob_info.content_type
    if not blobstore.get(resource):
        self.error(404)
    elif mim2 in mimetypes.types_map.values():       
        self.response.headers['Content-Type'] = mim2
        self.response.headers['Content-Disposition'] = "filename=\"%s\"" % str(blob_info.filename)
        self.send_blob(blob_info)
    else:
        self.response.headers['Content-Type'] = mim
        self.response.headers['Content-Disposition'] = "filename=\"%s\"" % str(blob_info.filename)
        self.send_blob(blob_info)
#    self.send_blob(blob_info)

class ServeHandlerDown(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    mimetypes.init()
    mim = "application/octet-stream"
    blob_info = blobstore.BlobInfo.get(resource)
    mim2 = blob_info.content_type
    if not blobstore.get(resource):
        self.error(404)
    elif mim2 in mimetypes.types_map.values():       
        self.response.headers['Content-Type'] = mim2
        self.send_blob(blob_info,save_as=True)
    else:
        self.response.headers['Content-Type'] = mim
        self.send_blob(blob_info,save_as=True)    
#    self.send_blob(blob_info)

class ServeHandlerDel(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    blob_info.delete()
    self.response.out.write("""ok""")

app = webapp2.WSGIApplication([('/bupfiles', MainHandler),
                               ('/bupload', UploadHandler),
                               ('/bserve/([^/]+)?', ServeHandler),
                               ('/bservedel/([^/]+)?', ServeHandlerDel),
                               ('/bservedown/([^/]+)?', ServeHandlerDown)],
                              debug=True)


