#!/usr/bin/env python
#
# Copyright 2008 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Image Sharing, a simple picture sharing application running on App Engine.

Specific App Engine features demonstrated include:
 * the Image API, which is used for creating thumbnails of uploaded pictures
 * the Datastore API, which is used to store both the metadata for and
   the actual content of pictures
 * the ListProperty type, which is used for efficient tagging support, and
 * support for file uploads using the WebOb request object

We use the webapp.py WSGI framework and the Django templating
language, both of which are documented in the App Engine docs
(http://appengine.google.com/docs/).
"""

__author__ = 'Fred Wulff'
__authormod__ = 'Nerijus Terebas'


import cgi
import os

from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext import db
#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2 as webapp
from google.appengine.ext.webapp import template

from wiki import Page
from UserAdd import UserAdd
from UserAdd import Vartotojai
from Start import DinCode
#import wsgiref.handlers

import locale 
import gettext 

import urllib
import facebookoauth
from facebookoauth import FBUser
from upelis_settings import *

_DEBUG = DEBUG
_mailsender=MAILSENDER
_mailrcptto=MAILRCPTTO


cmsname2=CMSNAME
cmspath2=CMSPATH
cmstrans2=CMSTRANS
site1a=SITE1A
site1b=SITE1B
site2a=SITE2A
site2b=SITE2B
sitedown=SITEDOWN

current_locale = CURLOCALE
kalbos=LANGUAGES
kalboseile=LANGUAGESNR
kalbossort = LANGUAGESSORT
locale_path = LOCALEPATH 
fileext=FILEEXT
lang=LANG
#_kalbhtml = LANGHTML
_kalbhtml = "<li><a href=\"/"+cmspath2+"-%s-%s.%s\"><img src=\"/static/images/flag/%s.gif\" border=\"0\" alt=\"\"></img></a></li>"

langdef=lang
lang1 = gettext.translation (cmstrans2, locale_path, [current_locale] , fallback=True) 
_ = lang1.ugettext

# Set to true if we want to have our webapp print stack traces, etc
_titauth = TITAUTH
#_titauth = "Nerijus Terebas"
_version=VERSION

UserAdd()

# Makes the tags defined by templatetags/basetags.py usable
# by templates rendered in this file
template.register_template_library('templatetags.basetags')

def urlhost2():
	if os.environ['HTTPS']=="off":
		return str('http://'+os.environ['HTTP_HOST'])
	else:
		return str('https://'+os.environ['HTTP_HOST'])


class Album(db.Model):
  """An album is an organizational unit for pictures.

  Properties:
    name: sanitized, user entered name for the album
    creator: Google Account of the person who created the album
    created_date: DateTime the album was created
  """

  name = db.StringProperty()
  creator = db.UserProperty()
  created_date = db.DateTimeProperty(auto_now_add=True)


class Picture(db.Model):
  """Storage for a picture and its associated metadata.

  Properties:
    submitter: Google Account of the person who submitted the picture
    submitted_date: DateTime the picture was submitted
    title: sanitized, user entered title for the picture
    caption: sanitized, user entered caption for the picture
    album: reference to album the picture is in
    tags: a StringListProperty of tags for the picture
    data: data for the original picture, converted into png format
    thumbnail_data: png format data for the thumbnail for this picture
  """

  submitter = db.UserProperty()
  submitted_date = db.DateTimeProperty(auto_now_add=True)
  title = db.StringProperty()
  caption = db.StringProperty(multiline=True)
  album = db.ReferenceProperty(Album, collection_name='pictures')
  tags = db.StringListProperty()
  data = db.BlobProperty()
  thumbnail_data = db.BlobProperty()


class ImageSharingBaseHandler(webapp.RequestHandler):
  """Base Image Sharing RequestHandlers with some convenience functions."""

  def template_path(self, filename):
    """Returns the full path for a template from its path relative to here."""
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, os.path.join('templates', filename))
    return path

  def render_to_response(self, filename, languag, template_args):
    if languag in kalbos:
      kalb=kalbos[languag]
    else:
      kalb=kalbos[langdef]
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    kalb2=kalb.replace("_", "-")
    """Renders a Django template and sends it to the client.

    Args:
      filename: template path (relative to this file)
      template_args: argument dict for the template
    """
    template_args.setdefault('current_uri', self.request.uri)
    values = {
      'noedit': '1',
      'imgshar': '1',
      'request': self.request,
      'user': users.GetCurrentUser(),
      'isadmin': users.is_current_user_admin(),
      'self_url': self.request.uri,
      'login_url': users.CreateLoginURL(self.request.uri),
      'logout_url': users.CreateLogoutURL(self.request.uri),
      'kalba': kalb2,
      'application_name': _titauth,
      'msgtext_logout': _("logout"),
      'msgtext_login': _("login"),
      'msgtext_header': _("header %(cmsname)s") % {'cmsname': cmsname2},
      'gallery': _("Gallery"),
      'imgshar_msg_1': _("Imgshar msg 1"),
      'imgshar_msg_2': _("Imgshar msg 2"),
      'imgshar_msg_3': _("Imgshar msg 3"),
      'imgshar_msg_4': _("Imgshar msg 4"),
      'imgshar_msg_5': _("Imgshar msg 5"),
      'imgshar_msg_6': _("Imgshar msg 6"),
      'imgshar_msg_7': _("Imgshar msg 7"),
      'imgshar_msg_8': _("Imgshar msg 8"),
      'imgshar_msg_9': _("Imgshar msg 9"),
      'imgshar_msg_10': _("Imgshar msg 10"),
      'imgshar_msg_11': _("Imgshar msg 11"),
      'imgshar_msg_12': _("Imgshar msg 12"),
      'imgshar_msg_14': _("Imgshar msg 14"),
      'imgshar_msg_15': _("Imgshar msg 15"),
      'imgshar_msg_16': _("Imgshar msg 16"),
      'imgshar_msg_17': _("Imgshar msg 17"),
      'imgshar_msg_18': _("Imgshar msg 18"),
      'imgshar_msg_19': _("Imgshar msg 19"),
      'imgshar_msg_20': _("Imgshar msg 20"),
      'imgshar_msg_21': _("Imgshar msg 21"),
      'imgshar_msg_22': _("Imgshar msg 22"),
      'imgshar_msg_23': _("Imgshar msg 23"),
      'imgshar_msg_24': _("Imgshar msg 24"),
      'imgshar_msg_25': _("Imgshar msg 25"),
      'imgshar_msg_26': _("Imgshar msg 26"),
      'imgshar_msg_27': _("Imgshar msg 27"),
      'imgshar_msg_28': _("Imgshar msg 28"),
      'imgshar_msg_29': _("Imgshar msg 29"),
      'imgshar_msg_30': _("Imgshar msg 30"),
      'fbuser': self.fb_current_user,
      'fblogin_url': "/auth/login?continue=%s" % (urllib.quote(self.request.uri)),
      'fblogout_url': "/auth/logout?continue=%s" % (urllib.quote(self.request.uri)),
      'cmspath':cmspath2
    }
    values.update(template_args)
    self.response.headers['X-Powered-By'] = cmsname2+'/'+_version
    appon=False
    try:
        codedb = db.GqlQuery("SELECT * FROM DinCode WHERE codename = :1", "start")
        for thiscode in codedb:
            thiscode = thiscode.codetext
        appon = eval(thiscode)
    except:
        appon=False
    if appon:
      self.response.out.write(
          template.render(self.template_path(filename), values)
      )
    else:
      disablecode = "<html><body>Disable, swith to on</body></html>"
      try:  
          codedb = db.GqlQuery("SELECT * FROM DinCode WHERE codename = :1", "disable")
          for thiscode in codedb:
              disablecode = thiscode.codetext
      except:
          disablecode = "<html><body>Disable, swith to on</body></html>"
      self.response.out.write(disablecode)
  @property
  def fb_current_user(self):
      """Returns the logged in Facebook user, or None if unconnected."""
      if not hasattr(self, "_fb_current_user"):
          self._fb_current_user = None
          user_id = facebookoauth.parse_cookie(self.request.cookies.get("fb_user"))
          if user_id:
              self._fb_current_user = FBUser.get_by_key_name(user_id)
      return self._fb_current_user


class ImageSharingAlbumIndex(ImageSharingBaseHandler):
  """Handler for listing albums."""

  def get(self, rparameters):
    """Lists all available albums."""
    parts = rparameters.split(".")
    parts.reverse()
    parts.append('')
    parts.append('')
    parts.append('')
    [ext,lang,aps]=parts[:3]
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('pic', textaps+name, ext, name))
    page3.content = text

    albums = Album.all().order('-created_date')
    page2 = Page.load(page_name2)
    self.render_to_response('pic_index.html',lang, {
        'plet': lang+'.'+fileext,
        'kalbos': page3,
        'albums': albums,
        'menu': page2,
      })


class ImageSharingAlbumCreate(ImageSharingBaseHandler):
  """Handler for creating a new Album via form."""

  def get(self, rparameters):
    """Lists all available albums."""
    parts = rparameters.split(".")
    parts.reverse()
    parts.append('')
    parts.append('')
    parts.append('')
    [ext,lang,aps]=parts[:3]
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('picnew', textaps+name, ext, name))
    page3.content = text
    """Displays the album creation form."""
    page2 = Page.load(page_name2)
    self.render_to_response('pic_new.html',lang, {'plet': lang+'.'+fileext,'menu': page2,'kalbos': page3})

  def post(self, rparameters):
    """Processes an album creation request."""
    parts = rparameters.split(".")
    parts.reverse()
    parts.append('')
    parts.append('')
    parts.append('')
    [ext,lang,aps]=parts[:3]
    Album(name=cgi.escape(self.request.get('albumname')),
          creator=users.get_current_user()).put()
    self.redirect('/'+cmspath2+'-pic-'+ lang+"."+ext)

PICTURES_PER_ROW = 5

class ImageSharingAlbumView(ImageSharingBaseHandler):
  """Handler for viewing the pictures in a particular album."""

  def get(self, rparameters, album_key):
    """Lists all available albums."""
    parts = rparameters.split(".")
    parts.reverse()
    parts.append('')
    parts.append('')
    parts.append('')
    [ext,lang,aps]=parts[:3]
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('picalbum', textaps+name, ext+'/'+album_key, name))
    page3.content = text
    """Displays a single album.

    Note that in this and later handlers, the args come
    from a capturing group in the WSGIApplication specification.
    See the webapp framework docs for more info.

    Args:
      album_key: the datastore key for the Album to view.
    """
    pics = []
    num_results = 0
    try:
      album = db.get(album_key)
      albumkey = album.key()
      albumname = album.name

      for picture in album.pictures:
        if num_results % PICTURES_PER_ROW == 0:
          current_row = []
          pics.append(current_row)
        current_row.append(picture)
        num_results += 1

    except:
      albumkey = "error404"
      albumname = "Not Found 404"
    page2 = Page.load(page_name2)

    self.render_to_response('pic_album.html',lang, {
        'plet': lang+'.'+fileext,
        'kalbos': page3,
        'menu': page2,
        'num_results': num_results,
        'album_key': albumkey,
        'pics': pics,
        'album_name': albumname
      })


class ImageSharingUploadImage(ImageSharingBaseHandler):
  """Handler for uploading images."""

  def get(self, rparameters, album_key):
    """Lists all available albums."""
    parts = rparameters.split(".")
    parts.reverse()
    parts.append('')
    parts.append('')
    parts.append('')
    [ext,lang,aps]=parts[:3]
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('picupload', textaps+name, ext+'/'+album_key, name))
    page3.content = text
    """Display the image upload form.

    Args:
      album_key: datastore key for the album to upload the image to
    """
    cerr = False
    try:
        album = db.get(album_key)
        albumname = album.name
        albumkey = album.key()
    except:
        cerr = True
    if not cerr:
        page2 = Page.load(page_name2)
        self.render_to_response('pic_upload.html',lang, {
            'plet': lang+'.'+fileext,
            'kalbos': page3,
            'menu': page2,
            'album_key': album.key(),
            'album_name': album.name
          })
    else:
        self.response.out.write("Error")

  def post(self, rparameters, album_key):
    parts = rparameters.split(".")
    parts.reverse()
    parts.append('')
    parts.append('')
    parts.append('')
    [ext,lang,aps]=parts[:3]
    """Process the image upload form.

    We also generate the thumbnail for the picture at this point.

    Args:
      album_key: datastore key for the album to add the image to
    """
    album = db.get(album_key)
    if album is None:
      self.error(400)
      self.response.out.write('Couldn\'t find specified album')

    title = cgi.escape(self.request.get('title'))
    caption = cgi.escape(self.request.get('caption'))
    tags = cgi.escape(self.request.get('tags')).split(',')
    tags = [tag.strip() for tag in tags]
    # Get the actual data for the picture
    img_data = self.request.POST.get('picfile').file.read()

    try:
      img = images.Image(img_data)
      # Basically, we just want to make sure it's a PNG
      # since we don't have a good way to determine image type
      # through the API, but the API throws an exception
      # if you don't do any transforms, so go ahead and use im_feeling_lucky.
      img.im_feeling_lucky()
      png_data = img.execute_transforms(images.PNG)
#      png_data = img

      img.resize(60, 100)
      thumbnail_data = img.execute_transforms(images.PNG)

      Picture(submitter=users.get_current_user(),
              title=title,
              caption=caption,
              album=album,
              tags=tags,
              data=png_data,
              thumbnail_data=thumbnail_data).put()

      self.redirect('/'+cmspath2+'-picalbum-'+ lang+"."+ext+'/%s' % album.key())
    except images.BadImageError:
      self.error(400)
      self.response.out.write(
          'Sorry, we had a problem processing the image provided.')
    except images.NotImageError:
      self.error(400)
      self.response.out.write(
          'Sorry, we don\'t recognize that image format.'
          'We can process JPEG, GIF, PNG, BMP, TIFF, and ICO files.')
    except images.LargeImageError:
      self.error(400)
      self.response.out.write(
          'Sorry, the image provided was too large for us to process.')

class ImageSharingShowImage(ImageSharingBaseHandler):
  """Handler for viewing a single image.

  Note that this doesn't actually serve the picture, only the page
  containing it. That happens in ImageSharingServeImage.
  """

  def get(self, rparameters, pic_key):
    """Lists all available albums."""
    parts = rparameters.split(".")
    parts.reverse()
    parts.append('')
    parts.append('')
    parts.append('')
    [ext,lang,aps]=parts[:3]
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('picshowimage', textaps+name, ext+'/'+pic_key, name))
    page3.content = text
    """Renders the page for a single picture.

    Args:
      pic_key: key for the Picture model for the picture to display
    """

    cerr = False
    try:
        pic = db.get(pic_key)
        pictitle = pic.title
        piccaption = pic.caption
        pictags = pic.tags
        pickey = pic.key()
        picalbumkey = pic.album.key()
    except:
        cerr = True
    if not cerr:
        page2 = Page.load(page_name2)
        self.render_to_response('pic_show_image.html',lang, {
            'plet': lang+'.'+fileext,
            'kalbos': page3,
            'menu': page2,
            'pic': pic,
            'image_key': pic.key(),
        })
    else:
        self.response.out.write("Error")
    


class ImageSharingServeImage(webapp.RequestHandler):
  """Handler for dynamically serving an image from the datastore.

  Very simple - it just pulls the appropriate data out of the datastore
  and serves it.
  """

  def get(self, display_type, rparameters, pic_key):
    """Dynamically serves a PNG image from the datastore.

    Args:
      type: a string describing the type of image to serve (image or thumbnail)
      pic_key: the key for a Picture model that holds the image
    """
    try:
      image = db.get(pic_key)
      data = image.data
      th_data = image.thumbnail_data
    except:
      from bindata import PictureErr
      image = PictureErr()
      data = image.data
      th_data = image.thumbnail_data

    if display_type == 'image':
      self.response.headers['Content-Type'] = 'image/png'
      from bindata import LogoButton
      imagelogo=LogoButton()
      data2=imagelogo.data
      xpng = images.Image(data)
      ypng = images.Image(data2)
      org_width, org_height = xpng.width, xpng.height
      composite = images.composite([(xpng, 0, 0, 1.0, images.TOP_LEFT),(ypng, 0, 0, 1.0, images.BOTTOM_RIGHT)], org_width, org_height,0,images.PNG) 
      self.response.out.write(composite)
    elif display_type == 'thumbnail':
      self.response.headers['Content-Type'] = 'image/png'
      self.response.out.write(th_data)
    else:
      self.error(500)
      self.response.out.write(
          'Couldn\'t determine what type of image to serve.')

class ImageSharingSearch(ImageSharingBaseHandler):
  """Handler for searching pictures by tag."""

  def get(self, rparameters):
    """Lists all available albums."""
    parts = rparameters.split(".")
    parts.reverse()
    parts.append('')
    parts.append('')
    parts.append('')
    [ext,lang,aps]=parts[:3]
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('picsearch', textaps+name, ext, name))
    page3.content = text
    """Displays the tag search box and possibly a list of results."""
    query = cgi.escape(self.request.get('q'))
    pics = []
    if query:
      # ListProperty magically does want we want: search for the occurrence
      # of the term in any of the tags.
      pics = Picture.all().filter('tags =', query)
    else:
      query = ''
    page2 = Page.load(page_name2)
    self.render_to_response('pic_search.html',lang, {
        'plet': lang+'.'+fileext,
        'kalbos': page3,
        'menu': page2,
        'query': query,
        'pics': pics,
      })

class RedirN(webapp.RequestHandler):
  def get(self, page_name):
    self.response.headers['X-Powered-By'] = cmsname2+'/'+_version
    self.redirect('http://'+site2b+os.environ['PATH_INFO'])


#def main():
#  redir = False
#  if os.environ['HTTP_HOST']=='www.upe.lt' or os.environ['HTTP_HOST']=='lt.upe.lt' or os.environ['HTTP_HOST']=='us.upe.lt' or os.environ['HTTP_HOST']=='upe.lt':
#    redir = True
#  applicationredir = webapp.WSGIApplication([('/(.*)', RedirN),], debug=_DEBUG)

url_map = [('/'+cmspath2+'-pic-(.*)', ImageSharingAlbumIndex),
             ('/'+cmspath2+'-picnew-(.*)', ImageSharingAlbumCreate),
             ('/'+cmspath2+'-picalbum-(.*)/([-\w]+)', ImageSharingAlbumView),
             ('/'+cmspath2+'-picupload-(.*)/([-\w]+)', ImageSharingUploadImage),
             ('/'+cmspath2+'-picshowimage-(.*)/([-\w]+)', ImageSharingShowImage),
             ('/'+cmspath2+'-pic(thumbnail|image)-(.*)/([-\w]+)', ImageSharingServeImage),
             ('/'+cmspath2+'-picsearch-(.*)', ImageSharingSearch)]
app = webapp.WSGIApplication(url_map,
                                       debug=True)
#  wsgiref.handlers.CGIHandler().run(application)
#  if redir:
#    run_wsgi_app(applicationredir)
#    exit(0)
#  run_wsgi_app(application)

#if __name__ == '__main__':
#  main()
