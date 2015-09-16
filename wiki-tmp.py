#!/usr/bin/env python
#
# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A simple Google App Engine wiki application.

The main distinguishing feature is that editing is in a WYSIWYG editor
rather than a text editor with special syntax.  This application uses
google.appengine.api.datastore to access the datastore.  This is a
lower-level API on which google.appengine.ext.db depends.
"""

__author__ = 'Bret Taylor & Nerijus Terebas'

import cgi
import cgitb
cgitb.enable()
import datetime
import os
import re
import sys
import urllib
import urlparse
import base64
import codecs
import math
from pngcanvas import PNGCanvas
import random
import json
#import wsgiref.handlers
#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2 as webapp
from webapp2_extras import routes
#import wsgiref.handlers
import traceback

from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.api import images

import locale 
import gettext 

from google.appengine.api import urlfetch
from Picasa import Picasa
from postmarkup import render_bbcode
from UserAdd import UserAdd
from UserAdd import Vartotojai
from Start import Start
from Start import Codeimagereg
from Start import AppVer
from Start import DinCode

import facebookoauth
from facebookoauth import FBUser
import linkedinauth
from linkedinauth import LIUser
import vkauth
from vkauth import VKUser
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
_kalbhtml = LANGHTML

langdef=lang
lang1 = gettext.translation (cmstrans2, locale_path, [current_locale] , fallback=True) 
_ = lang1.ugettext

# Set to true if we want to have our webapp print stack traces, etc
_titauth = TITAUTH
#_titauth = "Nerijus Terebas"
_version=VERSION
#if os.environ['HTTP_HOST']==site1a or os.environ['HTTP_HOST']==site1b or os.environ['HTTP_HOST']==site2a or os.environ['HTTP_HOST']==site2b:
#	imgfont = "Ubuntu-B.ttf"
#else:
#	imgfont = "VeraSeBd.ttf"
#imgfont = "Ubuntu-B.ttf"
imgopt = DYNABOPT
fbputimgurl2="/static/images/upelis116.jpg"
avatarmaxurl2="/static/images/avatarmax.png"
avatarminurl2="/static/images/avatarmin.png"
g16url="/static/images/g16.png"
fb16url="/static/images/fb16.png"
in16url="/static/images/in16.png"
vk16url="/static/images/vk16.png"
gplusurl="/static/images/plus.ico"

def siteauth():
	if os.environ['HTTP_HOST']==site1a or os.environ['HTTP_HOST']==site1b or os.environ['HTTP_HOST']==site2a or os.environ['HTTP_HOST']==site2b:
		return "Nerijus Terebas"
	else:
		return _titauth

def urlparam(rparameters):
	parts = rparameters.split(".")
	parts.reverse()
	parts.append('')
	parts.append('')
	parts.append('')
	[ext,lang,aps]=parts[:3]
	if lang in kalbos:
		kalb=kalbos[lang]
	else:
		kalb=kalbos[langdef]
		lang=langdef

	values = {
		'ext': ext,
		'lang': lang,
		'kalb': kalb,
		'aps': aps}
	return values
def userinfo(pic_key2,utype,lang, fileext):
  youtname=""
  rcomm = False
  rpica = False
  rplus = True
  buvoapp = False
  userid = "0"
  content = ""
  content2 = ""
  lank = UserNone(email=None, federated_identity=None)
  pseudonimas = "Anonymous"
  user = users.get_current_user()
  thubnail=""
  imagemaxurl = avatarmaxurl2
  userpicapagetext=""
  klaida=False
  errtext = "" 
  vartot = None
  vartkey=""

  try:
#  if not klaida:
        if utype:
			buvesapp = db.GqlQuery("SELECT * FROM Vartotojai WHERE userid = :1", pic_key2)
        else:
			buvesapp = db.GqlQuery("SELECT * FROM Vartotojai WHERE lankytojas = :1", pic_key2)
			for app in buvesapp:
				rcomm = app.commrodyti
				rpica = app.picarodyti
				rplus = app.plusrodyti
				buvoapp = app.rodyti
				userid = app.userid
				content = render_bbcode(str(app.content))
				content2 = str(app.content)
				pseudonimas = str(app.pseudonimas)
				lank=app.lankytojas
				youtname=app.youtname
				vartkey=app.key()
			thubnail=getphoto(lank.email())
			vartot = db.get(vartkey)

  except:
        klaida=True
        errtext =  cgi.escape(str(sys.exc_info()[0])) + ' ' + cgi.escape(str(sys.exc_info()[1])) + ' ' + cgi.escape(str(sys.exc_info()[2]))
  usercommpageurl = ("%s/%s-usercommpage-%s.%s/%s/%s" % (urlhost2(), cmspath2,lang, fileext, pseudonimas, userid))
  userpicapageurl = ("%s/%s-userpicapage-%s.%s/%s/%s" % (urlhost2(), cmspath2,lang, fileext, pseudonimas, userid))
  useryoutpageurl = ("%s/%s-useryoutpage-%s.%s/%s/%s" % (urlhost2(), cmspath2,lang, fileext, pseudonimas, userid))
  usermailformpageurl = ("%s/%s-usermailformpage-%s.%s/%s/%s" % (urlhost2(), cmspath2,lang, fileext, pseudonimas, userid))
  if lank.email():
    usermailformtext = (_("User mail form page link text %(usercppseudonimas)s %(usermailformpageurl)s") % {'usercppseudonimas': pseudonimas,'usermailformpageurl': usermailformpageurl})
  else:
    usermailformtext = "User not Found"
  if klaida:
    userpicapagetext = ("<div>Error: %s</div" %  (errtext))
  if rcomm:
    userpicapagetext = userpicapagetext + (_("User comm page link text %(usercppseudonimas)s %(usercommpageurl)s") % {'usercppseudonimas': pseudonimas,'usercommpageurl': usercommpageurl})
  if rpica:
    userpicapagetext = userpicapagetext + (_("User pica page link text %(usercppseudonimas)s %(userpicapageurl)s") % {'usercppseudonimas': pseudonimas,'userpicapageurl': userpicapageurl})
  if klaida:
    userpicapagetext = userpicapagetext + "<br>" + errtext
  plusurl=getplius(lank.email())
  if rplus and plusurl:
    usercpplustext = ("<a href=\"%s\"><img src=\"%s\" width=\"32\" height=\"32\" border=\"0\"> <strong>Google Plus</strong></a><br><br>\n\n" % (plusurl,gplusurl))
    rpluscheck="checked=\"yes\"" 
  else:
    usercpplustext = ""
    rpluscheck="checked=\"no\"" 
  if youtname and len(str(youtname))>0:
    userpicapagetext = userpicapagetext + (_("User yout page link text %(usercppseudonimas)s %(useryoutpageurl)s") % {'usercppseudonimas': pseudonimas,'useryoutpageurl': useryoutpageurl})
  if buvoapp:
    imagemaxurl = ("/%s-userimage/%s/%s" % (cmspath2,pseudonimas, userid))
  if thubnail and not buvoapp:
    imagemaxurl = str(thubnail)
    uphoto=imagemaxurl.split("/s144/", 1)
    slasas="/s200/"
    imagemaxurl = slasas.join(uphoto)
  usercpurl = ("/%s-usercontrolpanel-%s.%s" % (cmspath2,lang,fileext))
  userpageend = ("%s/%s/%s" % (fileext,pseudonimas,userid))
  userpageurl = ("%s/%s-userpage-%s.%s/%s/%s" % (urlhost2(),cmspath2, lang, fileext, pseudonimas, userid))

  if rcomm:
    rcommcheck="checked=\"yes\"" 
  else:
    rcommcheck="checked=\"no\""
  if rpica:
    rpicacheck="checked=\"yes\"" 
  else:
    rpicacheck="checked=\"no\""
  if buvoapp:
    buvoappcheck="checked=\"no\""
  else:
    buvoappcheck="checked=\"yes\"" 
 
  values = {
  	'imagemaxurl': imagemaxurl,
  	'userpageend': userpageend,
  	'userpicapagetext': userpicapagetext,
  	'usercpplustext': usercpplustext,
  	'usermailformtext': usermailformtext,
  	'usermailformpageurl': usermailformpageurl,
  	'useryoutpageurl': useryoutpageurl,
  	'userpicapageurl': userpicapageurl,
  	'usercommpageurl': usercommpageurl,
  	'usercommpageurl': usercommpageurl,
  	'usercpurl':  usercpurl,
  	'pseudonimas': pseudonimas,
  	'userid': userid,
  	'content': content,
  	'content2': content2,
  	'youtname': youtname,
  	'vartot': vartot,
  	'rcomm': rcomm,
  	'rpica': rpica,
  	'lank': lank,
  	'rcommcheck': rcommcheck,
  	'rpluscheck': rpluscheck,
  	'rpicacheck': rpicacheck,
  	'buvoappcheck': buvoappcheck,
  	'userpageurl': userpageurl}
  return values
	
def codekey2():
	codeimg = Codeimagereg()
	codeimg.ipadresas = os.environ['REMOTE_ADDR']
	codeimg.date = datetime.datetime.now()
	code = random.randrange(100000, 999999)
	codeimg.code = "%s" % code
	codeimg.put()
	codekey=codeimg.key()
	return codekey
def urlhost2():
	if os.environ['HTTPS']=="off":
		return str('http://'+os.environ['HTTP_HOST'])
	else:
		return str('https://'+os.environ['HTTP_HOST'])

def textloc():
	q2_message = ""
	if 'HTTP_X_APPENGINE_CITY' in os.environ:
		q2_message = q2_message + ("%s: %s \n" % ('City', os.environ['HTTP_X_APPENGINE_CITY']))
	if 'HTTP_X_APPENGINE_COUNTRY' in os.environ:
		q2_message = q2_message + ("%s: %s \n" % ('Country', os.environ['HTTP_X_APPENGINE_COUNTRY']))
	if 'HTTP_X_APPENGINE_CITYLATLONG' in os.environ:
		q2_message = q2_message +("%s: http://maps.google.com/maps?q=%s \n" % ('CityLatLong', os.environ['HTTP_X_APPENGINE_CITYLATLONG']))
	return q2_message
def textinfo():
	q2_message = "\n\nRemote Addr: " + os.environ['REMOTE_ADDR'] + "\nUser Agent: " + os.environ['HTTP_USER_AGENT'] + "\nLog ID: " + os.environ['REQUEST_LOG_ID'] + "\n"
	return q2_message

class BaseRequestHandler(webapp.RequestHandler):
  """Supplies a common template generation function.

  When you call generate(), we augment the template variables supplied with
  the current user in the 'user' variable and the current webapp request
  in the 'request' variable.
  """
  def generate(self, template_name, languag, template_values={}):
    UserAdd().plus()
    Start().first()
    if not languag:
      languag=langdef
    if languag in kalbos:
      kalb=kalbos[languag]
    else:
      kalb=kalbos[langdef]
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    kalb2=kalb.replace("_", "-")
    values = {
      'request': self.request,
      'user': users.GetCurrentUser(),
      'fbuser': self.fb_current_user,
      'liuser': self.li_current_user,
      'vkuser': self.vk_current_user,
      'isadmin': users.is_current_user_admin(),
      'self_url': self.request.uri,
      'login_url': users.CreateLoginURL(self.request.uri),
      'logout_url': users.CreateLogoutURL(self.request.uri),
      'fblogin_url': "/auth/login?continue=%s" % (urllib.quote(self.request.uri)),
      'fblogout_url': "/auth/logout?continue=%s" % (urllib.quote(self.request.uri)),
      'lilogin_url': "/liauth/login?continue=%s" % (urllib.quote(self.request.uri)),
      'lilogout_url': "/liauth/logout?continue=%s" % (urllib.quote(self.request.uri)),
      'vklogin_url': "/vkauth/login?continue=%s" % (urllib.quote(self.request.uri)),
      'vklogout_url': "/vkauth/logout?continue=%s" % (urllib.quote(self.request.uri)),
      'application_name': siteauth(),
      'msgtext_logout': _("logout"),
      'msgtext_login': _("login"),
      'msgtext_header': _("header %(cmsname)s") % {'cmsname': cmsname2},
      'gallery': _("Gallery"),
      'kalba': kalb2,
      'cmspath':cmspath2,

    }
    values.update(template_values)
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, os.path.join('templates', template_name))
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
      self.response.out.write(template.render(path, values, debug=_DEBUG))
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
              if not self._fb_current_user or not hasattr(self._fb_current_user, "login") or not self._fb_current_user.login:
                  self._fb_current_user=None
      return self._fb_current_user
  @property
  def li_current_user(self):
      """Returns the logged in Linkedin user, or None if unconnected."""
      if not hasattr(self, "_li_current_user"):
          self._li_current_user = None
          user_id = linkedinauth.parse_cookie(self.request.cookies.get("li_user"))
          if user_id:
              self._li_current_user = LIUser.get_by_key_name(user_id)
      return self._li_current_user

  @property
  def vk_current_user(self):
      """Returns the logged in Linkedin user, or None if unconnected."""
      if not hasattr(self, "_vk_current_user"):
          self._vk_current_user = None
          user_id = vkauth.parse_cookie(self.request.cookies.get("vk_user"))
          if user_id:
              self._vk_current_user = VKUser.get_by_key_name(user_id)
      return self._vk_current_user

class WikiFav(BaseRequestHandler):
  def get(self, page_name):
    self.response.headers['Cache-Control'] = 'public, max-age=60'
#	self.response.headers['Last-Modified'] = lastmod.strftime("%a, %d %b %Y %H:%M:%S GMT")
    expires = datetime.datetime.now() + datetime.timedelta(minutes=1)
    self.response.headers['Expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT") 
    from bindata import FavIcon
    imagelogo=FavIcon()
    fav=imagelogo.data1
    if os.environ['HTTP_HOST']==site1a or os.environ['HTTP_HOST']==site1b:
        fav = imagelogo.data2
    self.response.headers['Content-Type'] = 'image/x-icon'
    self.response.out.write(fav)
  def post(self, page_name):
    self.response.headers['Cache-Control'] = 'public, max-age=60'
#	self.response.headers['Last-Modified'] = lastmod.strftime("%a, %d %b %Y %H:%M:%S GMT")
    expires = datetime.datetime.now() + datetime.timedelta(minutes=1)
    self.response.headers['Expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT") 
    from bindata import FavIcon
    imagelogo=FavIcon()
    fav=imagelogo.data1
    if os.environ['HTTP_HOST']==site1a or os.environ['HTTP_HOST']==site1b:
        fav = imagelogo.data2
    self.response.headers['Content-Type'] = 'image/x-icon'
    self.response.out.write(fav)

class WikiRedirDown(BaseRequestHandler):
  def get(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext

    user = users.get_current_user()
    if user:
      self.response.headers['X-Powered-By'] = cmsname2+'/'+_version
      self.redirect(sitedown)
#      exit(0)
    else:
      greeting = _("Sign in or register %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}
      greeting=greeting+"<br>"+(_("diferent accounts"))

      page = Page.loadnew("download")
      page.content = "Download - "+_("Login header %(greeting)s") % {'greeting': greeting}
      page_name2 = 'menu'+'-'+lang+'.'+fileext
      page2 = Page.load(page_name2)
      page3 = Page.loadnew("kalbos")
      textaps=''
      if len(aps)>0:
          textaps=aps+'.'
      text=''
      for name, value in kalbossort:
          text = text + (_kalbhtml % ('download', textaps+name, ext, name, name))
      page3.content = text
      self.generate('view.html', lang, {
        'imgshar': False,
        'noedit': '1',
        'application_name': siteauth(),
        'kalbos': page3,
        'menu': page2,
        'page': page,
      })

class RedirN(BaseRequestHandler):
  def get(self, page_name):
    self.response.headers['X-Powered-By'] = cmsname2+'/'+_version
    self.redirect('http://'+site2b+os.environ['PATH_INFO'])

class RedirN2(BaseRequestHandler):
  def get(self, page_name):
    self.redirect('http://www.google.com/')

class WikiRedirMain(BaseRequestHandler):
  def get(self, page_name):
    if not page_name:
        page_name="MainPage"
    self.response.headers['X-Powered-By'] = cmsname2+'/'+_version
    entitiesRx  = re.compile("[^0-9a-zA-Z]")
    page_name = entitiesRx.sub("", page_name)
    self.redirect('/'+cmspath2+'-'+page_name+'-'+lang+'.'+fileext)
#  def post(self, page_name):
#    if not page_name:
#        page_name="MainPage"
#    self.response.headers['X-Powered-By'] = cmsname2+'/'+_version
#    self.redirect('/'+cmspath2+'-'+page_name+'-'+lang+'.'+fileext)
  def post(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    page = Page.loadnew("env")
    user = users.get_current_user()
    greeting = ''
    if user:
      if users.is_current_user_admin():
        items = os.environ.items()
        items.sort()
        for name, value in items:
                 aaa = "%s\t= %s <br/>" % (name, value)
                 greeting = greeting + aaa
        for field in self.request.arguments():
                 aaa = "%s\t= %s <br/>" % (field, self.request.get(field))
                 greeting = greeting + aaa
      else:
        greeting = _("Welcome2 %(admin)s %(usernickname)s %(userlogouturl)s") % {'admin': '', 'usernickname': user.nickname(), 'userlogouturl': users.create_logout_url(self.request.uri)}
        greeting = greeting + " " + _("and") + " " + (_("sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)})
    else:
      greeting = _("Sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}
    page.content = _("Enviroment header %(greeting)s") % {'greeting': greeting}
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('env', textaps+name, ext, name, name))
        page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })



class WikiRedir(BaseRequestHandler):
  def get(self, page_name):
    self.redirect('/')
  def post(self, page_name):
    self.redirect('/')

class WikiInstall(BaseRequestHandler):
    def get(self):
        for name, value in kalbossort:
            lang=name
            kalb=kalbos[lang]
            lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
            _ = lang1.ugettext
            yra1 = False
            yra2 = False
            puslapis1 = _("page index html %(cmsname)s %(cmspath)s") % {'cmsname': cmsname2,'cmspath': cmspath2}
            puslapis2 = _("page menu html %(cmspath)s") % {'cmspath': cmspath2}
            query = datastore.Query('Page')
            query['name ='] = "MainPage-"+lang+'.'+fileext
            entities = query.Get(1)
            if len(entities) < 1:
                yra1 = False
            else:
                yra1 = True
            query = datastore.Query('Page')
            query['name ='] = "menu-"+lang+'.'+fileext
            entities = query.Get(1)
            if len(entities) < 1:
                yra2 = False
            else:
                yra2 = True
            if not yra1:
                page = Page.loadnew("MainPage-"+lang+'.'+fileext)
                page.content = puslapis1
                page.save()
            if not yra2:
                page = Page.loadnew("menu-"+lang+'.'+fileext)
                page.content = puslapis2
                page.save()
        self.redirect('/')
    
class WikiPage(BaseRequestHandler):
  """Our one and only request handler.

  We first determine which page we are editing, using "MainPage" if no
  page is specified in the URI. We then determine the mode we are in (view
  or edit), choosing "view" by default.

  POST requests to this handler handle edit operations, writing the new page
  to the datastore.
  """
  def get(self, page_name, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    formurl=urlhost2()
    formurl=urlparse.urljoin(formurl, str(self.request.uri))
    o = urlparse.urlparse(formurl)
    urlpath_without_query_string = o.path
    url_without_query_string = o.scheme+"://"+o.netloc+o.path
    url_host = o.scheme+"://"+o.netloc
    # Load the main page by default
    if not page_name:
      page_name = 'MainPage'
    page_name_org = page_name
    rparameters2 = rparameters
    entitiesRx  = re.compile("[^0-9a-zA-Z\x2D\x5F\x2E\x2C]")
    rparameters2 = entitiesRx.sub("", rparameters2)
    page_name = "%s-%s" % (page_name,rparameters2)
    page = Page.load(page_name)
    #    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page_name2 = "menu-%s.%s" % (lang,fileext)
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % (page_name_org, textaps+name, ext, name, name))
    page3.content = text

# ner
    if not page.entity and not users.GetCurrentUser() and not users.is_current_user_admin():
      self.error(404)
      self.response.out.write('Not found')
      return

    # Default to edit for pages that do not yet exist
    if not page.entity:
      mode = 'edit'

    else:
      modes = ['view', 'edit', 'fbputwall']
      mode = self.request.get('mode')
      if not mode in modes:
        mode = 'view'

    # User must be logged in to edit
    if mode == 'edit' and not users.GetCurrentUser() and not users.is_current_user_admin():
      self.redirect(users.CreateLoginURL(self.request.uri))
      return

    if mode == 'fbputwall':
      greeting = ''
      fb_current_user=self.fb_current_user
      if fb_current_user:	
        aaa = _("logged Facebook %(fbprofileurl)s %(fbpicurl)s %(fbname)s %(url)s") % {'fbprofileurl': fb_current_user.profile_url,'fbpicurl': "http://graph.facebook.com/"+fb_current_user.id+"/picture",'fbname': fb_current_user.name,'url': '/auth/logout?continue='+urllib.quote(self.request.uri)}
        from rss import MyHTMLParser,HTMLParser  
        parser = HTMLParser()
        parerr = False
        try:
            p = MyHTMLParser()
            p.feed(parser.unescape(page.content))
            pav=p.data[0]
            p.close()
        except:
        	pav=_("--- tag h1 not found in page ---")
        	parerr = True
        if not parerr:
        	message = _("Message from:").encode("utf-8")+"\n"+urlhost2()      
        	attachment = {}  
        	attachment['name'] = pav.encode("utf-8") 
        	attachment['caption'] = os.environ['HTTP_HOST']  
        	attachment['link'] = urlhost2()+os.environ['PATH_INFO']
        	attachment['picture'] = urlhost2()+fbputimgurl2  
        	attachment['description'] = '   '  
        	import fb
        	obj = self
        	aaa=fb.putwall(obj,message,attachment)
        else:
        	aaa="<h1>Error</h1>%s" % (pav)

      else:
        aaa = _("not logged Facebook %(url)s") % {'url': '/auth/login?continue='+urllib.quote(self.request.uri)}
      greeting = greeting + aaa
      page.content = "%s" % (greeting)

      # Genertate the appropriate template
      self.generate('view.html', lang, {
        'imgshar': False,
        'kalbos': page3,
        'menu': page2,
        'page': page,
        })
      return
    if mode == 'view':
      page.content = "%s%s" % (page.content,"<p>&nbsp;</p><p><a href=\""+url_without_query_string+"?mode=fbputwall\"><img src=\""+url_host+"/dynab?button_text="+urllib.quote(_("Put to Facebook Wall").encode("utf-8"))+imgopt+"\" border=\"0\" alt=\""+_("Put to Facebook Wall")+"\"></a></p>")

    soccomtext = ""
    soccomshowform = False
    if mode == 'view' and (page.commenablego or page.commenablefb or page.commenableli or page.commenablevk):
#        if hasattr(a, 'property'):
        soccomtext = "<p><h3>"+_("Commenting is turned on with a social networks logins:")	
        if page.commenablego:	
            soccomtext = soccomtext + " Google"	
            user = users.get_current_user()
            if user:	
                soccomshowform = True	
        if page.commenablefb:	
            soccomtext = soccomtext + " FaceBook"	
            fb_current_user=self.fb_current_user
            if fb_current_user:	
                soccomshowform = True	
        if page.commenableli:	
            soccomtext = soccomtext + " LinkedIn"	
            li_current_user=self.li_current_user
            if li_current_user:	
                soccomshowform = True	
        if page.commenablevk:	
            soccomtext = soccomtext + " VKontakte"	
            vk_current_user=self.vk_current_user
            if vk_current_user:	
                soccomshowform = True	
        soccomtext = soccomtext + "</h3></p>"	
        page.content = "%s%s" % (page.content,soccomtext)
        soccomtext2 = ""
        if soccomshowform:
            codekey=codekey2()
            soccomtext2 = (_("page Comments form %(commsendurl)s %(commcodekey)s %(commbutsrc)s")  % {'commsendurl': urlpath_without_query_string, 'commcodekey': codekey, 'commbutsrc':  "src=\""+url_host+"/dynab?button_text="+urllib.quote(_("Submit Comment").encode("utf-8"))+imgopt+"\""})
        if mode == 'view' and (page.commenablego or page.commenablefb or page.commenableli or page.commenablevk):
            page.content = "%s%s%s" % (page.content,soccomtext2,("<div><p><a href=\""+ urlpath_without_query_string +"?cmd=comments\"><img src=\""+url_host+"/dynab?button_text="+urllib.quote(_("View Comments").encode("utf-8"))+imgopt+"\" border=\"0\" alt=\""+_("View Comments")+"\"></a></p></div>" ))

        if self.request.get('cmd') == 'comments':
            rcomm = True
            userid = "0"
            content = ""
            pseudonimas = "Anonymous"
            user = users.get_current_user()
            if rcomm:
              yra=False
              wtext=""
              try:
                pg=self.request.get('pg')
                entitiesRx  = re.compile("[^0-9]")
                pg=entitiesRx.sub("", pg)
                if pg:
                  pg = int(pg)
                else:
                  pg=0

                try:
                  query = db.GqlQuery("SELECT * FROM Commentsrec3 WHERE commpage = :1 ORDER BY date DESC", page_name)
                  greetings = query.fetch(10,pg*10)
                  co=query.count()
                except:
                  klaida=True
                  co=0
                  greetings = []

                i=0
                ii=0
                bbb=""
                while i<=co:
                  i=i+10
                  if ii == pg:
                    bbb=bbb+' '+str(ii)
                  else:
                    bbb=bbb+' '+("<a href=\"%s?cmd=comments&pg=%s\">%s</a>" % (urlpath_without_query_string,str(ii),str(ii)))
                  ii=ii+1
               
                wtext=wtext+"<div><hr width=\"70%\"></div>\n<div style=\"text-align: center;\">"+bbb+"</div>\n\n"
                for greeting in greetings:
                  wijun = ""
                  wdel = ""
                  if greeting.rodyti or (users.GetCurrentUser() and users.get_current_user() == greeting.author) or users.is_current_user_admin():
                      if users.is_current_user_admin():
                          wdel = _("Comments delete %(commswiturl)s %(commkey)s") % {'commswiturl': '/commswit', 'commkey': greeting.key()}
                      if (users.GetCurrentUser() and users.get_current_user() == greeting.author) or users.is_current_user_admin():
                          if not greeting.rodyti:
                              wijun = _("Comments show %(commswiturl)s %(commkey)s") % {'commswiturl': '/commswit', 'commkey': greeting.key()}
                          else:
                              wijun = _("Comments hidden %(commswiturl)s %(commkey)s") % {'commswiturl': '/commswit', 'commkey': greeting.key()}

                      user3 = greeting.vartot
                      user3fb = greeting.vartotfb
                      user3li = greeting.vartotli
                      user3vk = greeting.vartotvk
                      pseudonimas3 = "Anonymous"
                      userid3 = '0'
                      try:
                            userid3 = user3.userid
                            pseudonimas3 = user3.pseudonimas
                      except:
                            klaida=True
                      
                      wtext = wtext + "\n<div class=\"comm-container\">\n"
                      wtext = wtext + "<div class=\"comm-name\">\n"
                      if user3:
                      	imagemaxurl2 = ("/%s-userimagemin/%s/%s" % (cmspath2,pseudonimas3, userid3))
                      	userpageurl = ("%s/%s-userpage-%s.%s/%s/%s" % (urlhost2(), cmspath2,lang, fileext, pseudonimas3, userid3))
                      	wtext = wtext +("<a href=\"%s\"><img src=\"%s\" alt=\"\" border=\"0\"></img></a> <strong><img src=\"%s\" alt=\"\" border=\"0\"></img></strong> " % (userpageurl,imagemaxurl2,g16url))+(' <strong>%s</strong>' % pseudonimas3) +", <br />\n"
                      if user3fb:
                      	userid = user3fb.id
#                      	pseudonimas3 = user3fb.nickname
                      	pseudonimas3 = user3fb.name
                      	imagemaxurl2 = ("http://graph.facebook.com/%s/picture" % (userid))
                      	userpageurl = ("%s/fbinfo?id=%s" % (urlhost2(),userid))
                      	wtext = wtext +("<a href=\"%s\"><img src=\"%s\" alt=\"\" border=\"0\"></img></a> <strong><img src=\"%s\" alt=\"\" border=\"0\"></img></strong> " % (userpageurl,imagemaxurl2,fb16url))+(' <strong>%s</strong>' % pseudonimas3) +", <br />\n"
                      if user3li:
                      	userid = user3li.id
                      	ukey = user3li.key()
#                      	pseudonimas3 = user3li.nickname
                      	pseudonimas3 = user3li.name
                      	imagemaxurl2 = ("%s/liphoto2/%s" % (urlhost2(),ukey))
                      	userpageurl = user3li.profile_url
                      	wtext = wtext +("<a href=\"%s\"><img src=\"%s\" alt=\"\" border=\"0\"></img></a> <strong><img src=\"%s\" alt=\"\" border=\"0\"></img></strong> " % (userpageurl,imagemaxurl2,in16url))+(' <strong>%s</strong>' % pseudonimas3) +", <br />\n"
                      if user3vk:
                      	userid = user3vk.id
                      	ukey = user3vk.key()
#                      	pseudonimas3 = user3li.nickname
                      	pseudonimas3 = user3vk.name
                      	imagemaxurl2 = ("%s/vkphoto/%s" % (urlhost2(),userid))
                      	userpageurl = user3vk.profile_url
                      	wtext = wtext +("<a href=\"%s\"><img src=\"%s\" alt=\"\" border=\"0\"></img></a> <strong><img src=\"%s\" alt=\"\" border=\"0\"></img></strong> " % (userpageurl,imagemaxurl2,vk16url))+(' <strong>%s</strong>' % pseudonimas3) +", <br />\n"
                      wtext = wtext +"\n</div>\n"
                      wtext = wtext +('<div class="font-small-gray">%s</div>' % greeting.date.strftime("%a, %d %b %Y %H:%M:%S"))+"\n"
                      if greeting.avatar:
                      	if greeting.avatarmax:
                      		wtext = wtext + ('<div class="font-small-gray"><a href="/commimg?img_id=%s&size=yes"><img src="/commimg?img_id=%s" alt=""></img></a></div>' % (greeting.key(),greeting.key()))+"\n"
                      	else:
                      		wtext = wtext + ('<div class="font-small-gray"><img src="/commimg?img_id=%s" alt=""></img></div>' % greeting.key())+"\n"
#                      wtext = wtext + "</div>"
                      wtext = wtext + "\n"+('<div class="comm-text"><div>%s</div>' % greeting.content)+"</div>\n"
#                      wtext = wtext + "</div><div class=\"clear\"><!-- --></div>\n"
#redaguoti                      wtext = wtext + "\n<div>"+wijun+"  " +wdel+"</div>\n\n"
                      wtext = wtext + "<div>&nbsp;</div>\n"
                      wtext = wtext + "</div>\n"
                yra=True
              except:
                yra=False
                errtext =  ''.join(traceback.format_exception(*sys.exc_info())) #cgi.escape(str(sys.exc_info()[0]))
              if yra:
                commtext=("<div>%s</div>\n\t" % (wtext))
              else:
                commtext="<div>comments db error: %s</div>\n\t" % (errtext)
            page.content = "%s%s" % (page.content,commtext)
            
            
    # Genertate the appropriate template
    self.generate(mode + '.html', lang, {
      'imgshar': False,
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })

  def post(self, page_name, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    # User must be logged in to edit
    if not users.GetCurrentUser()  and not self.request.get('cmd') == 'pagecomm':
      # The GET version of this URI is just the view/edit mode, which is a
      # reasonable thing to redirect to
      self.redirect(users.CreateLoginURL(self.request.uri))
      return
    if not users.is_current_user_admin()  and not self.request.get('cmd') == 'pagecomm':
      self.redirect(users.CreateLoginURL(self.request.uri))
      return
      
    if not page_name:
      self.redirect('/')

    # Create or overwrite the page
    page_name = page_name+'-'+rparameters
    page = Page.load(page_name)

    if self.request.get('cmd') == 'pagecomm' and ((page.commenablego and users.get_current_user()) or  (page.commenablefb and self.fb_current_user) or (page.commenableli and self.li_current_user) or (page.commenablevk and self.vk_current_user)):
        user = users.get_current_user()
        if user:
            userid = user.user_id()
        else:
            userid = "0"
        fb_current_user=self.fb_current_user
        li_current_user=self.li_current_user
        vk_current_user=self.vk_current_user
        connt=""
        vartot = None
        vartkey=""
        try:
              buvesapp = db.GqlQuery("SELECT * FROM Vartotojai WHERE userid = :1", userid)
              for app in buvesapp:
                  vartkey=app.key()
              vartot = db.get(vartkey)
        except:
              klaida=True
        try:
            codeimg = db.get(self.request.get("scodeid"))
        except:
            prn="Error"
        if codeimg and codeimg.code == self.request.get("scode"):
            greeting = Commentsrec3()
            greeting.commpage = page_name
            greeting.vartot = vartot
            greeting.vartotfb = self.fb_current_user
            greeting.vartotli = self.li_current_user
            greeting.vartotvk = self.vk_current_user
            greeting.rodyti = True
            greeting.userid = userid
            greeting.ipadresas = os.environ['REMOTE_ADDR']
#	greeting.laikas = datetime.datetime.now()
            if users.get_current_user():
            	greeting.author = users.get_current_user()
            connt = cgi.escape(self.request.get("content"))
            connt = render_bbcode(connt)
            connt = connt[0:400]
            greeting.content = connt
#    priesduom = self.request.get("img")
            greeting.rname = "anonymous"
            if self.request.get("img"):
              avatarmax = images.resize(self.request.get("img"), width=600, height=400, output_encoding=images.PNG)
              greeting.avatarmax = db.Blob(avatarmax)
              avatar = images.resize(self.request.get("img"), width=96, height=96, output_encoding=images.PNG)
              greeting.avatar = db.Blob(avatar)
            greeting.put()
            to_addr = _mailrcptto
            user = users.get_current_user()
            if user:
                uname=user.nickname()
                umail=users.get_current_user().email()
            else:
                uname=""
                umail=""
            message = mail.EmailMessage()
            message.subject = os.environ['HTTP_HOST'] + " - comments"
            message.sender = _mailsender
            message.to = to_addr
            q_message = ""
            q_message = q_message + ("\n%s: %s \n%s \n%s \n" % ('Page', str(self.request.uri),str(textinfo()),str(textloc())))

            message.body = (_("Comments mail message %(communame)s %(commumail)s %(commrealname)s %(commmessage)s") % {'communame': uname,'commumail': umail,'commrealname': greeting.rname,'commmessage': greeting.content}) + q_message
            message.send()

#    self.redirect('/'+cmspath2+'-usercommpage-'+lang+'.'+fileext+'/'+pseudonimas+'/'+userid )






    if not self.request.get('cmd') == 'pagecomm':
        page.content = self.request.get('content')
        page.save()
    self.redirect(page.view_url())

class WikiExec(BaseRequestHandler):
  def get(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
 #	values222 = { "name" : "world" }
    page = Page.loadnew("pasaulis")
    page.content = base64.decodestring("PGgxPkhlbGxvPC9oMT48cD5OZXJpamF1cyBUZXJlYmFzIC0gQ01TICIlcyIgLSAlcyAtIGJhc2VkICJjY2N3aWtpIiAoQnJldCBUYXlsb3IpLCAiaW1hZ2Vfc2hhcmluZyIgKEZyZWQgV3VsZmYpPC9wPg==") % (cmsname2,_version)
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('ver', textaps+name, ext, name, name))
    page3.content = text
    page2 = Page.load(page_name2)
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })

class WikiLogin(BaseRequestHandler):
  def get(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext

    user = users.get_current_user()
    if user:
      greeting = _("Welcome2 %(admin)s %(usernickname)s %(userlogouturl)s") % {'admin': '', 'usernickname': user.nickname(), 'userlogouturl': users.create_logout_url(self.request.uri)}
      if users.is_current_user_admin():
        greeting = _("Welcome2 %(admin)s %(usernickname)s %(userlogouturl)s") % {'admin': 'Administrator', 'usernickname': user.nickname(), 'userlogouturl': users.create_logout_url(self.request.uri)}
    else:
      greeting = _("Sign in or register %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}
      greeting=greeting+"<br>"+(_("diferent accounts"))

    page = Page.loadnew("login")
    page.content = _("Login header %(greeting)s") % {'greeting': greeting}
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('login', textaps+name, ext, name, name))
    page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })

class WikiEnv(BaseRequestHandler):

  def get(self, rparameters):

    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    page = Page.loadnew("env")
    user = users.get_current_user()
    greeting = ''
    if user:
      if users.is_current_user_admin():
        items = os.environ.items()
        items.sort()
        for name, value in items:
                 aaa = "%s\t= %s <br/>" % (name, value)
                 greeting = greeting + aaa
      else:
        greeting = _("Welcome2 %(admin)s %(usernickname)s %(userlogouturl)s") % {'admin': '', 'usernickname': user.nickname(), 'userlogouturl': users.create_logout_url(self.request.uri)}
        greeting = greeting + " " + _("and") + " " + (_("sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)})
    else:
      greeting = _("Sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}
    page.content = _("Enviroment header %(greeting)s") % {'greeting': greeting}
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('env', textaps+name, ext, name, name))
        page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })

class WikiFB(BaseRequestHandler):

  def get(self, rparameters):

    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    page = Page.loadnew("fb")
    user = users.get_current_user()
    greeting = ''
    if user:
      if users.is_current_user_admin():
        items = os.environ.items()
        fb_current_user=self.fb_current_user
        if fb_current_user:
            aaa = _("logged Facebook %(fbprofileurl)s %(fbpicurl)s %(fbname)s %(url)s") % {'fbprofileurl': fb_current_user.profile_url,'fbpicurl': "http://graph.facebook.com/"+fb_current_user.id+"/picture",'fbname': fb_current_user.name,'url': '/auth/logout?continue='+urllib.quote(self.request.uri)}
        else:
            aaa = _("not logged Facebook %(url)s") % {'url': '/auth/login?continue='+urllib.quote(self.request.uri)}
        greeting = greeting + aaa
      else:
        greeting = _("Welcome2 %(admin)s %(usernickname)s %(userlogouturl)s") % {'admin': '', 'usernickname': user.nickname(), 'userlogouturl': users.create_logout_url(self.request.uri)}
        greeting = greeting + " " + _("and") + " " + (_("sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)})
    else:
      greeting = _("Sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}
    page.content = _("Facebook header %(greeting)s") % {'greeting': greeting}
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('fb', textaps+name, ext, name, name))
        page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })

class WikiLI(BaseRequestHandler):

  def get(self, rparameters):

    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    page = Page.loadnew("fb")
    user = users.get_current_user()
    greeting = ''
    if user:
      if users.is_current_user_admin():
        items = os.environ.items()
        li_current_user=self.li_current_user
        if li_current_user:
            aaa = _("logged LinkedIn %(liprofileurl)s %(lipicurl)s %(liname)s %(url)s") % {'liprofileurl': li_current_user.profile_url,'lipicurl': "/liphoto/"+li_current_user.id,'liname': li_current_user.name,'url': '/liauth/logout?continue='+urllib.quote(self.request.uri)}
        else:
            aaa = _("not logged LinkedIn %(url)s") % {'url': '/liauth/login?continue='+urllib.quote(self.request.uri)}
        greeting = greeting + aaa
      else:
        greeting = _("Welcome2 %(admin)s %(usernickname)s %(userlogouturl)s") % {'admin': '', 'usernickname': user.nickname(), 'userlogouturl': users.create_logout_url(self.request.uri)}
        greeting = greeting + " " + _("and") + " " + (_("sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)})
    else:
      greeting = _("Sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}
    page.content = _("LinkedIn header %(greeting)s") % {'greeting': greeting}
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('li', textaps+name, ext, name, name))
        page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })


class WikiVK(BaseRequestHandler):

  def get(self, rparameters):

    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    page = Page.loadnew("vk")
    user = users.get_current_user()
    greeting = ''
    if user:
      if users.is_current_user_admin():
        items = os.environ.items()
        vk_current_user=self.vk_current_user
        if vk_current_user:
            aaa = _("logged VKontakte %(vkprofileurl)s %(vkpicurl)s %(vkname)s %(url)s") % {'vkprofileurl': vk_current_user.profile_url,'vkpicurl': "/vkphoto/"+vk_current_user.id,'vkname': vk_current_user.name,'url': '/vkauth/logout?continue='+urllib.quote(self.request.uri)}
        else:
            aaa = _("not logged VKontakte %(url)s") % {'url': '/vkauth/login?continue='+urllib.quote(self.request.uri)}
        greeting = greeting + aaa
      else:
        greeting = _("Welcome2 %(admin)s %(usernickname)s %(userlogouturl)s") % {'admin': '', 'usernickname': user.nickname(), 'userlogouturl': users.create_logout_url(self.request.uri)}
        greeting = greeting + " " + _("and") + " " + (_("sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)})
    else:
      greeting = _("Sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}
    page.content = _("VKontakte header %(greeting)s") % {'greeting': greeting}
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('li', textaps+name, ext, name, name))
        page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })

class WikiAdmin(BaseRequestHandler):

  def get(self, rparameters):

    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    page = Page.loadnew("admin")
    user = users.get_current_user()
    greeting = ''
    if user:
      if users.is_current_user_admin():
        greeting = _("page admin content html %(cmspath)s") % {'cmspath': cmspath2}
      else:
        greeting = _("Welcome2 %(admin)s %(usernickname)s %(userlogouturl)s") % {'admin': '', 'usernickname': user.nickname(), 'userlogouturl': users.create_logout_url(self.request.uri)}
        greeting = greeting + " " + _("and") + " " + (_("sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)})
    else:
      greeting = _("Sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}
    page.content = _("Admin header %(greeting)s") % {'greeting': greeting}
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('admin', textaps+name, ext, name, name))
    page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })
class WikiMod(BaseRequestHandler):

  def get(self, modname, rparameters):

    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    sys.path.append(os.getcwd()+os.path.sep+"componets")
    import importlib
    entitiesRx  = re.compile("[^0-9a-zA-Z]")
    modname = entitiesRx.sub("", modname)
    modloaderr = False
    modname2 = 'custommodule'
    try:
		moduleim = importlib.import_module("mod"+modname)
    except:
        modloaderr = True
    if not modloaderr:
		moduleim = importlib.import_module("mod"+modname)
		modmed = getattr(moduleim, "modobj"+modname)
		modresult = modmed().cont(self)
		if 'cont' in modresult and len(modresult['cont'])>0:
			modcont = modresult['cont']
		else:
			modcont = "<h1>Custom Compontet \"%s\"</h1>\n" % (modname)
		if 'name' in modresult and len(modresult['name'])>0:
			modname2 = modresult['name']
		else:
			modname2 = 'customcomponent'
		if 'fpput' in modresult and modresult['fpput']==True:
			modfpput = True
		else:
			modfpput = False
		if 'title' in modresult and len(modresult['title'])>0:
			modtitle = modresult['title']
		else:
			modtitle = 'Custom Compontet'
		if 'descr' in modresult and len(modresult['descr'])>0:
			moddescr = modresult['descr']
		else:
			moddescr = '   '
#   	 user = users.get_current_user()

		aaa = "%s" % (modcont)
		modes = ['view', 'fbputwall']
		mode = self.request.get('mode')
		if not mode in modes:
			mode = 'view'

		if mode == 'fbputwall' and modfpput:
			fb_current_user=self.fb_current_user
			if fb_current_user:	
				pav = modtitle
				aaa = _("logged Facebook %(fbprofileurl)s %(fbpicurl)s %(fbname)s %(url)s") % {'fbprofileurl': fb_current_user.profile_url,'fbpicurl': "http://graph.facebook.com/"+fb_current_user.id+"/picture",'fbname': fb_current_user.name,'url': '/auth/logout?continue='+urllib.quote(self.request.uri)}
				parerr = False
				if not parerr:
					message = _("Message from:").encode("utf-8")+"\n"+urlhost2()   
					attachment = {}  
					attachment['name'] = pav.encode("utf-8") 
					attachment['caption'] = os.environ['HTTP_HOST']  
					attachment['link'] = urlhost2()+os.environ['PATH_INFO']
					attachment['picture'] = urlhost2()+fbputimgurl2  
					attachment['description'] = moddescr.encode("utf-8")   
					obj=self   
					import fb
					obj = self
					aaa=fb.putwall(obj,message,attachment)
				else:
					aaa="<h1>Error</h1>%s" % (pav)

			else:
				aaa = _("not logged Facebook %(url)s") % {'url': '/auth/login?continue='+urllib.quote(self.request.uri)}
		if mode == 'view' and modfpput:
			aaa = "%s%s" % (aaa,"<p>&nbsp;</p><p><a href=\""+urlhost2()+os.environ['PATH_INFO']+"?mode=fbputwall\"><img src=\""+urlhost2()+"/dynab?button_text="+urllib.quote(_("Put to Facebook Wall").encode("utf-8"))+imgopt+"\" border=\"0\" alt=\""+_("Put to Facebook Wall")+"\"></a></p>")
    else:
		aaa = "<h1>Compontet \"%s\" load error</h1>\n" % (modname)


    page = Page.loadnew(modname2)
    page.content = "%s" % (aaa)
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('mod'+modname, textaps+name, ext, name, name))
    page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })


  def post(self, modname, rparameters):

    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    sys.path.append(os.getcwd()+os.path.sep+"componets")
    import importlib
    entitiesRx  = re.compile("[^0-9a-zA-Z]")
    modname = entitiesRx.sub("", modname)
    modloaderr = False
    modname2 = 'custommodule'
    try:
		moduleim = importlib.import_module("mod"+modname)
    except:
        modloaderr = True
    if not modloaderr:
		moduleim = importlib.import_module("mod"+modname)
		modmed = getattr(moduleim, "modobj"+modname)
		modresult = modmed().cont(self)
		if 'cont' in modresult and len(modresult['cont'])>0:
			modcont = modresult['cont']
		else:
			modcont = "<h1>Custom Compontet \"%s\"</h1>\n" % (modname)
		if 'name' in modresult and len(modresult['name'])>0:
			modname2 = modresult['name']
		else:
			modname2 = 'customcomponent'
		if 'fpput' in modresult and modresult['fpput']==True:
			modfpput = True
		else:
			modfpput = False
		if 'title' in modresult and len(modresult['title'])>0:
			modtitle = modresult['title']
		else:
			modtitle = 'Custom Compontet'
		if 'descr' in modresult and len(modresult['descr'])>0:
			moddescr = modresult['descr']
		else:
			moddescr = '   '
#   	 user = users.get_current_user()

		aaa = "%s" % (modcont)
		modes = ['view', 'fbputwall']
		mode = self.request.get('mode')
		if not mode in modes:
			mode = 'view'

		if mode == 'fbputwall' and modfpput:
			fb_current_user=self.fb_current_user
			if fb_current_user:	
				pav = modtitle
				aaa = _("logged Facebook %(fbprofileurl)s %(fbpicurl)s %(fbname)s %(url)s") % {'fbprofileurl': fb_current_user.profile_url,'fbpicurl': "http://graph.facebook.com/"+fb_current_user.id+"/picture",'fbname': fb_current_user.name,'url': '/auth/logout?continue='+urllib.quote(self.request.uri)}
				parerr = False
				if not parerr:
					message = _("Message from:").encode("utf-8")+"\n"+urlhost2()   
					attachment = {}  
					attachment['name'] = pav.encode("utf-8") 
					attachment['caption'] = os.environ['HTTP_HOST']  
					attachment['link'] = urlhost2()+os.environ['PATH_INFO']
					attachment['picture'] = urlhost2()+fbputimgurl2  
					attachment['description'] = moddescr.encode("utf-8")   
					obj=self   
					import fb
					obj = self
					aaa=fb.putwall(obj,message,attachment)
				else:
					aaa="<h1>Error</h1>%s" % (pav)

			else:
				aaa = _("not logged Facebook %(url)s") % {'url': '/auth/login?continue='+urllib.quote(self.request.uri)}
		if mode == 'view' and modfpput:
			aaa = "%s%s" % (aaa,"<p>&nbsp;</p><p><a href=\""+urlhost2()+os.environ['PATH_INFO']+"?mode=fbputwall\"><img src=\""+urlhost2()+"/dynab?button_text="+urllib.quote(_("Put to Facebook Wall").encode("utf-8"))+imgopt+"\" border=\"0\" alt=\""+_("Put to Facebook Wall")+"\"></a></p>")
    else:
		aaa = "<h1>Compontet \"%s\" load error</h1>\n" % (modname)


    page = Page.loadnew(modname2)
    page.content = "%s" % (aaa)
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('mod'+modname, textaps+name, ext, name, name))
    page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })

class ListDir(BaseRequestHandler):

  def get(self, rparameters):

    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    page = Page.loadnew("list")
    user = users.get_current_user()
    greeting = ''
    if user:
      if users.is_current_user_admin():
        items = os.listdir(self.request.get("ls"))
        items.sort()
        for name in items:
           aaa = "%s <br>\n" % (name)
           greeting = greeting + aaa

      else:
        greeting = _("Welcome2 %(admin)s %(usernickname)s %(userlogouturl)s") % {'admin': '', 'usernickname': user.nickname(), 'userlogouturl': users.create_logout_url(self.request.uri)}
        greeting = greeting + " " + _("and") + " " + (_("sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)})
    else:
      greeting = _("Sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}
    page.content = _("List header %(greeting)s") % {'greeting': greeting}
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('ls', textaps+name, ext, name, name))
    page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })

class Greeting(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)



class SingGuestbook(BaseRequestHandler):
  def post(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    greeting = Greeting()
    aaa=""

    if users.get_current_user():
      greeting = Greeting()
      greeting.author = users.get_current_user()

      greeting.content = self.request.get('content')
      greeting.put()
#    self.redirect('/')
      aaa = _("Guestbook 2")
    else:
      aaa = _("Guestbook 1 %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}

    page = Page.loadnew("guestbook")
    page.content = aaa
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'menu': page2,
      'page': page,
    })


class WikiGuest(BaseRequestHandler):
  def get(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    aaa=""
    pg=self.request.get('pg')
    entitiesRx  = re.compile("[^0-9]")
    pg=entitiesRx.sub("", pg)
    if pg:
      pg = int(pg)
    else:
      pg=0

    query = db.GqlQuery("SELECT * "
                            "FROM Greeting "
                            "ORDER BY date DESC")
    greetings = query.fetch(10,pg*10)
#    query = Greeting.all()
    co=query.count()
    i=0
    ii=0
    bbb=""
    while i<=co:
      i=i+10
      if ii == pg:
        bbb=bbb+' '+str(ii)
      else:
        bbb=bbb+' '+"<a href=\""+'/'+cmspath2+'-guestbook-'+lang+'.'+fileext+"?pg="+ str(ii) +"\">"+ str(ii) +"</a>"
      ii=ii+1
      
    aaa=aaa+"<center>"+bbb+"</center><br>\n"
    for greeting in greetings:
      if greeting.author:
        ccc1=''
        ccc1=_("Guestbook 3 %(greetingusernickname)s post") % {'greetingusernickname': greeting.author.nickname()}
        aaa=aaa+ccc1
      else:
        aaa=aaa + _("Guestbook 4 anonymous post")
      aaa=aaa+('<blockquote>%s</blockquote>' %
                              cgi.escape(greeting.content))

    if users.get_current_user():
      aaa=aaa+(_("Guestbook 5 %(guestsendurl)s") % {'guestsendurl': '/'+cmspath2+'-sing-'+lang+'.'+fileext})
    else:
      ccc2 = ''
      ccc2 = _("Guestbook 6 %(guestuserloginurl)s") % {'guestuserloginurl': users.create_login_url(self.request.uri)}
      aaa=aaa+ccc2


    page = Page.loadnew("guestbook")
    page.content = _("Guestbook header %(guestgreeting)s") % {'guestgreeting': aaa} 
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('guestbook', textaps+name, ext, name, name))
    page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })

class MailForm(BaseRequestHandler):
  def get(self, rparameters):

    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    codekey=codekey2()

    page2 = Page.load("pasl-"+lang+'.'+fileext)
    page = Page.loadnew("mailform")
    user = users.get_current_user()
    greeting = ''
#    if user:
    greeting = _("Mail form %(mailsendurl)s %(mailcodekey)s") % {'mailsendurl': '/'+cmspath2+'-sendmail-'+lang+'.'+fileext,'mailcodekey': codekey}

#    else:
#      greeting = "<p><a href=\""+users.create_login_url(self.request.uri)+u"\">Please login</a> with Google account.</p>"
    page.content = u""+page2.content+greeting+""
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('mailform', textaps+name, ext, name, name))
    page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })

class MailSend(BaseRequestHandler):
#    @login_required
    def post(self, rparameters):
        param=urlparam(rparameters)
        ext=param['ext']
        lang=param['lang']
        aps=param['aps']
        kalb=param['kalb']
        lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
        _ = lang1.ugettext
        try:
            codeimg = db.get(self.request.get("scodeid"))
        except:
            prn="Error"
#        codeimg = db.get(self.request.get("scodeid"))
        if codeimg and codeimg.code == self.request.get("scode"):
            codeimg.delete()
            x_zmail = self.request.get("zemail")
            x_subject = self.request.get("zsubject")
            x_realname = self.request.get("zrealname")
            x_message = self.request.get("zmessage")
            to_addr = _mailrcptto
            user = users.get_current_user()
            if user:
                uname=user.nickname()
                umail=users.get_current_user().email()
            else:
                uname=""
                umail=""
            if not mail.is_email_valid(to_addr):
                # Return an error message...
                pass
            message = mail.EmailMessage()
            message.subject = os.environ['HTTP_HOST'] + " maiform - " +x_subject.encode("utf-8")
#        message.subject = "www"
            message.sender = _mailsender
            message.to = to_addr
#            q_uname = uname.encode("utf-8")
#            q_umail = umail.encode("utf-8")
#            q_zmail = x_zmail.encode("utf-8")
#            q_realname = x_realname.encode("utf-8")
#            q_message = x_message.encode("utf-8")

            q_uname = ''
            q_umail = ''
            q_zmail = ''
            q_realname = ''
            q_message = ''
            q_uname = uname
            q_umail = umail
            q_zmail = x_zmail
            q_realname = x_realname
            q_message = x_message + ("\n%s: %s \n%s \n%s \n" % ('Page', str(self.request.uri),str(textinfo()),str(textloc())))

            message.body = (_("Mail message %(mailuname)s %(mailumail)s %(mailrealname)s %(mailzmail)s %(mailmessage)s") % {'mailuname': q_uname, 'mailumail': q_umail, 'mailrealname': q_realname, 'mailzmail': q_zmail, 'mailmessage': q_message})
            message.send()
            ptext=_("Mail send OK")
        else:
            ptext=_("Mail send Error")
        page = Page.loadnew("sendmail")
        page.content = ptext
        page_name2 = 'menu'+'-'+lang+'.'+fileext
        page2 = Page.load(page_name2)
        self.generate('view.html', lang, {
          'imgshar': False,
          'noedit': '1',
          'application_name': siteauth(),
          'menu': page2,
          'page': page,
        })


class Page(object):
  """Our abstraction for a Wiki page.

  We handle all datastore operations so that new pages are handled
  seamlessly. To create OR edit a page, just create a Page instance and
  clal save().
  """
  def __init__(self, name, entity=None):
    self.name = name
    self.entity = entity
    if entity:
      self.content = entity['content']
      if entity.has_key('user'):
        self.user = entity['user']
      else:
        self.user = None
      self.created = entity['created']
      self.modified = entity['modified']
      self.sitemaprodyti=entity['sitemaprodyti']
      self.rssrodyti=entity['rssrodyti']
      self.sitemapfreq=entity['sitemapfreq']
      self.sitemapprio=entity['sitemapprio']
      if "commenablego" in entity:
        self.commenablego=entity['commenablego']
      else:
        self.commenablego=False
      if "commenablefb" in entity:
        self.commenablefb=entity['commenablefb']
      else:
        self.commenablefb=False
      if "commenableli" in entity:
        self.commenableli=entity['commenableli']
      else:
        self.commenableli=False
      if "commenablevk" in entity:
        self.commenablevk=entity['commenablevk']
      else:
        self.commenablevk=False

    else:
      # New pages should start out with a simple title to get the user going
      now = datetime.datetime.now()
      if not name=="menu":
            self.content = '<h1>' + cgi.escape(name) + '</h1>'
      self.user = None
      self.created = now
      self.modified = now
      self.rssrodyti=False
      self.sitemaprodyti=False
      self.sitemapfreq='weekly'
      self.sitemapprio='0.5'
      self.commenablego=False
      self.commenablefb=False
      self.commenableli=False
      self.commenablevk=False

  def entity(self):
    return self.entity

  def edit_url(self):
    return '/'+cmspath2+'-' + self.name + '?mode=edit'

  def view_url(self):
    return '/'+cmspath2+'-' + self.name

  def wikified_content(self):
    """Applies our wiki transforms to our content for HTML display.

    We auto-link URLs, link WikiWords, and hide referers on links that
    go outside of the Wiki.
    """
    transforms = [
#      AutoLink(),
#      WikiWords(),
#      HideReferers(),
    ]
    content = self.content
    for transform in transforms:
      content = transform.run(content)
    return content

  def save(self):
    """Creates or edits this page in the datastore."""
    now = datetime.datetime.now()
    if self.entity:
      entity = self.entity
    else:
      entity = datastore.Entity('Page')
      entity['name'] = self.name
      entity['created'] = now
      entity['rssrodyti'] = self.rssrodyti
      entity['sitemaprodyti'] = self.sitemaprodyti
      entity['sitemapfreq'] = self.sitemapfreq
      entity['sitemapprio'] = self.sitemapprio
      entity['commenablego'] = self.commenablego
      entity['commenablefb'] = self.commenablefb
      entity['commenableli'] = self.commenableli
      entity['commenablevk'] = self.commenablevk
    entity['content'] = datastore_types.Text(self.content)
    entity['modified'] = now

    if users.GetCurrentUser():
      entity['user'] = users.GetCurrentUser()
    elif entity.has_key('user'):
      del entity['user']

    datastore.Put(entity)

  @staticmethod
  def loadnew(name):
      return Page(name)

  @staticmethod
  def load(name):
    """Loads the page with the given name.

    We always return a Page instance, even if the given name isn't yet in
    the database. In that case, the Page object will be created when save()
    is called.
    """
    query = datastore.Query('Page')
    query['name ='] = name
    entities = query.Get(1)
    if len(entities) < 1:
      return Page(name)
    else:
      return Page(name, entities[0])

  @staticmethod
  def exists(name):
    """Returns true if the page with the given name exists in the datastore."""
    return Page.load(name).entity


class Transform(object):
  """Abstraction for a regular expression transform.

  Transform subclasses have two properties:
     regexp: the regular expression defining what will be replaced
     replace(MatchObject): returns a string replacement for a regexp match

  We iterate over all matches for that regular expression, calling replace()
  on the match to determine what text should replace the matched text.

  The Transform class is more expressive than regular expression replacement
  because the replace() method can execute arbitrary code to, e.g., look
  up a WikiWord to see if the page exists before determining if the WikiWord
  should be a link.
  """
  def run(self, content):
    """Runs this transform over the given content.

    We return a new string that is the result of this transform.
    """
    parts = []
    offset = 0
    for match in self.regexp.finditer(content):
      parts.append(content[offset:match.start(0)])
      parts.append(self.replace(match))
      offset = match.end(0)
    parts.append(content[offset:])
    return ''.join(parts)


class WikiWords(Transform):
  """Translates WikiWords to links.

  We look up all words, and we only link those words that currently exist.
  """
  def __init__(self):
    self.regexp = re.compile(r'[A-Z][a-z]+([A-Z][a-z]+)+')

  def replace(self, match):
    wikiword = match.group(0)
    if Page.exists(wikiword):
      return '<a class="wikiword" href="/%s">%s</a>' % (wikiword, wikiword)
    else:
      return wikiword


class AutoLink(Transform):
  """A transform that auto-links URLs."""
  def __init__(self):
    self.regexp = re.compile(r'([^"])\b((http|https)://[^ \t\n\r<>\(\)&"]+' \
                             r'[^ \t\n\r<>\(\)&"\.])')

  def replace(self, match):
    url = match.group(2)
    return match.group(1) + '<a class="autourl" href="%s">%s</a>' % (url, url)


class HideReferers(Transform):
  """A transform that hides referers for external hyperlinks."""

  def __init__(self):
    self.regexp = re.compile(r'href="(http[^"]+)"')

  def replace(self, match):
    url = match.group(1)
    scheme, host, path, parameters, query, fragment = urlparse.urlparse(url)
    url = 'http://www.google.com/url?sa=D&amp;q=' + urllib.quote(url)
    return 'href="' + url + '"'

class VarId(BaseRequestHandler):
  def get(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    query = db.GqlQuery("SELECT * "
                            "FROM Vartotojai "
                            "ORDER BY laikas DESC")
    for greeting in query:
      greeting.userid=greeting.lankytojas.user_id()
      greeting.put()
    page = Page.loadnew("suradimas")
    page.content = u'<h1>Suradimas</h1>'+""
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('searchid', textaps+name, ext, name, name))
    page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })

class VartSar(BaseRequestHandler):
  def get(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    aaa=""
    pg=self.request.get('pg')
    entitiesRx  = re.compile("[^0-9]")
    pg=entitiesRx.sub("", pg)
    if pg:
      pg = int(pg)
    else:
      pg=0

    query = db.GqlQuery("SELECT * "
                            "FROM Vartotojai "
                            "ORDER BY laikas DESC")
    greetings = query.fetch(10,pg*10)
    co=query.count()
    i=0
    ii=0
    bbb=""
    while i<=co:
      i=i+10
      if ii == pg:
        bbb=bbb+' '+str(ii)
      else:
        bbb=bbb+' '+"<a href=\"/"+cmspath2+"-memberlist-"+lang+'.'+fileext+"?pg="+ str(ii) +"\">"+ str(ii) +"</a>"
      ii=ii+1
      
    aaa=aaa+"<center>"+bbb+"</center><br>\n"

    for greeting in greetings:
      buvoapp = greeting.rodyti
      userid = greeting.userid
      content = greeting.content
      pseudonimas = greeting.pseudonimas
      if buvoapp:
        imagemaxurl = ("/"+cmspath2+"-userimagemin/%s/%s" % (pseudonimas, userid))
      else:
        imagemaxurl = avatarminurl2
      if greeting.lankytojas:
        thubnail=getphoto(greeting.lankytojas.email())
        if not thubnail:
            thubnail = imagemaxurl
        userpageurl = ("%s/%s-userpage-%s.%s/%s/%s" % (urlhost2(), cmspath2,lang, fileext, pseudonimas, userid))
        userpicaurl = ("%s/picaenable2?user=%s" % (urlhost2(), greeting.lankytojas.email()))
        userplusurl = ("%s/avatar2?user=%s" % (urlhost2(), greeting.lankytojas.email()))
        aaa=aaa+(("<a href=\"%s\"><img src=\"%s\"+ border=\"0\"><img src=\"%s\"+ border=\"0\"><br>\n\n<strong>%s</strong></a> <a href=\"%s\">Plus</a> <a href=\"%s\">Picasa</a><br>google user: <b>%s</b> email: %s") % (userpageurl,imagemaxurl,thubnail,pseudonimas,userplusurl,userpicaurl,greeting.lankytojas.nickname(),greeting.lankytojas.email()))
      else:
        aaa=aaa+''
      iplink = ("<a href=\"%s/logs3?filter=%s\">%s</a>" % (urlhost2(), greeting.ipadresas,greeting.ipadresas))
      aaa=aaa+(_("Memberlist entry msg %(memlisttime)s %(memlistipaddr)s %(memlistbrowser)s") % {'memlisttime': greeting.laikas, 'memlistipaddr': iplink, 'memlistbrowser': greeting.narsykle}) 

    if not users.get_current_user() or not users.is_current_user_admin():
      aaa = _("Sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}
    page = Page.loadnew("memberlist")
    page.content = _("Memberlist header %(memlistgreeting)s") % {'memlistgreeting': aaa}
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('memberlist', textaps+name, ext, name, name))
    page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })
class VartSarTrumpas(BaseRequestHandler):
  def get(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    aaa=""
    pg=self.request.get('pg')
    entitiesRx  = re.compile("[^0-9]")
    pg=entitiesRx.sub("", pg)
    if pg:
      pg = int(pg)
    else:
      pg=0

    query = db.GqlQuery("SELECT * "
                            "FROM Vartotojai "
                            "ORDER BY laikas DESC")
    greetings = query.fetch(8,pg*8)
    co=query.count()
    i=0
    ii=0
    bbb=""
    while i<=co:
      i=i+8
      if ii == pg:
        bbb=bbb+' '+str(ii)
      else:
        bbb=bbb+' '+"<a href=\"/"+cmspath2+"-memberlistshort-"+lang+'.'+fileext+"?pg="+ str(ii) +"\">"+ str(ii) +"</a>"
      ii=ii+1
      
#    aaa=aaa+"<center>"+bbb+"</center><br>\n"
    aaa=aaa+"<table  cellspacing=\"0\" cellpadding=\"0\">\n"
    z = 0
    for greeting in greetings:
      z = z + 1
      if z==1:
        aaa=aaa+"<tr height=\"50\">\n"
      buvoapp = greeting.rodyti
      userid = greeting.userid
      content = greeting.content
      pseudonimas = greeting.pseudonimas
      if buvoapp:
        imagemaxurl = ("/%s-userimagemin/%s/%s" % (cmspath2,pseudonimas, userid))
      else:
        imagemaxurl = avatarminurl2
      if greeting.lankytojas:
        thubnail=getphoto(greeting.lankytojas.email())
        if thubnail and not buvoapp:
            imagemaxurl = str(thubnail)
            uphoto=imagemaxurl.split("/s144/", 1)
            slasas="/s50/"
            imagemaxurl = slasas.join(uphoto)
        userpageurl = ("%s/%s-userpage-%s.%s/%s/%s" % (urlhost2(), cmspath2 ,lang, fileext, pseudonimas, userid))
        aaa=aaa+(("<td width=\"50\"><a href=\"%s\" target=\"_top\"><img src=\"%s\" border=\"0\" alt=\"%s\"></a></td>\n") % (userpageurl,imagemaxurl,pseudonimas))
      else:
        aaa=aaa+''
      if z==2:
        z=0
        aaa=aaa+"\n</tr>"
#      aaa=aaa+(_("Memberlist entry msg %(memlisttime)s %(memlistipaddr)s %(memlistbrowser)s") % {'memlisttime': greeting.laikas, 'memlistipaddr': greeting.ipadresas, 'memlistbrowser': greeting.narsykle}) 
    if z==1:
      aaa=aaa+"<td width=\"50\">&nbsp</td></tr>"
    if z==0:
      aaa=aaa+"\n</tr>"
    aaa=aaa+"\n</table>"
#    if not users.get_current_user() or not users.is_current_user_admin():
#      aaa = _("Sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}
    page = Page.loadnew("memberlist")
    page.content = aaa
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('memberlist', textaps+name, ext, name, name))
    page3.content = text
    self.generate('viewicon.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })
class FBUserListSort(BaseRequestHandler):
  def get(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    aaa=""
    pg=self.request.get('pg')
    entitiesRx  = re.compile("[^0-9]")
    pg=entitiesRx.sub("", pg)
    if pg:
      pg = int(pg)
    else:
      pg=0

    query = db.GqlQuery("SELECT * "
                            "FROM FBUser "
                            "ORDER BY updated DESC")
    greetings = query.fetch(8,pg*8)
    co=query.count()
    i=0
    ii=0
    bbb=""
    while i<=co:
      i=i+8
      if ii == pg:
        bbb=bbb+' '+str(ii)
      else:
        bbb=bbb+' '+"<a href=\"/"+cmspath2+"-fbmemberlistshort-"+lang+'.'+fileext+"?pg="+ str(ii) +"\">"+ str(ii) +"</a>"
      ii=ii+1
      
#    aaa=aaa+"<center>"+bbb+"</center><br>\n"
    aaa=aaa+"<table  cellspacing=\"0\" cellpadding=\"0\">\n"
    z = 0
    for greeting in greetings:
      z = z + 1
      if z==1:
        aaa=aaa+"<tr height=\"50\">\n"
      userid = greeting.id
      pseudonimas = greeting.nickname
      imagemaxurl = ("http://graph.facebook.com/%s/picture" % (userid))
      if greeting.id:
#        userpageurl = ("http://www.facebook.com/profile.php?id=%s" % (userid))
        userpageurl = ("%s/fbinfo?id=%s" % (urlhost2(),userid))
        aaa=aaa+(("<td width=\"50\"><a href=\"%s\" target=\"_top\"><img src=\"%s\" border=\"0\" alt=\"%s\"></a></td>\n") % (userpageurl,imagemaxurl,pseudonimas))
      else:
        aaa=aaa+''
      if z==2:
        z=0
        aaa=aaa+"\n</tr>"
#      aaa=aaa+(_("Memberlist entry msg %(memlisttime)s %(memlistipaddr)s %(memlistbrowser)s") % {'memlisttime': greeting.laikas, 'memlistipaddr': greeting.ipadresas, 'memlistbrowser': greeting.narsykle}) 
    if z==1:
      aaa=aaa+"<td width=\"50\">&nbsp</td></tr>"
    if z==0:
      aaa=aaa+"\n</tr>"
    aaa=aaa+"\n</table>"
#    if not users.get_current_user() or not users.is_current_user_admin():
#      aaa = _("Sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}
    page = Page.loadnew("fbmemberlist")
    page.content = aaa
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('fbmemberlist', textaps+name, ext, name, name))
    page3.content = text
    self.generate('viewicon.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })
class LIUserListSort(BaseRequestHandler):
  def get(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    aaa=""
    pg=self.request.get('pg')
    entitiesRx  = re.compile("[^0-9]")
    pg=entitiesRx.sub("", pg)
    if pg:
      pg = int(pg)
    else:
      pg=0

    query = db.GqlQuery("SELECT * "
                            "FROM LIUser "
                            "ORDER BY updated DESC")
    greetings = query.fetch(8,pg*8)
    co=query.count()
    i=0
    ii=0
    bbb=""
    while i<=co:
      i=i+8
      if ii == pg:
        bbb=bbb+' '+str(ii)
      else:
        bbb=bbb+' '+"<a href=\"/"+cmspath2+"-fbmemberlistshort-"+lang+'.'+fileext+"?pg="+ str(ii) +"\">"+ str(ii) +"</a>"
      ii=ii+1
      
#    aaa=aaa+"<center>"+bbb+"</center><br>\n"
    aaa=aaa+"<table  cellspacing=\"0\" cellpadding=\"0\">\n"
    z = 0
    for greeting in greetings:
      z = z + 1
      if z==1:
        aaa=aaa+"<tr height=\"50\">\n"
      ukey = greeting.key()
      userid = greeting.id
      pseudonimas = greeting.nickname
      profile_url = greeting.profile_url
      liuname = greeting.name
      directory = os.path.dirname(__file__)
      pathimg = os.path.join(directory, 'liphoto2.py')
      if os.path.exists(pathimg) and os.path.isfile(pathimg):
        imagemaxurl = ("%s/liphoto2/%s" % (urlhost2(),ukey))
      else:
        imagemaxurl = ("%s%s" % (urlhost2(),avatarminurl2))
      if greeting.id:
#        userpageurl = ("http://www.facebook.com/profile.php?id=%s" % (userid))
        userpageurl = profile_url
        aaa=aaa+(("<td width=\"50\"><a href=\"%s\" target=\"_top\"><img src=\"%s\" border=\"0\" alt=\"%s\"></a></td>\n") % (userpageurl,imagemaxurl,pseudonimas))
      else:
        aaa=aaa+''
      if z==2:
        z=0
        aaa=aaa+"\n</tr>"
#      aaa=aaa+(_("Memberlist entry msg %(memlisttime)s %(memlistipaddr)s %(memlistbrowser)s") % {'memlisttime': greeting.laikas, 'memlistipaddr': greeting.ipadresas, 'memlistbrowser': greeting.narsykle}) 
    if z==1:
      aaa=aaa+"<td width=\"50\">&nbsp</td></tr>"
    if z==0:
      aaa=aaa+"\n</tr>"
    aaa=aaa+"\n</table>"
#    if not users.get_current_user() or not users.is_current_user_admin():
#      aaa = _("Sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}
    page = Page.loadnew("limemberlist")
    page.content = aaa
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('fbmemberlist', textaps+name, ext, name, name))
    page3.content = text
    self.generate('viewicon.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })
class VKUserListSort(BaseRequestHandler):
  def get(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    aaa=""
    pg=self.request.get('pg')
    entitiesRx  = re.compile("[^0-9]")
    pg=entitiesRx.sub("", pg)
    if pg:
      pg = int(pg)
    else:
      pg=0

    query = db.GqlQuery("SELECT * "
                            "FROM VKUser "
                            "ORDER BY updated DESC")
    greetings = query.fetch(8,pg*8)
    co=query.count()
    i=0
    ii=0
    bbb=""
    while i<=co:
      i=i+8
      if ii == pg:
        bbb=bbb+' '+str(ii)
      else:
        bbb=bbb+' '+"<a href=\"/"+cmspath2+"-vkmemberlistshort-"+lang+'.'+fileext+"?pg="+ str(ii) +"\">"+ str(ii) +"</a>"
      ii=ii+1
      
#    aaa=aaa+"<center>"+bbb+"</center><br>\n"
    aaa=aaa+"<table  cellspacing=\"0\" cellpadding=\"0\">\n"
    z = 0
    for greeting in greetings:
      z = z + 1
      if z==1:
        aaa=aaa+"<tr height=\"50\">\n"
      userid = greeting.id
      pseudonimas = greeting.nickname
      directory = os.path.dirname(__file__)
      pathimg = os.path.join(directory, 'vkphoto.py')
      if os.path.exists(pathimg) and os.path.isfile(pathimg):
        imagemaxurl = ("/vkphoto/%s" % (userid))
      else:
        imagemaxurl = ("%s%s" % (urlhost2(),avatarminurl2))

      if greeting.id:
#        userpageurl = ("http://www.facebook.com/profile.php?id=%s" % (userid))
#        userpageurl = ("%s/fbinfo?id=%s" % (urlhost2(),userid))
        userpageurl = greeting.profile_url
        aaa=aaa+(("<td width=\"50\"><a href=\"%s\" target=\"_top\"><img src=\"%s\" border=\"0\" alt=\"%s\"></a></td>\n") % (userpageurl,imagemaxurl,pseudonimas))
      else:
        aaa=aaa+''
      if z==2:
        z=0
        aaa=aaa+"\n</tr>"
#      aaa=aaa+(_("Memberlist entry msg %(memlisttime)s %(memlistipaddr)s %(memlistbrowser)s") % {'memlisttime': greeting.laikas, 'memlistipaddr': greeting.ipadresas, 'memlistbrowser': greeting.narsykle}) 
    if z==1:
      aaa=aaa+"<td width=\"50\">&nbsp</td></tr>"
    if z==0:
      aaa=aaa+"\n</tr>"
    aaa=aaa+"\n</table>"
#    if not users.get_current_user() or not users.is_current_user_admin():
#      aaa = _("Sign in on Administrator %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}
    page = Page.loadnew("vkmemberlist")
    page.content = aaa
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)
    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('vkmemberlist', textaps+name, ext, name, name))
    page3.content = text
    self.generate('viewicon.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })
class SiteDisable(webapp.RequestHandler):

  def get(self,pagename):
    disablecode = "<html><body>Disable, swith to on</body></html>"
    try:  
        codedb = db.GqlQuery("SELECT * FROM DinCode WHERE codename = :1", "disable")
        for thiscode in codedb:
            disablecode = thiscode.codetext
    except:
        disablecode = "<html><body>Disable, swith to on</body></html>"
    self.response.out.write(disablecode)
  def post(self,pagename):
    disablecode = "<html><body>Disable, swith to on</body></html>"
    try:  
        codedb = db.GqlQuery("SELECT * FROM DinCode WHERE codename = :1", "disable")
        for thiscode in codedb:
            disablecode = thiscode.codetext
    except:
        disablecode = "<html><body>Disable, swith to on</body></html>"
    self.response.out.write(disablecode)

class HttpError(webapp.RequestHandler):

  def get(self,pagename):
    disablecode = "<html><body>over quota - website flood botnet</body></html>"
    self.response.out.write(disablecode)
  def post(self,pagename):
    disablecode = "<html><body>over quota - website flood botnet</body></html>"
    self.response.out.write(disablecode)


class PicaAlbumOn(db.Model):
  lankytojas = db.UserProperty(required=True)
  laikas = db.DateTimeProperty(auto_now_add=True)
  administratorius = db.BooleanProperty()
  ipadresas = db.StringProperty()
  userid = db.StringProperty()
  rodyti = db.BooleanProperty()
  albumname = db.StringProperty()
class SpamIP(db.Model):
  ipadresas = db.StringProperty()
  lastserver = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  check = db.BooleanProperty()
  spamcount = db.StringProperty()
  spam = db.BooleanProperty()
class Commentsrec(db.Model):
#  laikas = db.DateTimeProperty(auto_now_add=True)
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  rname = db.StringProperty(multiline=False)
  avatar = db.BlobProperty()
  avatarmax = db.BlobProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  ipadresas = db.StringProperty()
  rodyti = db.BooleanProperty()
class Commentsrec2(db.Model):
#  laikas = db.DateTimeProperty(auto_now_add=True)
  vartot = db.ReferenceProperty(Vartotojai, collection_name='komentarai')
  author = db.UserProperty()
  userid = db.StringProperty()
  content = db.StringProperty(multiline=True)
  rname = db.StringProperty(multiline=False)
  avatar = db.BlobProperty()
  avatarmax = db.BlobProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  ipadresas = db.StringProperty()
  rodyti = db.BooleanProperty()
class Commentsrec3(db.Model):
#  laikas = db.DateTimeProperty(auto_now_add=True)
  commpage = db.StringProperty()
  vartot = db.ReferenceProperty(Vartotojai, collection_name='komentarai-go')
  vartotfb = db.ReferenceProperty(FBUser, collection_name='komentarai-fb')
  vartotli = db.ReferenceProperty(LIUser, collection_name='komentarai-li')
  vartotvk = db.ReferenceProperty(VKUser, collection_name='komentarai-vk')
  author = db.UserProperty()
  userid = db.StringProperty()
  content = db.StringProperty(multiline=True)
  rname = db.StringProperty(multiline=False)
  avatar = db.BlobProperty()
  avatarmax = db.BlobProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  ipadresas = db.StringProperty()
  rodyti = db.BooleanProperty()

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
            plusid = "https://plus."+r.search(data).group(2)
            yra=True
        if yra:
            return plusid
        else:
            return False
    except:
       return False

class UserControl(BaseRequestHandler):
 def get(self,rparameters):
#  self.response.out.write('<html><head><style>body {	text-align: center;	font: 11px arial, sans-serif;	color: #565656; } .clear { clear:both; } .comm-container { margin-bottom:20px;} .comm-name { font-size:10pt; float:left; width:20%; padding:5px; overflow:hidden; } .comm-text { float:left; line-height:17px; width:70%; padding:5px; padding-top:0px; overflow:hidden; } .font-small-gray { font-size:10pt !important; }</style></head><body>')
  param=urlparam(rparameters)
  ext=param['ext']
  lang=param['lang']
  aps=param['aps']
  kalb=param['kalb']
  lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
  _ = lang1.ugettext
  wtext=""
     
  codekey=codekey2()
  buvoapp = False
  rpica = False
  rplus = True
  rcomm = True
  userid = "0"
  content = ""
  pseudonimas = "Anonymous"
  thubnail = avatarmaxurl2
  thubnail2 = avatarmaxurl2
  eee=""
  rpicacheck = "" 
  rcommcheck = "" 
  buvoappcheck="" 
  youtname="" 
  if users.get_current_user():
    user = users.get_current_user()
    userinfo2=userinfo(user ,False,lang,ext)
    imagemaxurl = userinfo2['imagemaxurl']
    userpageend = userinfo2['userpageend']
    userpicapagetext = userinfo2['userpicapagetext']
    usercpplustext = userinfo2['usercpplustext']
    usermailformtext = userinfo2['usermailformtext']
    usermailformpageurl = userinfo2['usermailformpageurl']
    useryoutpageurl = userinfo2['useryoutpageurl']
    userpicapageurl = userinfo2['userpicapageurl']
    usercommpageurl = userinfo2['usercommpageurl']
    usercpurl = userinfo2['usercpurl']
    pseudonimas = userinfo2['pseudonimas']
    userid = userinfo2['userid']
    content = userinfo2['content2']
    youtname = userinfo2['youtname']
    vartot = userinfo2['vartot']
    rcomm = userinfo2['rcomm']
    rpica = userinfo2['rpica']
    lank = userinfo2['lank']
    userpageurl= userinfo2['userpageurl']
    rcommcheck= userinfo2['rcommcheck']
    rpluscheck= userinfo2['rpluscheck']
    rpicacheck= userinfo2['rpicacheck']
    buvoappcheck= userinfo2['buvoappcheck']
    usercppicaurl = ("/%s-userpicacontrol-%s.%s" % (cmspath2,lang,fileext))

  if users.get_current_user():
    wtext = wtext + _("user control panel header") + "<br>" + "<img src=\""+imagemaxurl+"\" border=\"0\"><img src=\""+thubnail2+"\" border=\"0\"><br>\n\n"+usercpplustext+(_("User control panel form %(usercpsendurl)s %(usercpcodekey)s %(usercpuserid)s %(usercpcontent)s %(usercppseudonimas)s %(rpluscheck)s %(rpicacheck)s %(buvoappcheck)s %(youtname)s %(rcommcheck)s")  % {'usercpsendurl': '/'+cmspath2+'-usercpsubmit-'+lang+'.'+fileext, 'usercpcodekey': codekey, 'usercpuserid': userid, 'usercpcontent': content,'usercppseudonimas': pseudonimas,'rpluscheck': rpluscheck,'rpicacheck': rpicacheck,'buvoappcheck': buvoappcheck,'youtname': youtname,'rcommcheck': rcommcheck})
    if rpica:
      wtext = wtext + (_("pica control link %(usercppicaurl)s") % {'usercppicaurl': usercppicaurl})
    if userid != "0":
      wtext = wtext + (_("vartotojo puslapis %(usercppseudonimas)s %(userpageurl)s") % {'usercppseudonimas': pseudonimas, 'userpageurl': userpageurl})
  else:
    wtext = wtext + _("user control panel header") + "<br>" + (_("Sign in or register %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)})
  page = Page.loadnew("usercontrolpanel")
  page.content = wtext
  page_name2 = 'menu'+'-'+lang+'.'+fileext
  page2 = Page.load(page_name2)
  page3 = Page.loadnew("kalbos")
  textaps=''
  if len(aps)>0:
    textaps=aps+'.'
  text=''
  for name, value in kalbossort:
    text = text + (_kalbhtml % ('usercontrolpanel', textaps+name, ext, name, name))
  page3.content = text
  self.generate('view.html', lang, {
    'imgshar': False,
    'noedit': '1',
    'application_name': siteauth(),
    'kalbos': page3,
    'menu': page2,
    'page': page,
  })

class UserShowPage(BaseRequestHandler):
 def get(self,rparameters, pseudonim , pic_key):
#  self.response.out.write('<html><head><style>body {	text-align: center;	font: 11px arial, sans-serif;	color: #565656; } .clear { clear:both; } .comm-container { margin-bottom:20px;} .comm-name { font-size:10pt; float:left; width:20%; padding:5px; overflow:hidden; } .comm-text { float:left; line-height:17px; width:70%; padding:5px; padding-top:0px; overflow:hidden; } .font-small-gray { font-size:10pt !important; }</style></head><body>')
  param=urlparam(rparameters)
  ext=param['ext']
  lang=param['lang']
  aps=param['aps']
  kalb=param['kalb']
  lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
  _ = lang1.ugettext
  wtext=""
     
  codekey=codekey2()
  userinfo2=userinfo(pic_key, True,lang,ext)
  imagemaxurl = userinfo2['imagemaxurl']
  userpageend = userinfo2['userpageend']
  userpicapagetext = userinfo2['userpicapagetext']
  usercpplustext = userinfo2['usercpplustext']
  usermailformtext = userinfo2['usermailformtext']
  usermailformpageurl = userinfo2['usermailformpageurl']
  useryoutpageurl = userinfo2['useryoutpageurl']
  userpicapageurl = userinfo2['userpicapageurl']
  usercommpageurl = userinfo2['usercommpageurl']
  usercpurl = userinfo2['usercpurl']
  pseudonimas = userinfo2['pseudonimas']
  userid = userinfo2['userid']
  content = userinfo2['content']
  lank = userinfo2['lank']
  userpageurl= userinfo2['userpageurl']

  wtext = wtext + (_("user page header %(pseudonimas)s") % {'pseudonimas': pseudonimas}) + "<br>" + "<img src=\""+imagemaxurl+"\"  border=\"0\" id=\"profile_pic\"><br>\n\n"+usercpplustext+(_("User page %(usercpuserid)s %(usercpcontent)s %(usercppseudonimas)s %(usercpurl)s %(userpicapagetext)s %(usermailformtext)s")  % { 'usercpuserid': userid, 'usercpcontent': content,'usercppseudonimas': pseudonimas, 'usercpurl': usercpurl, 'userpicapagetext': userpicapagetext,'usermailformtext': usermailformtext})
  page = Page.loadnew("userpage")
  page.content = wtext
  page_name2 = 'menu'+'-'+lang+'.'+fileext
  page2 = Page.load(page_name2)
  page3 = Page.loadnew("kalbos")
  textaps=''
  if len(aps)>0:
    textaps=aps+'.'
  text=''
  for name, value in kalbossort:
    text = text + (_kalbhtml % ('userpage', textaps+name, userpageend, name, name))
  page3.content = text
  self.generate('view.html', lang, {
    'imgshar': False,
    'noedit': '1',
    'application_name': siteauth(),
    'kalbos': page3,
    'menu': page2,
    'page': page,
  })


class UserYoutPage(BaseRequestHandler):
 def get(self,rparameters, pseudonim , pic_key):
#  self.response.out.write('<html><head><style>body {	text-align: center;	font: 11px arial, sans-serif;	color: #565656; } .clear { clear:both; } .comm-container { margin-bottom:20px;} .comm-name { font-size:10pt; float:left; width:20%; padding:5px; overflow:hidden; } .comm-text { float:left; line-height:17px; width:70%; padding:5px; padding-top:0px; overflow:hidden; } .font-small-gray { font-size:10pt !important; }</style></head><body>')
  param=urlparam(rparameters)
  ext=param['ext']
  lang=param['lang']
  aps=param['aps']
  kalb=param['kalb']
  lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
  _ = lang1.ugettext
  wtext=""
     
#  codekey=codekey2()
  userinfo2=userinfo(pic_key, True,lang,ext)
  imagemaxurl = userinfo2['imagemaxurl']
  userpageend = userinfo2['userpageend']
  userpicapagetext = userinfo2['userpicapagetext']
  usercpplustext = userinfo2['usercpplustext']
  usermailformtext = userinfo2['usermailformtext']
  usermailformpageurl = userinfo2['usermailformpageurl']
  useryoutpageurl = userinfo2['useryoutpageurl']
  userpicapageurl = userinfo2['userpicapageurl']
  usercommpageurl = userinfo2['usercommpageurl']
  usercpurl = userinfo2['usercpurl']
  pseudonimas = userinfo2['pseudonimas']
  userid = userinfo2['userid']
  content = userinfo2['content']
  youtname = userinfo2['youtname']
  lank = userinfo2['lank']
  userpageurl= userinfo2['userpageurl']

  youtname = ""
  if  youtname and len(str(youtname))>0:
    yra=False
    out=""
    try:
        if not yra:
            f = urllib.urlopen("https://gdata.youtube.com/feeds/api/users/%s/uploads?v=2&alt=jsonc" % youtname)
            data = json.loads(f.read())
            out=out+"<table>"
            for item in data['data']['items']:
            	out=out+"<tr><td>Video Title: </td><td>%s</td></tr>" % (item['title'])
            	out=out+"<tr><td>Video Category: </td><td>%s</tr>" % (item['category'])
            	out=out+"<tr><td>Video ID: </td><td>%s</tr>" % (item['id'])
            	if item.has_key('rating'):
            	    out=out+"<tr><td>Video Rating: </td><td>%f</tr>" % (item['rating'])
            	out=out+"<tr><td>Embed URL: </td><td><a href=\"%s\">link to Youtube</a></tr>" % (item['player']['default'])
            	out=out+"<tr><td>&nbsp;</td><td>&nbsp;</td></tr>"
            out=out+"</table>"
            yra=True
    except:
        yra=False
    if yra:
    	usercppicatext=("<div>%s</div>\n\t" % (out))
    else:
    	usercppicatext="<div>Youtube not found or error</div>\n\t";

  wtext = wtext + (_("user yout page header %(pseudonimas)s") % {'pseudonimas': pseudonimas}) + "<br>" + "<img src=\""+imagemaxurl+"\" border=\"0\" id=\"profile_pic\"><br>\n\n"+usercpplustext+(_("User yout page %(usercpuserid)s %(usercpcontent)s %(usercppseudonimas)s %(usercpurl)s %(usercppicatext)s")  % { 'usercpuserid': userid, 'usercpcontent': content,'usercppseudonimas': pseudonimas, 'usercpurl': usercpurl, 'usercppicatext': usercppicatext})
  wtext = wtext + (_("vartotojo puslapis %(usercppseudonimas)s %(userpageurl)s") % {'usercppseudonimas': pseudonimas, 'userpageurl': userpageurl})
  page = Page.loadnew("useryoutpage")
  page.content = wtext
  page_name2 = 'menu'+'-'+lang+'.'+fileext
  page2 = Page.load(page_name2)
  page3 = Page.loadnew("kalbos")
  textaps=''
  if len(aps)>0:
    textaps=aps+'.'
  text=''
  for name, value in kalbossort:
    text = text + (_kalbhtml % ('useryoutpage', textaps+name, userpageend, name, name))
  page3.content = text
  self.generate('view.html', lang, {
    'imgshar': False,
    'noedit': '1',
    'application_name': siteauth(),
    'kalbos': page3,
    'menu': page2,
    'page': page,
  })



class UserCommPage(BaseRequestHandler):
 def get(self,rparameters, pseudonim , pic_key):
#  self.response.out.write('<html><head><style>body {	text-align: center;	font: 11px arial, sans-serif;	color: #565656; } .clear { clear:both; } .comm-container { margin-bottom:20px;} .comm-name { font-size:10pt; float:left; width:20%; padding:5px; overflow:hidden; } .comm-text { float:left; line-height:17px; width:70%; padding:5px; padding-top:0px; overflow:hidden; } .font-small-gray { font-size:10pt !important; }</style></head><body>')
  param=urlparam(rparameters)
  ext=param['ext']
  lang=param['lang']
  aps=param['aps']
  kalb=param['kalb']
  lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
  _ = lang1.ugettext
  wtext=""
     
  userinfo2=userinfo(pic_key, True,lang,ext)
  imagemaxurl = userinfo2['imagemaxurl']
  userpageend = userinfo2['userpageend']
  userpicapagetext = userinfo2['userpicapagetext']
  usercpplustext = userinfo2['usercpplustext']
  usermailformtext = userinfo2['usermailformtext']
  usermailformpageurl = userinfo2['usermailformpageurl']
  useryoutpageurl = userinfo2['useryoutpageurl']
  userpicapageurl = userinfo2['userpicapageurl']
  usercommpageurl = userinfo2['usercommpageurl']
  usercpurl = userinfo2['usercpurl']
  pseudonimas = userinfo2['pseudonimas']
  userid = userinfo2['userid']
  content = userinfo2['content']
  youtname = userinfo2['youtname']
  vartot = userinfo2['vartot']
  rcomm = userinfo2['rcomm']
  lank = userinfo2['lank']
  userpageurl= userinfo2['userpageurl']
  
  if rcomm:
    yra=False
    wtext=""
    try:
      pg=self.request.get('pg')
      entitiesRx  = re.compile("[^0-9]")
      pg=entitiesRx.sub("", pg)
      if pg:
        pg = int(pg)
      else:
        pg=0

      try:
        query = db.GqlQuery("SELECT * FROM Commentsrec2 WHERE vartot = :1 ORDER BY date DESC", vartot)
#  query = db.GqlQuery("SELECT * FROM Commentsrec WHERE rodyti = :1, author = :2 ORDER BY date DESC", '1',users.GetCurrentUser())
        greetings = query.fetch(10,pg*10)
        co=query.count()
      except:
        klaida=True
        co=0
        greetings = []

      i=0
      ii=0
      bbb=""
      while i<=co:
        i=i+10
        if ii == pg:
          bbb=bbb+' '+str(ii)
        else:
          bbb=bbb+' '+"<a href=\"/"+cmspath2+"-usercommpage-"+lang+'.'+fileext+'/'+pseudonimas+'/'+userid+"?pg="+ str(ii) +"\">"+ str(ii) +"</a>"
        ii=ii+1
#      page2 = Page.load("atsi-"+lang+'.'+fileext)
     
      wtext=wtext+"<div><hr width=\"70%\"></div>\n<div><div style=\"text-align: center;\">"+bbb+"</div>\n\n"
      for greeting in greetings:
        wijun = ""
        wdel = ""
        if greeting.rodyti or (users.GetCurrentUser() and users.get_current_user() == greeting.author) or (users.GetCurrentUser() and users.get_current_user() == vartot.lankytojas) or users.is_current_user_admin():
            if users.is_current_user_admin():
                wdel = _("Comments delete %(commswiturl)s %(commkey)s") % {'commswiturl': '/commswit', 'commkey': greeting.key()}
            if (users.GetCurrentUser() and users.get_current_user() == vartot.lankytojas) or (users.GetCurrentUser() and users.get_current_user() == greeting.author) or users.is_current_user_admin():
                if not greeting.rodyti:
                    wijun = _("Comments show %(commswiturl)s %(commkey)s") % {'commswiturl': '/commswit', 'commkey': greeting.key()}
                else:
                    wijun = _("Comments hidden %(commswiturl)s %(commkey)s") % {'commswiturl': '/commswit', 'commkey': greeting.key()}

            user3 = greeting.author
            pseudonimas3 = "Anonymous"
            userid3 = '0'
            try:
                  buvesapp = db.GqlQuery("SELECT * FROM Vartotojai WHERE lankytojas = :1", user3)
                  for app in buvesapp:
                      userid3 = app.userid
                      pseudonimas3 = app.pseudonimas
            except:
                  klaida=True
            
            imagemaxurl2 = ("/%s-userimagemin/%s/%s" % (cmspath2,pseudonimas3, userid3))
            userpageurl = ("%s/%s-userpage-%s.%s/%s/%s" % (urlhost2(), cmspath2,lang, fileext, pseudonimas3, userid3))
            wtext = wtext + "\n<div class=\"comm-container\">"
            wtext = wtext + "<div class=\"comm-name\">"+("<a href=\"%s\"><img src=\"%s\" alt=\"\" border=\"0\"></img></a>" % (userpageurl,imagemaxurl2))+(' <strong>%s</strong>' % pseudonimas3) +", "+('<div class="font-small-gray">%s</div>' % greeting.date.strftime("%a, %d %b %Y %H:%M:%S"))
            if greeting.avatar:
            	if greeting.avatarmax:
            		wtext = wtext + ('<div class="font-small-gray"><a href="/commimg?img_id=%s&size=yes"><img src="/commimg?img_id=%s" alt=""></img></a></div>' % (greeting.key(),greeting.key()))
            	else:
            		wtext = wtext + ('<div class="font-small-gray"><img src="/commimg?img_id=%s" alt=""></img></div>' % greeting.key())
            wtext = wtext + "</div>"
            wtext = wtext + "\n"+('<div class="comm-text"><div>%s</div>' % greeting.content)+"</div>\n"
            wtext = wtext + "</div><div class=\"clear\"><!-- --></div>\n"
            wtext = wtext + "\n<div>"+wijun+"  " +wdel+"</div>\n\n"
            wtext = wtext + "<div>&nbsp;</div>\n"
      codekey=codekey2()
      if users.GetCurrentUser():
        wtext = wtext + "\n</div>\n<div>&nbsp;</div>\n"+(_("user Comments form %(commsendurl)s %(commcodekey)s")  % {'commsendurl': '/'+cmspath2+'-usercommsubmit-'+lang+'.'+fileext+'/'+pseudonimas +'/'+userid, 'commcodekey': codekey})
      else:
        wtext = wtext + "\n</div>\n<div>&nbsp;</div>\n<div>" + (_("Sign in or register %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}) + "</div>"
      yra=True
    except:
      yra=False
    if yra:
      usercppicatext=("<div>%s</div>\n\t" % (wtext))
    else:
      usercppicatext="<div>comments db error</div>\n\t";

  wtext = (_("user comm page header %(pseudonimas)s") % {'pseudonimas': pseudonimas}) + "<br>" + "<img src=\""+imagemaxurl+"\" border=\"0\" id=\"profile_pic\"><br>\n\n"+usercpplustext+(_("User comm page %(usercpuserid)s %(usercpcontent)s %(usercppseudonimas)s %(usercpurl)s %(usercppicatext)s")  % { 'usercpuserid': userid, 'usercpcontent': content,'usercppseudonimas': pseudonimas, 'usercpurl': usercpurl, 'usercppicatext': usercppicatext})
  wtext = wtext + (_("vartotojo puslapis %(usercppseudonimas)s %(userpageurl)s") % {'usercppseudonimas': pseudonimas, 'userpageurl': userpageurl})
  page = Page.loadnew("usercommpage")
  page.content = wtext
  page_name2 = 'menu'+'-'+lang+'.'+fileext
  page2 = Page.load(page_name2)
  page3 = Page.loadnew("kalbos")
  textaps=''
  if len(aps)>0:
    textaps=aps+'.'
  text=''
  for name, value in kalbossort:
    text = text + (_kalbhtml % ('usercommpage', textaps+name, userpageend, name, name))
  page3.content = text
  self.generate('view.html', lang, {
    'imgshar': False,
    'noedit': '1',
    'application_name': siteauth(),
    'kalbos': page3,
    'menu': page2,
    'page': page,
  })

class UserCommSubmit(webapp.RequestHandler):
  def post(self, rparameters, pseudonim , pic_key):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    buvoapp = False
    rpica = False
    rplus = True
    rcomm = False
    userid = "0"
    content = ""
    lank = ""
    pseudonimas = "Anonymous"
    user = users.get_current_user()
    thubnail=""
    imagemaxurl = avatarmaxurl2
    userpicapageurl = ("%s/%s-userpicapage-%s.%s/%s/%s" % (urlhost2(), cmspath2,lang, fileext, pseudonim, pic_key))
    usercppicaurl = ("/%s-userpicacontrol-%s.%s" % (cmspath2,lang,fileext))
    usercppicasubmiturl = ("/%s-userpicasubmit-%s.%s" % (cmspath2,lang,fileext))
    usercppicatext = ""
    vartkey=""
    try:
          buvesapp = db.GqlQuery("SELECT * FROM Vartotojai WHERE userid = :1", pic_key)
          for app in buvesapp:
              rcomm = app.commrodyti
              rpica = app.picarodyti
              buvoapp = app.rodyti
              userid = app.userid
              content = render_bbcode(str(app.content))
              pseudonimas = str(app.pseudonimas)
              lank=app.lankytojas
              vartkey=app.key()
          vartot = db.get(vartkey)
          thubnail=getphoto(lank.email())
    except:
          klaida=True
    connt=""
    try:
        codeimg = db.get(self.request.get("scodeid"))
    except:
        prn="Error"
    if codeimg and codeimg.code == self.request.get("scode") and rcomm:
        greeting = Commentsrec2()
        greeting.vartot = vartot
        greeting.rodyti = True
        greeting.userid = userid
        greeting.ipadresas = os.environ['REMOTE_ADDR']
#	greeting.laikas = datetime.datetime.now()
        if users.get_current_user():
        	greeting.author = users.get_current_user()
        connt = cgi.escape(self.request.get("content"))
        connt = render_bbcode(connt)
        connt = connt[0:400]
        greeting.content = connt
#    priesduom = self.request.get("img")
        greeting.rname = pseudonimas
        if self.request.get("img"):
          avatarmax = images.resize(self.request.get("img"), width=600, height=400, output_encoding=images.PNG)
          greeting.avatarmax = db.Blob(avatarmax)
          avatar = images.resize(self.request.get("img"), width=96, height=96, output_encoding=images.PNG)
          greeting.avatar = db.Blob(avatar)
        greeting.put()
        to_addr = _mailrcptto
        user = users.get_current_user()
        if user:
            uname=user.nickname()
            umail=users.get_current_user().email()
        else:
            uname=""
            umail=""
        message = mail.EmailMessage()
        message.subject = os.environ['HTTP_HOST'] + " - comments"
#        message.subject = "www"
        message.sender = _mailsender
        message.to = to_addr
        q_message =  ("\n%s: %s \n%s \n%s \n" % ('Page', str(self.request.uri),str(textinfo()),str(textloc())))
 
        message.body = (_("Comments mail message %(communame)s %(commumail)s %(commrealname)s %(commmessage)s") % {'communame': uname,'commumail': umail,'commrealname': greeting.rname,'commmessage': greeting.content}) + q_message
        message.send()

    self.redirect('/'+cmspath2+'-usercommpage-'+lang+'.'+fileext+'/'+pseudonimas+'/'+userid )

class UserPicaPage(BaseRequestHandler):
 def get(self,rparameters, pseudonim , pic_key):
#  self.response.out.write('<html><head><style>body {	text-align: center;	font: 11px arial, sans-serif;	color: #565656; } .clear { clear:both; } .comm-container { margin-bottom:20px;} .comm-name { font-size:10pt; float:left; width:20%; padding:5px; overflow:hidden; } .comm-text { float:left; line-height:17px; width:70%; padding:5px; padding-top:0px; overflow:hidden; } .font-small-gray { font-size:10pt !important; }</style></head><body>')
  param=urlparam(rparameters)
  ext=param['ext']
  lang=param['lang']
  aps=param['aps']
  kalb=param['kalb']
  lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
  _ = lang1.ugettext
  wtext=""
     
  codekey=codekey2()
  userinfo2=userinfo(pic_key, True,lang,ext)
  imagemaxurl = userinfo2['imagemaxurl']
  userpageend = userinfo2['userpageend']
  userpicapagetext = userinfo2['userpicapagetext']
  usercpplustext = userinfo2['usercpplustext']
  usermailformtext = userinfo2['usermailformtext']
  usermailformpageurl = userinfo2['usermailformpageurl']
  useryoutpageurl = userinfo2['useryoutpageurl']
  userpicapageurl = userinfo2['userpicapageurl']
  usercommpageurl = userinfo2['usercommpageurl']
  usercpurl = userinfo2['usercpurl']
  pseudonimas = userinfo2['pseudonimas']
  userid = userinfo2['userid']
  content = userinfo2['content']
  youtname = userinfo2['youtname']
  vartot = userinfo2['vartot']
  rcomm = userinfo2['rcomm']
  rpica = userinfo2['rpica']
  lank = userinfo2['lank']
  userpageurl= userinfo2['userpageurl']
  if rpica:
    albumbuvo = {}
    buves_album = db.GqlQuery("SELECT * FROM PicaAlbumOn WHERE userid = :1", userid)
    for albumb in buves_album:
        albumname=albumb.albumname
        albumbuvo[albumname]=albumb.rodyti
    user2 = lank.email()
    album = self.request.get("album")
    yra=False
    out=""
    try:
        if not self.request.get("album"):
            f = urllib.urlopen("http://picasaweb.google.com/data/feed/api/user/%s?kind=album" % user2)
            list = Picasa().albums(f.read())
#        self.response.out.write("<xmp>")
#        self.response.out.write(list)
#        self.response.out.write("</xmp>")
            out=out+"<table>"
            for name in list.keys():
                album = list[name]
                if albumbuvo.has_key(name) and albumbuvo[name]:  #albumname in albumbuvo:
                    out=out+("<tr><td><img src=\"%s\" border=\"0\" alt=\"%s\"></td><td><a href=\"%s?album=%s\">%s</a></td><td>%s</td></tr>" % (album.thumbnail,album.title,userpicapageurl,name,name,album.title))
#            pass
            out=out+"<tr><td colspan=\"3\"></td></tr></table>"
#        pass
            yra=True
        else:
            f = urllib.urlopen("http://picasaweb.google.com/data/feed/api/user/%s/album/%s?kind=photo" % (user2,album))
            list = Picasa().photos(f.read())
            out=out+"<table>"
            for photo in list:
                out=out+("<tr><td><img src=\"%s\" border=\"0\" alt=\"%s\"></td><td><a href=\"%s\">%s</a></td><td>%s</td></tr>" % (photo.thumbnail,photo.title,photo.webpage,photo.title, photo.getDatetime() ))
#            pass
            out=out+"<tr><td colspan=\"3\"></td></tr></table>"
#        self.response.out.write("Please login");
            yra=True
    except:
        yra=False
    if yra:
    	usercppicatext=("<div>%s</div>\n\t" % (out))
    else:
    	usercppicatext="<div>Picasa info not found or error</div>\n\t";

  wtext = wtext + (_("user pica page header %(pseudonimas)s") % {'pseudonimas': pseudonimas}) + "<br>" + "<img src=\""+imagemaxurl+"\" border=\"0\" id=\"profile_pic\"><br>\n\n"+usercpplustext+(_("User pica page %(usercpuserid)s %(usercpcontent)s %(usercppseudonimas)s %(usercpurl)s %(usercppicatext)s")  % { 'usercpuserid': userid, 'usercpcontent': content,'usercppseudonimas': pseudonimas, 'usercpurl': usercpurl, 'usercppicatext': usercppicatext})
  wtext = wtext + (_("vartotojo puslapis %(usercppseudonimas)s %(userpageurl)s") % {'usercppseudonimas': pseudonimas, 'userpageurl': userpageurl})
  page = Page.loadnew("userpicapage")
  page.content = wtext
  page_name2 = 'menu'+'-'+lang+'.'+fileext
  page2 = Page.load(page_name2)
  page3 = Page.loadnew("kalbos")
  textaps=''
  if len(aps)>0:
    textaps=aps+'.'
  text=''
  for name, value in kalbossort:
    text = text + (_kalbhtml % ('userpicapage', textaps+name, userpageend, name, name))
  page3.content = text
  self.generate('view.html', lang, {
    'imgshar': False,
    'noedit': '1',
    'application_name': siteauth(),
    'kalbos': page3,
    'menu': page2,
    'page': page,
  })


class UserPicaControl(BaseRequestHandler):
 def get(self,rparameters):
#  self.response.out.write('<html><head><style>body {	text-align: center;	font: 11px arial, sans-serif;	color: #565656; } .clear { clear:both; } .comm-container { margin-bottom:20px;} .comm-name { font-size:10pt; float:left; width:20%; padding:5px; overflow:hidden; } .comm-text { float:left; line-height:17px; width:70%; padding:5px; padding-top:0px; overflow:hidden; } .font-small-gray { font-size:10pt !important; }</style></head><body>')
  param=urlparam(rparameters)
  ext=param['ext']
  lang=param['lang']
  aps=param['aps']
  kalb=param['kalb']
  lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
  _ = lang1.ugettext
  wtext=""
     
  codekey=codekey2()
  user = users.get_current_user()
  userinfo2=userinfo(user,False,lang,ext)
  imagemaxurl = userinfo2['imagemaxurl']
  userpageend = userinfo2['userpageend']
  userpicapagetext = userinfo2['userpicapagetext']
  usercpplustext = userinfo2['usercpplustext']
  usermailformtext = userinfo2['usermailformtext']
  usermailformpageurl = userinfo2['usermailformpageurl']
  useryoutpageurl = userinfo2['useryoutpageurl']
  userpicapageurl = userinfo2['userpicapageurl']
  usercommpageurl = userinfo2['usercommpageurl']
  usercpurl = userinfo2['usercpurl']
  pseudonimas = userinfo2['pseudonimas']
  userid = userinfo2['userid']
  content = userinfo2['content']
  youtname = userinfo2['youtname']
  vartot = userinfo2['vartot']
  rcomm = userinfo2['rcomm']
  rpica = userinfo2['rpica']
  lank = userinfo2['lank']
  userpageurl= userinfo2['userpageurl']
  
  
  if rpica:
    albumbuvo = {}
    buves_album = db.GqlQuery("SELECT * FROM PicaAlbumOn WHERE lankytojas = :1", user)
    for albumb in buves_album:
       albumname=albumb.albumname
       albumbuvo[albumname]=albumb.rodyti
    user2 = lank.email()
    album = self.request.get("album")
    yra=False
    out=""
    namelist =""
    errtext =""
    buvoappcheck="" 
    try:
        if not self.request.get("album"):
            f = urllib.urlopen("http://picasaweb.google.com/data/feed/api/user/%s?kind=album" % user2)
            list = Picasa().albums(f.read())
            out=out+"<table><form method=\"POST\" action=\""+usercppicasubmiturl+"\">"
            for name in list.keys():
                album = list[name]
                if albumbuvo.has_key(name) and albumbuvo[name]:  #albumname in albumbuvo:
                    buvoappcheck="checked=\"yes\"" 
                out=out+("<tr><td><img src=\"%s\" border=\"0\" alt=\"%s\"></td><td><a href=\"%s?album=%s\">%s</a></td><td>%s</td><td><input type=\"checkbox\" name=\"photoalbum\" value=\"%s\" %s></td></tr>" % (album.thumbnail,album.title,usercppicaurl,name,name,album.title,name,buvoappcheck))
                namelist = namelist + "||" + str(base64.urlsafe_b64encode(str(name)))
            out=out+"<tr><td colspan=\"4\"><input type=\"hidden\" name=\"namelist\" value=\""+str(namelist)+"\" ><input type=\"submit\"></td></tr></form></table>"
            yra=True
        else:
            f = urllib.urlopen("http://picasaweb.google.com/data/feed/api/user/%s/album/%s?kind=photo" % (user2,album))
            list = Picasa().photos(f.read())
            out=out+"<table>"
            for photo in list:
                out=out+("<tr><td><img src=\"%s\" border=\"0\" alt=\"%s\"></td><td><a href=\"%s\">%s</a></td><td>%s</td></tr>" % (photo.thumbnail,photo.title,photo.webpage,photo.title, photo.getDatetime() ))
            out=out+"<tr><td colspan=\"3\"></td></tr></table>"
            yra=True
    except:
        errtext =  cgi.escape(str(sys.exc_info()[0]))
        yra=False
    if yra:
    	usercppicatext=("<div>%s</div>\n\t" % (out))
    else:
    	usercppicatext="<div>Picasa info not found or error " + errtext +"</div>\n\t";

  wtext = wtext + _("user pica control panel header") + "<br>" + "<img src=\""+imagemaxurl+"\" border=\"0\" id=\"profile_pic\"><br>\n\n"+usercpplustext+(_("User pica page %(usercpuserid)s %(usercpcontent)s %(usercppseudonimas)s %(usercpurl)s %(usercppicatext)s")  % { 'usercpuserid': userid, 'usercpcontent': content,'usercppseudonimas': pseudonimas, 'usercpurl': usercpurl, 'usercppicatext': usercppicatext})
  page = Page.loadnew("userpage")
  page.content = wtext
  page_name2 = 'menu'+'-'+lang+'.'+fileext
  page2 = Page.load(page_name2)
  page3 = Page.loadnew("kalbos")
  textaps=''
  if len(aps)>0:
    textaps=aps+'.'
  text=''
  for name, value in kalbossort:
    text = text + (_kalbhtml % ('userpage', textaps+name, userpageend, name, name))
  page3.content = text
  self.generate('view.html', lang, {
    'imgshar': False,
    'noedit': '1',
    'application_name': siteauth(),
    'kalbos': page3,
    'menu': page2,
    'page': page,
  })

class UserControlSend(webapp.RequestHandler):
  def post(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    cont=""
    try:
        codeimg = db.get(self.request.get("scodeid"))
    except:
        prn="Error"
    if codeimg and codeimg.code == self.request.get("scode"):
        user = users.get_current_user()
        klaida=False
        try:
          buves_vart = db.GqlQuery("SELECT * FROM Vartotojai WHERE lankytojas = :1", user)
          for vart in buves_vart:
            vart.ipadresas = os.environ['REMOTE_ADDR']
            vart.narsykle = os.environ['HTTP_USER_AGENT']
#	greeting.laikas = datetime.datetime.now()
            if users.get_current_user():
              vart.lankytojas = users.get_current_user()
              cont = self.request.get("content")
              cont = cgi.escape(cont)
              vart.content = (cont)[0:2000]
#    priesduom = self.request.get("img")
              vart.pseudonimas = "Anonymous"
            if self.request.get("img"):
              avatarmin = images.resize(self.request.get("img"), width=50, height=50, output_encoding=images.PNG)
              vart.avatarmin = db.Blob(avatarmin)
              avatarmax = images.resize(self.request.get("img"), width=200, height=200, output_encoding=images.PNG)
              vart.avatarmax = db.Blob(avatarmax)
              vart.rodyti = True
            if self.request.get("rname"):
              entitiesRx  = re.compile("[^0-9a-zA-Z]")
              rnametext = cgi.escape(self.request.get("rname"))
              rnametext = entitiesRx.sub("", rnametext)
              vart.pseudonimas = rnametext[0:30]
            if self.request.get("youtname"):
              entitiesRx  = re.compile("[^0-9a-zA-Z]")
              ynametext = cgi.escape(self.request.get("youtname"))
              ynametext = entitiesRx.sub("", ynametext)
              vart.youtname = ynametext[0:50]
            if self.request.get("globphoto"):
              vart.rodyti = False
            if self.request.get("picasaen"):
              vart.picarodyti = True
            else:
              vart.picarodyti = False
            if self.request.get("plusen"):
              vart.plusrodyti = True
            else:
              vart.plusrodyti = False
            if self.request.get("commen"):
              vart.commrodyti = True
            else:
              vart.commrodyti = False
            vart.put()
        except:
          errtext =  cgi.escape(str(sys.exc_info()[0]))
          klaida=True
        to_addr = _mailrcptto
        user = users.get_current_user()
        if user:
            uname=user.nickname()
            umail=users.get_current_user().email()
        else:
            uname=""
            umail=""
        message = mail.EmailMessage()
        message.subject = os.environ['HTTP_HOST'] + " - user page edit"
#        message.subject = "www"
        message.sender = _mailsender
        message.to = to_addr
        q_message =  ("\n%s: %s \n%s \n%s \n" % ('Page', str(self.request.uri),str(textinfo()),str(textloc())))
        message.body = (_("Comments mail message %(communame)s %(commumail)s %(commrealname)s %(commmessage)s") % {'communame': uname,'commumail': umail,'commrealname': vart.pseudonimas,'commmessage': vart.content})  + q_message
        message.send()
    if klaida:
        self.response.out.write("""%s <br />\n""" % (errtext))
    else:
        self.redirect('/'+cmspath2+'-usercontrolpanel-'+lang+'.'+fileext)

class UserPicaControlSend(webapp.RequestHandler):
  def post(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext

    user = users.get_current_user()
    now = datetime.datetime.now()
    buvo = False
    if user:
#      try:
      if user:
       photoal=[]
       namelist2=[]
       albumbuvo = {}
       albumname = ""
#       form = cgi.FieldStorage()
#       item = form.getvalue("photoalbum")
#       if form["namelist"].value:
#         namelist=form["namelist"].value
#         namelist2=namelist.split("||")
#       if isinstance(item, list):
#         for item in form.getlist("photoalbum"):
#           photoal.append(item)
#       else:
#         photoa = form.getfirst("photoalbum", "")
#         photoal.append(photoa) 
       namelist=self.request.POST['namelist']
       namelist2=namelist.split("||")
       photoal=self.request.POST.getall('photoalbum')
       for albumn2 in namelist2: 
         if len(albumn2)>0:
          albumname = base64.urlsafe_b64decode(str(albumn2))
          albumbuvo[albumname]=False
#          self.response.out.write("namelist:" +albumname+ "<br>\n")
       for albumn2 in photoal: 
         albumbuvo[albumn2]=True
#         self.response.out.write("photoal:" +albumn2+ "<br>\n")
       albumbuvo2=albumbuvo
       buves_album = db.GqlQuery("SELECT * FROM PicaAlbumOn WHERE lankytojas = :1", user)
       for albumb in buves_album:
          albumb.ipadresas = os.environ['REMOTE_ADDR']
          albumb.narsykle = os.environ['HTTP_USER_AGENT']
          albumb.laikas = datetime.datetime.now()
          albumb.userid = user.user_id()
          if users.is_current_user_admin():
            albumb.administratorius = True
          else:
            albumb.administratorius = False
          albumname=str(albumb.albumname)
          if albumbuvo.has_key(albumname):  #albumname in albumbuvo:
            albumb.rodyti = albumbuvo[albumname]
#            self.response.out.write("buvo:" +albumname+" "+str(albumbuvo[albumname])+ "<br>\n")
            albumbuvo2.pop(albumname)
          albumb.put()
       for albumn in albumbuvo2.keys():
         album = PicaAlbumOn(lankytojas=user)
         album.albumname=albumn
         album.ipadresas = os.environ['REMOTE_ADDR']
         album.narsykle = os.environ['HTTP_USER_AGENT']
         album.laikas = datetime.datetime.now()
         album.userid = user.user_id()
         if users.is_current_user_admin():
           album.administratorius = True
         else:
           album.administratorius = False
         album.rodyti = albumbuvo2[albumn]
#         self.response.out.write("naujas:" +albumn+" "+str(albumbuvo2[albumn])+ "<br>\n")
         album.put()
         buvo = True
#      except:
#        klaida=True

       to_addr = _mailrcptto
       user = users.get_current_user()
       if user:
         uname=user.nickname()
         umail=users.get_current_user().email()
       else:
         uname=""
         umail=""
       message = mail.EmailMessage()
       message.subject = os.environ['HTTP_HOST'] + " - add albums"
#        message.subject = "www"
       message.sender = _mailsender
       message.to = to_addr
       q_message = ("\n%s: %s \n%s \n%s \n" % ('Page', str(self.request.uri),str(textinfo()),str(textloc())))
       message.body = (_("Comments mail message %(communame)s %(commumail)s %(commrealname)s %(commmessage)s") % {'communame': uname,'commumail': umail,'commrealname': '','commmessage': ''}) + q_message
       message.send()

    self.redirect('/'+cmspath2+'-userpicacontrol-'+lang+'.'+fileext)

class UserMailFormPage(BaseRequestHandler):
  def get(self, rparameters, pseudonim , pic_key):

    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    codekey=codekey2()

    userinfo2=userinfo(pic_key,True,lang,ext)
    imagemaxurl = userinfo2['imagemaxurl']
    userpageend = userinfo2['userpageend']
    userpicapagetext = userinfo2['userpicapagetext']
    usercpplustext = userinfo2['usercpplustext']
    usermailformtext = userinfo2['usermailformtext']
    usermailformpageurl = userinfo2['usermailformpageurl']
    useryoutpageurl = userinfo2['useryoutpageurl']
    userpicapageurl = userinfo2['userpicapageurl']
    usercommpageurl = userinfo2['usercommpageurl']
    usercpurl = userinfo2['usercpurl']
    pseudonimas = userinfo2['pseudonimas']
    userid = userinfo2['userid']
    content = userinfo2['content']
    youtname = userinfo2['youtname']
    vartot = userinfo2['vartot']
    rcomm = userinfo2['rcomm']
    rpica = userinfo2['rpica']
    lank = userinfo2['lank']
    userpageurl= userinfo2['userpageurl']
    
    usersendmailurl = ("/%s-usersendmail-%s.%s/%s/%s" % (cmspath2,lang, fileext, pseudonimas, userid))
    userpagetext = (_("vartotojo puslapis %(usercppseudonimas)s %(userpageurl)s") % {'usercppseudonimas': pseudonimas, 'userpageurl': userpageurl})
    if hasattr(lank, 'email'):
      plusurl=getplius(lank.email())
    else:
      plusurl=None
    wtext = (_("user mailform header %(pseudonimas)s") % {'pseudonimas': pseudonimas}) + "<br>" + "<img src=\""+imagemaxurl+"\"  border=\"0\" id=\"profile_pic\"><br>\n\n"+usercpplustext+(_("User mailform %(usercpuserid)s %(usercpcontent)s %(usercppseudonimas)s %(usercpurl)s %(userpicapagetext)s")  % { 'usercpuserid': userid, 'usercpcontent': content,'usercppseudonimas': pseudonimas, 'usercpurl': usercpurl, 'userpicapagetext': userpagetext})


  
    page = Page.loadnew("usermailformpage")
    user = users.get_current_user()
    greeting = ''
    if user and hasattr(lank, 'email'):
      greeting = _("User Mail form %(mailsendurl)s %(mailcodekey)s") % {'mailsendurl': usersendmailurl,'mailcodekey': codekey}
    elif not hasattr(lank, 'email'):
      greeting = "\t\n<div>&nbsp;</div>\t\n<div>User not Found</div>"
    else:
      greeting = "\t\n<div>&nbsp;</div>\t\n<div>" + (_("Sign in or register %(userloginurl)s") % {'userloginurl': users.create_login_url(self.request.uri)}) + "</div>"


    page.content = u""+ wtext +greeting+""
    page_name2 = 'menu'+'-'+lang+'.'+fileext
    page2 = Page.load(page_name2)

	


    page3 = Page.loadnew("kalbos")
    textaps=''
    if len(aps)>0:
        textaps=aps+'.'
    text=''
    for name, value in kalbossort:
        text = text + (_kalbhtml % ('usermailformpage', textaps+name, userpageend, name, name))
    page3.content = text
    self.generate('view.html', lang, {
      'imgshar': False,
      'noedit': '1',
      'application_name': siteauth(),
      'kalbos': page3,
      'menu': page2,
      'page': page,
    })

class UserMailSend(BaseRequestHandler):
#    @login_required
    def post(self, rparameters, pseudonim , pic_key):
        parts = rparameters.split(".")
        param=urlparam(rparameters)
        ext=param['ext']
        lang=param['lang']
        aps=param['aps']
        kalb=param['kalb']
        lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
        _ = lang1.ugettext
        try:
            codeimg = db.get(self.request.get("scodeid"))
        except:
            prn="Error"
#        codeimg = db.get(self.request.get("scodeid"))
        if codeimg and codeimg.code == self.request.get("scode") and users.GetCurrentUser():

          rpica = False
          rplus = True
          buvoapp = False
          userid = "0"
          content = ""
          lank = UserNone(email=None, federated_identity=None)
          pseudonimas = "Anonymous"
          user = users.get_current_user()
          thubnail=""
          imagemaxurl = avatarmaxurl2
          userpicapagetext=""
          try:
              buvesapp = db.GqlQuery("SELECT * FROM Vartotojai WHERE userid = :1", pic_key)
              for app in buvesapp:
                  rpica = app.picarodyti
                  buvoapp = app.rodyti
                  userid = app.userid
                  content = str(app.content)
                  pseudonimas = str(app.pseudonimas)
                  lank=app.lankytojas
              thubnail=getphoto(lank.email())

          except:
              klaida=True

          userpageurl = ("%s/%s-userpage-%s.%s/%s/%s" % (urlhost2(), cmspath2,lang, fileext, pseudonimas, userid))
          codeimg.delete()
          x_zmail = lank.email()
          x_subject = self.request.get("zsubject")
          x_realname = self.request.get("zrealname")
          x_message = self.request.get("zmessage")
          to_addr = _mailrcptto
          user = users.get_current_user()
          if user:
              uname=user.nickname()
              umail=users.get_current_user().email()
          else:
              uname=""
              umail=""
          if not mail.is_email_valid(to_addr):
                # Return an error message...
              pass
          message = mail.EmailMessage()
          message.subject = x_subject.encode("utf-8")
#        message.subject = "www"
          message.sender = users.get_current_user().email()
          if lank.email():
              message.to = lank.email()
          else:
              message.to = to_addr
#            q_uname = uname.encode("utf-8")
#            q_umail = umail.encode("utf-8")
#            q_zmail = x_zmail.encode("utf-8")
#            q_realname = x_realname.encode("utf-8")
#            q_message = x_message.encode("utf-8")

          q_uname = ''
          q_umail = ''
          q_zmail = ''
          q_realname = ''
          q_message = ''
          q_uname = uname
          q_umail = umail
          q_zmail = x_zmail
          q_realname = x_realname
          q_message = x_message + ("\n%s: %s \n%s \n%s \n" % ('Page', str(self.request.uri),str(textinfo()),str(textloc())))

          message.body = (_("Mail message %(mailuname)s %(mailumail)s %(mailrealname)s %(mailzmail)s %(mailmessage)s") % {'mailuname': q_uname, 'mailumail': q_umail, 'mailrealname': q_realname, 'mailzmail': q_zmail, 'mailmessage': q_message})
          message.body = message.body + ("\n\nMail page: %s" % (userpageurl))
          message.send()
          ptext=_("Mail send OK")
        else:
          ptext=_("Mail send Error")
        page = Page.loadnew("sendmail")
        page.content = ptext
        page_name2 = 'menu'+'-'+lang+'.'+fileext
        page2 = Page.load(page_name2)
        self.generate('view.html', lang, {
          'imgshar': False,
          'noedit': '1',
          'application_name': siteauth(),
          'menu': page2,
          'page': page,
        })



class Comments(BaseRequestHandler):
 def get(self,rparameters):
#  self.response.out.write('<html><head><style>body {	text-align: center;	font: 11px arial, sans-serif;	color: #565656; } .clear { clear:both; } .comm-container { margin-bottom:20px;} .comm-name { font-size:10pt; float:left; width:20%; padding:5px; overflow:hidden; } .comm-text { float:left; line-height:17px; width:70%; padding:5px; padding-top:0px; overflow:hidden; } .font-small-gray { font-size:10pt !important; }</style></head><body>')
  param=urlparam(rparameters)
  ext=param['ext']
  lang=param['lang']
  aps=param['aps']
  kalb=param['kalb']
  lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
  _ = lang1.ugettext
  wtext=""
  pg=self.request.get('pg')
  entitiesRx  = re.compile("[^0-9]")
  pg=entitiesRx.sub("", pg)
  if pg:
    pg = int(pg)
  else:
    pg=0

  try:
    query = db.GqlQuery("SELECT * FROM Commentsrec ORDER BY date DESC")
#  query = db.GqlQuery("SELECT * FROM Commentsrec WHERE rodyti = :1, author = :2 ORDER BY date DESC", '1',users.GetCurrentUser())
    greetings = query.fetch(10,pg*10)
    co=query.count()
  except:
    klaida=True
    co=0
    greetings = []

  i=0
  ii=0
  bbb=""
  while i<=co:
    i=i+10
    if ii == pg:
      bbb=bbb+' '+str(ii)
    else:
      bbb=bbb+' '+"<a href=\"/"+cmspath2+"-comments-"+lang+'.'+fileext+"?pg="+ str(ii) +"\">"+ str(ii) +"</a>"
    ii=ii+1
  page2 = Page.load("atsi-"+lang+'.'+fileext)
     
  wtext=wtext+page2.content+"\n<div><div style=\"text-align: center;\">"+bbb+"</div>\n\n"
  for greeting in greetings:
    wijun = ""
    wdel = ""
    if greeting.rodyti or (users.GetCurrentUser() and users.get_current_user() == greeting.author) or users.is_current_user_admin():
        if users.is_current_user_admin():
            wdel = _("Comments delete %(commswiturl)s %(commkey)s") % {'commswiturl': '/commswit', 'commkey': greeting.key()}
        if (users.GetCurrentUser() and users.get_current_user() == greeting.author) or users.is_current_user_admin():
            if not greeting.rodyti:
                wijun = _("Comments show %(commswiturl)s %(commkey)s") % {'commswiturl': '/commswit', 'commkey': greeting.key()}
            else:
                wijun = _("Comments hidden %(commswiturl)s %(commkey)s") % {'commswiturl': '/commswit', 'commkey': greeting.key()}
        wtext = wtext + "\n<div class=\"comm-container\">"
        wtext = wtext + "<div class=\"comm-name\">"+('<strong>%s</strong>' % greeting.rname) +", "+('<div class="font-small-gray">%s</div>' % greeting.date.strftime("%a, %d %b %Y %H:%M:%S"))
        if greeting.avatar:
        	if greeting.avatarmax:
        		wtext = wtext + ('<div class="font-small-gray"><a href="/commimg?img_id=%s&size=yes"><img src="/commimg?img_id=%s" alt=""></img></a></div>' % (greeting.key(),greeting.key()))
        	else:
        		wtext = wtext + ('<div class="font-small-gray"><img src="/commimg?img_id=%s" alt=""></img></div>' % greeting.key())
        wtext = wtext + "</div>"
        wtext = wtext + "\n"+('<div class="comm-text"><div>%s</div>' % greeting.content)+"</div>\n"
        wtext = wtext + "</div><div class=\"clear\"><!-- --></div>\n"
        wtext = wtext + "\n<div>"+wijun+"  " +wdel+"</div>\n\n"
  codekey=codekey2()
  wtext = wtext + "\n</div>\n"+(_("Comments form %(commsendurl)s %(commcodekey)s")  % {'commsendurl': '/'+cmspath2+'-commsubmit-'+lang+'.'+fileext, 'commcodekey': codekey})
  page = Page.loadnew("comments")
  page.content = wtext
  page_name2 = 'menu'+'-'+lang+'.'+fileext
  page2 = Page.load(page_name2)
  page3 = Page.loadnew("kalbos")
  textaps=''
  if len(aps)>0:
    textaps=aps+'.'
  text=''
  for name, value in kalbossort:
    text = text + (_kalbhtml % ('comments', textaps+name, ext, name, name))
  page3.content = text
  self.generate('view.html', lang, {
    'imgshar': False,
    'noedit': '1',
    'application_name': siteauth(),
    'kalbos': page3,
    'menu': page2,
    'page': page,
  })
class AvatarErr(object):
  from bindata import PictureErr
  avatar=PictureErr.thumbnail_data
  avatarmax=PictureErr.data

class CommentsImage(webapp.RequestHandler):
  def get(self):
    try:
      greeting = db.get(self.request.get("img_id"))
      atype = "png"
    except:
      greeting = AvatarErr()
      atype = "jpeg"
    if self.request.get("size"):
      if hasattr(greeting, 'avatarmax'):
#      if greeting.avatarmax:
        self.response.headers['Content-Type'] = "image/%s" % atype
        self.response.out.write(greeting.avatarmax)
      else:
        self.response.out.write("No image")
    else:
      if hasattr(greeting, 'avatar'):
#      if greeting.avatar:
        self.response.headers['Content-Type'] = "image/%s" % atype
        self.response.out.write(greeting.avatar)
      else:
        self.response.out.write("No image")
 
class UserShowImageMin(webapp.RequestHandler):
  def get(self, pseudonim , pic_key):
    buvoapp = False
    imagemaxurl = ""
    lank = UserNone(email=None, federated_identity=None)
    try:
        buvesapp = db.GqlQuery("SELECT * FROM Vartotojai WHERE userid = :1", pic_key)
        for app in buvesapp:
            avatarmin=app.avatarmin
            buvoapp = app.rodyti
            lank=app.lankytojas
    except:
            klaida=True

    thubnail=getphoto(lank.email())
    if buvoapp:
      self.response.headers['Content-Type'] = "image/png"
      self.response.out.write(avatarmin)

    elif thubnail:
      imagemaxurl = str(thubnail)
      uphoto=imagemaxurl.split("/s144/", 1)
      slasas="/s50/"
      imagemaxurl = slasas.join(uphoto)
      self.response.set_status(302)
      self.response.headers['Location'] = imagemaxurl
    else:
      self.response.set_status(302)
      self.response.headers['Location'] = avatarminurl2
      self.response.out.write("No image " +pic_key)
    
class UserShowImageMax(webapp.RequestHandler):
  def get(self, pseudonim , pic_key):
    buvoapp = False
    avatarmax = ""
    try:
        buvesapp = db.GqlQuery("SELECT * FROM Vartotojai WHERE userid = :1", pic_key)
        for app in buvesapp:
            avatarmax=app.avatarmax
            buvoapp = app.rodyti
    except:
        klaida=True

    if buvoapp:
      self.response.headers['Content-Type'] = "image/png"
      self.response.out.write(avatarmax)
    else:
      self.response.set_status(302)
      self.response.headers['Location'] = avatarmaxurl2
      self.response.out.write("No image " +pic_key)
    
    
class SwitComments(webapp.RequestHandler):
  def get(self):
    userid = "0"
    pseudonimas = "Anonymous"
    lank = ""
    vartkey=""
    user = users.get_current_user()
    usercomm = False
    url='/comments'
    try:
        buvesapp = db.GqlQuery("SELECT * FROM Vartotojai WHERE lankytojas = :1", user)
        for app in buvesapp:
            userid = app.userid
            pseudonimas = str(app.pseudonimas)
            lank=app.lankytojas
            vartkey=app.key()
        vartot = db.get(vartkey)
        comm = db.get(self.request.get("id"))
        kname=comm.kind()
        vartot_comm=comm.vartot
        vartot_comm_key=vartot_comm.key()
        vartot_comm_vartot=db.get(vartot_comm_key)
        if (userid == vartot_comm_vartot.userid):
            usercomm = True
    except:
        klaida=True
    try:
        if ((users.GetCurrentUser() and users.get_current_user() == comm.author) or (usercomm) or users.is_current_user_admin()) and ((kname == 'Commentsrec') or (kname == 'Commentsrec2')):
            if self.request.get("show")=="del" and users.is_current_user_admin():
                comm.delete()
            if self.request.get("show")=="yes":
                comm.rodyti=True
                comm.put()
            if self.request.get("show")=="no":
                comm.rodyti=False
                comm.put()
        if kname == 'Commentsrec':
            url='/comments'
        if kname == 'Commentsrec2':
            userid=comm.userid
            rname=comm.rname
            url='/'+cmspath2+'-usercommpage-'+langdef+'.'+fileext+'/'+rname+'/'+userid
    except:
        klaida=True
    self.redirect(url)
class SubmitComments(webapp.RequestHandler):
  def post(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    connt=""
    try:
        codeimg = db.get(self.request.get("scodeid"))
    except:
        prn="Error"
    if codeimg and codeimg.code == self.request.get("scode"):
        codeimg.delete()
        greeting = Commentsrec()
        greeting.rodyti = True
        greeting.ipadresas = os.environ['REMOTE_ADDR']
#	greeting.laikas = datetime.datetime.now()
        if users.get_current_user():
        	greeting.author = users.get_current_user()
        htmlerr=True
        connt = self.request.get("content")
        connt2 = cgi.escape(connt)
        if connt==connt2:
        	htmlerr=False
        connt = render_bbcode(connt)
        connt = connt[0:400]
        greeting.content = connt
#    priesduom = self.request.get("img")
        greeting.rname = "Anonymous"
        if self.request.get("img"):
          try:
              avatar = images.resize(self.request.get("img"), width=96, height=96, output_encoding=images.PNG)
              greeting.avatar = db.Blob(avatar)
              avatarmax = images.resize(self.request.get("img"), width=600, height=400, output_encoding=images.PNG)
              greeting.avatarmax = db.Blob(avatarmax)
          except:
              avatarerr="Error"
        if self.request.get("rname"):
          greeting.rname = cgi.escape(self.request.get("rname")[0:60])
        if not htmlerr:
        	greeting.put()
        	buvoip = False
        	try:
        	    ipaddr = os.environ['REMOTE_ADDR']
        	    if True:
        	      try:
        	        buvesip = db.GqlQuery("SELECT * FROM SpamIP WHERE ipadresas = :1", ipaddr)
        	        for app in buvesip:
        	          buvoip = True
        	      except:
        	        klaida=True
        	      if not buvoip:
        	        app = SpamIP(ipadresas=ipaddr)
        	        app.date = datetime.datetime.now()
        	        app.lastserver = '0'
        	        app.check = False
        	        app.spamcount = '0'
        	        app.spam = False
        	        app.put()
        	except:
        	    klaida=True
        to_addr = _mailrcptto
        user = users.get_current_user()
        if user:
            uname=user.nickname()
            umail=users.get_current_user().email()
        else:
            uname=""
            umail=""
        message = mail.EmailMessage()
        message.subject = os.environ['HTTP_HOST'] + " - comments" + (" %s %s %s") %  (codeimg.code,self.request.get("scode"),htmlerr)
#        message.subject = "www"
        message.sender = _mailsender
        message.to = to_addr
        q_message = ("\n%s: %s \n%s \n%s \n" % ('Page', str(self.request.uri),str(textinfo()),str(textloc())))

        message.body = (_("Comments mail message %(communame)s %(commumail)s %(commrealname)s %(commmessage)s") % {'communame': uname,'commumail': umail,'commrealname': greeting.rname,'commmessage': greeting.content}) + q_message
        message.send()

    self.redirect('/'+cmspath2+'-comments-'+lang+'.'+fileext)


class SiteMapControl(BaseRequestHandler):
 def get(self,rparameters):
#  self.response.out.write('<html><head><style>body {	text-align: center;	font: 11px arial, sans-serif;	color: #565656; } .clear { clear:both; } .comm-container { margin-bottom:20px;} .comm-name { font-size:10pt; float:left; width:20%; padding:5px; overflow:hidden; } .comm-text { float:left; line-height:17px; width:70%; padding:5px; padding-top:0px; overflow:hidden; } .font-small-gray { font-size:10pt !important; }</style></head><body>')
  param=urlparam(rparameters)
  ext=param['ext']
  lang=param['lang']
  aps=param['aps']
  kalb=param['kalb']
  lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
  _ = lang1.ugettext
  wtext=""
     
  buvoappcheck=""
  user = users.get_current_user()
  usercpsmurl = ("/%s-sitemapcp2-%s.%s" % (cmspath2,lang,fileext))
  out=("<table><form method=\"POST\" action=\"%s\">\n" % (usercpsmurl))
  freqvalues = {
      '1': 'always',
      '2': 'hourly',
      '3': 'daily',
      '4': 'weekly',
      '5': 'monthly',
      '6': 'yearly',
      '7': 'never'
    }
  selecttext=""
  namelist = ''
  if users.is_current_user_admin():
    sitemapbuvo = {}
    query = datastore.Query('Page')
    entities = query.Get(1000)
    namelist = ''
    for entity in entities:
        sitemaprodyti=True
        rssprodyti=True
        sitemapfreqkey='weekly'
        buvosmcheck="" 
        buvorsscheck="" 
        commenablegocheck="" 
        commenablefbcheck="" 
        commenablelicheck="" 
        commenablevkcheck="" 
        ename="---" 
        pagekey=entity.key()
        sitemapprio='0.5'
        if 'name' in entity.keys():
            ename=entity['name']
        if 'sitemapfreq' in entity.keys():
            sitemapfreqkey=entity['sitemapfreq']
        if 'sitemapprio' in entity.keys():
            sitemapprio=entity['sitemapprio']
        if 'sitemaprodyti' in entity.keys():
            if entity['sitemaprodyti']:
                sitemaprodyti=entity['sitemaprodyti']
                buvosmcheck="checked=\"yes\"" 
        if 'rssrodyti' in entity.keys():
            if entity['rssrodyti']:
                sitemaprodyti=entity['rssrodyti']
                buvorsscheck="checked=\"yes\"" 
        if 'commenablego' in entity.keys():
            if entity['commenablego']:
                commenablegocheck="checked=\"yes\"" 
        if 'commenablefb' in entity.keys():
            if entity['commenablefb']:
                commenablefbcheck="checked=\"yes\"" 
        if 'commenableli' in entity.keys():
            if entity['commenableli']:
                commenablelicheck="checked=\"yes\"" 
        if 'commenablevk' in entity.keys():
            if entity['commenablevk']:
                commenablevkcheck="checked=\"yes\"" 
        selecttext=("<select name=\"freq_%s\">" % (ename))
        for fname in sorted(freqvalues.iterkeys()):
            freqvalue = freqvalues[fname]
            selecttextyes=""
#            if cmp(int(fname),int(sitemapfreqkey))==0:
            if freqvalue==sitemapfreqkey:
                selecttextyes="selected=\"selected\""
            selecttext=selecttext+("<option %s>%s</option>" % (selecttextyes,freqvalue))
        selecttext=selecttext+"</select>\n"

        out=out+("<tr><td>%s</td><td><input type=\"checkbox\" name=\"sitemaprodyti\" value=\"%s\" %s></td><td>%s</td><td><input type=\"text\" size=\"4\" name=\"prio_%s\" value=\"%s\" > RSS <input type=\"checkbox\" name=\"rssrodyti\" value=\"%s\" %s></td></tr>\n" % (ename,ename,buvosmcheck,selecttext,ename,sitemapprio,ename,buvorsscheck))
        out=out+("<tr><td>&nbsp;</td><td colspan=\"3\"> Google comments <input type=\"checkbox\" name=\"commenablego\" value=\"%s\" %s> Facebook comments <input type=\"checkbox\" name=\"commenablefb\" value=\"%s\" %s> LinkedIn comments <input type=\"checkbox\" name=\"commenableli\" value=\"%s\" %s> VKontakte comments <input type=\"checkbox\" name=\"commenablevk\" value=\"%s\" %s></td></td></tr>\n" % (ename,commenablegocheck,ename,commenablefbcheck,ename,commenablelicheck,ename,commenablevkcheck))
        namelist = namelist + "||" + str(base64.urlsafe_b64encode(str(ename)))
  out=out+"<tr><td colspan=\"4\"><input type=\"hidden\" name=\"namelist\" value=\""+str(namelist)+"\" ></td></tr>\n"
  out=out+"<tr><td></td><td></td><td></td><td><input type=\"submit\"></td></tr>\n"
  out=out+"</form></table>\n"


  wtext = out 
  page = Page.loadnew("sitemapcp")
  page.content = wtext
  page_name2 = 'menu'+'-'+lang+'.'+fileext
  page2 = Page.load(page_name2)
  page3 = Page.loadnew("kalbos")
  textaps=''
  if len(aps)>0:
    textaps=aps+'.'
  text=''
  for name, value in kalbossort:
    text = text + (_kalbhtml % ('sitemapcp', textaps+name, ext, name, name))
  page3.content = text
  self.generate('view.html', lang, {
    'imgshar': False,
    'noedit': '1',
    'application_name': siteauth(),
    'kalbos': page3,
    'menu': page2,
    'page': page,
  })

class SiteMapControl2(webapp.RequestHandler):
  def post(self, rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext

    user = users.get_current_user()
    now = datetime.datetime.now()
    buvo = False
    if user:
#      try:
      if users.is_current_user_admin():
       photoal=[]
       namelist2=[]
       albumbuvo = {}
       rssbuvo = {}
       commenablegobuvo = {}
       commenablefbbuvo = {}
       commenablelibuvo = {}
       commenablevkbuvo = {}
       albumname = ""
#       form = cgi.FieldStorage()
#       item = form.getvalue("sitemaprodyti")
#       if form["namelist"].value:
#         namelist=form["namelist"].value
#         namelist2=namelist.split("||")
#       if isinstance(item, list):
#         for item in form.getlist("sitemaprodyti"):
#           photoal.append(item)
#       else:
#         photoa = form.getfirst("sitemaprodyti", "")
#         photoal.append(photoa) 
       namelist=self.request.POST['namelist']
       namelist2=namelist.split("||")
       photoal=self.request.POST.getall('sitemaprodyti')
       rssal=self.request.POST.getall('rssrodyti')
       commenablegoal=self.request.POST.getall('commenablego')
       commenablefbal=self.request.POST.getall('commenablefb')
       commenablelial=self.request.POST.getall('commenableli')
       commenablevkal=self.request.POST.getall('commenablevk')
       for albumn2 in namelist2: 
         if len(albumn2)>0:
          albumname = base64.urlsafe_b64decode(str(albumn2))
          albumbuvo[albumname]=False
          rssbuvo[albumname]=False
          commenablegobuvo[albumname]=False
          commenablefbbuvo[albumname]=False
          commenablelibuvo[albumname]=False
          commenablevkbuvo[albumname]=False
#          self.response.out.write("namelist:" +albumname+ "<br>\n")
       for albumn2 in photoal: 
         albumbuvo[albumn2]=True
       for albumn2 in rssal: 
         rssbuvo[albumn2]=True
       for albumn2 in commenablegoal: 
         commenablegobuvo[albumn2]=True
       for albumn2 in commenablefbal: 
         commenablefbbuvo[albumn2]=True
       for albumn2 in commenablelial: 
         commenablelibuvo[albumn2]=True
       for albumn2 in commenablevkal: 
         commenablevkbuvo[albumn2]=True
#         self.response.out.write("photoal:" +albumn2+ "<br>\n")
       albumbuvo2=albumbuvo
       rssbuvo2=rssbuvo
       query = datastore.Query('Page')
       entities = query.Get(1000)
       for albumb in entities:
          albumname=str(albumb['name'])
          if albumbuvo.has_key(albumname):  #albumname in albumbuvo:
            albumb['sitemaprodyti'] = albumbuvo[albumname]
            albumb['rssrodyti'] = rssbuvo[albumname]
            albumb['commenablego'] = commenablegobuvo[albumname]
            albumb['commenablefb'] = commenablefbbuvo[albumname]
            albumb['commenableli'] = commenablelibuvo[albumname]
            albumb['commenablevk'] = commenablevkbuvo[albumname]
            albumb['sitemapfreq'] = self.request.POST["freq_"+albumname]
            albumb['sitemapprio'] = self.request.POST["prio_"+albumname]
#            self.response.out.write("buvo:" +albumname+" "+str(albumbuvo[albumname])+ "<br>\n")
            albumbuvo2.pop(albumname)
          datastore.Put(albumb)

    self.redirect('/'+cmspath2+'-sitemapcp-'+lang+'.'+fileext)


class CodeImage(webapp.RequestHandler):
 def get(self):
#  img = PNGCanvas(256, 256)
#  pix = [0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,1,1,1,1,0,0,0,1,1,1,1,0,0,0,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,0,0,1,1,1,1,0,0,0,0,0,0,0,1,0,0,1,1,1,0,0,0,0,0,0,0,0,1,0,0,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,1,1,0,0,1,1,1,0,0,0,0,0,0,1,1,1,0,0,1,1,1,0,0,0,0,0,0,1,1,1,0,0,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1,0,0,0,1,1,1,1,1,1,0,0,0,1,1,1,0,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,1,0,0,1,1,1,0,0,0,0,0,0,0,1,1,0,0,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,0,0,1,1,1,1,0,0,0,0,0,0,1,0,0,0,1,1,1,1,0,0,0,0,0,1,1,1,0,0,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,1,0,0,0,0,0,0,1,1,1,1,0,0,0,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
  krast=5
  starp=2
#  splot = 14;
#  sauks = 14;
  pix = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,1,1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,1,1,0,0,0,0,1,1,0,1,1,0,0,0,0,1,1,0,1,1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1,1,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,0,1,1,0,1,1,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,1,1,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,1,1,1,0,0,0,1,1,1,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,1,1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1,0,0,1,1,0,0,0,0,0,0,0,1,1,0,1,1,1,0,0,0,1,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,1,1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,1,1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1,1,0,1,1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,1,0,0,0,1,1,1,0,1,1,0,0,0,0,0,0,0,1,1,0,0,1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
  krast=5
  starp=2
  splot = 14
  sauks = 14
  splot = 9
  sauks = 15
  nn=6
  istr=int(math.sqrt((splot/2)*(splot/2)+(sauks/2)*(sauks/2)))
  splot2 = istr*2
  sauks2 = istr*2
  plot=2*krast + nn*splot + (nn-1)*starp;
  auks=2*krast + sauks;
  plot2=2*krast + nn*splot2 + (nn-1)*starp
  auks2=2*krast + sauks2;


#  img = PNGCanvas(plot, auks, [0, 0,0,0])
#  img = PNGCanvas(plot2, auks2, [0, 0,0,0])
  img = PNGCanvas(plot2, auks2, [0xff, 0xfa, 0xcd, 0xff])
 # img = PNGCanvas(plot, auks, [0, 0,0,0])
  ss=[0,2,4,6,8,1,3,5,7,9]
  try:
    codeimg = db.get(self.request.get("id"))
    kodas=codeimg.code
  except:
    kodas="000000"
  for i in range(0, 6):
   sx2 = "%s" % kodas[i:i+1]
   try:
      sx = int(sx2)
   except:

      sx=0
   #   sx = random.randrange(0, 10)
   alfa=((random.randrange(0, 90 , 5)-45)*math.pi)/180
   for y in range(1, sauks):
#    alfa=math.pi/2
#    alfa=math.pi/4
    for x in range(1, splot):
      nr = sx*(splot*sauks)+(y-1)*splot+x-1
      xcor=x-splot/2 -1
      ycor=y-sauks/2-1
      istrs=math.sqrt(xcor*xcor+ycor*ycor)
      alfa1=math.atan2(ycor,xcor)
      xcornew=istrs*math.cos(alfa1+alfa)
      ycornew=istrs*math.sin(alfa1+alfa)
      xx=int(krast+i*(starp+splot2)+splot2/2+1+xcornew)
      yy=int(krast+sauks2/2+1+ycornew)
#      xx=krast+i*(starp+splot2)+xcor+splot2/2 +1;
#      yy=krast+ycor+sauks2/2 +1;
      if pix[nr]==1:
#          img.point(xx, yy, [0xff, 0, 0, 0xff])
        img.point(xx, yy, [0, 0, 0, 0xff])
#        img.point(xx, yy, [0xff, 0xfa, 0xcd, 0xff])


  self.response.headers['Content-Type'] = "image/png"
  self.response.out.write(img.dump())

class UserNone(object):

  __user_id = None
  __federated_identity = None
  __federated_provider = None

  def __init__(self, email=None, _auth_domain=None,
               _user_id=None, federated_identity=None, federated_provider=None,
               _strict_mode=True):

    if email is None:
      email = ''

    self.__email = email
    self.__federated_identity = federated_identity
    self.__federated_provider = federated_provider
    self.__auth_domain = _auth_domain
    self.__user_id = _user_id or None


  def nickname(self):
    return self.__email

  def email(self):
    return self.__email

  def user_id(self):
    return self.__user_id

  def auth_domain(self):
    return self.__auth_domain

  def federated_identity(self):
     return self.__federated_identity

  def federated_provider(self):
    return self.__federated_provider


def getphoto(useris):
    yra=False
    try:
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
    except:
        yra=False
    if yra:
        return phototurim
    else:
        return False


def mainold():
    try:
        imgcodes = db.GqlQuery("SELECT * FROM Codeimagereg WHERE date < :1", datetime.datetime.now() + datetime.timedelta(minutes=-15))
        for imgcode in imgcodes:
            imgcode.delete()
    except:
        klaida=True

    
    redir = False
    if os.environ['HTTP_HOST']=='www.upe.lt' or os.environ['HTTP_HOST']=='lt.upe.lt' or os.environ['HTTP_HOST']=='us.upe.lt' or os.environ['HTTP_HOST']=='upe.lt':
      redir = True
    redir2 = False
    if os.environ['HTTP_HOST']=='google5353c7992b3833b7.nerij.us':
      redir2 = True
    
    
    
    buvoapp = False
    try:
        thisappver = os.environ['CURRENT_VERSION_ID']
        thisappid = os.environ['APPLICATION_ID']
        thisappsoftver = os.environ['SERVER_SOFTWARE']
        thishostname = os.environ['DEFAULT_VERSION_HOSTNAME']

        if True:
          try:
            buvesapp = db.GqlQuery("SELECT * FROM AppVer WHERE appver = :1", thisappver)
            for app in buvesapp:
              app.timelast = datetime.datetime.now()
              app.put()
              buvoapp = True
          except:
            klaida=True

#      db.put(buves_vart)
          if not buvoapp:
            app = AppVer(appver=thisappver)
            app.timestart = now
            app.timelast = now
            app.enable = False
            app.appsoftver = thisappsoftver
            app.appid = thisappid
            app.hostname = thishostname
            app.put()
    except:
        klaida=True

    try:
        codedb = db.GqlQuery("SELECT * FROM DinCode WHERE codename = :1", "start")
        for thiscode in codedb:
            thiscode = thiscode.codetext
        appon = eval(thiscode)
    except:
        appon=False

def handle_500(request, response, exception):
    greeting = ''
    items = os.environ.items()
    items.sort()
    for name, value in items:
        aaa = "%s\t= %s\n" % (name, value)
        greeting = greeting + aaa
 
    lines = ''.join(traceback.format_exception(*sys.exc_info()))
    message = mail.EmailMessage()
    message.subject = os.environ['HTTP_HOST'] + " - Error500 - " + os.environ['REQUEST_ID_HASH']
    message.sender = _mailsender
    message.to = _mailrcptto
    message.body = "%s\n\n%s" % (greeting,lines)
    message.send()
    response.write("<html><body><h1>Internal Server Error 500</h1>\n<xmp>")
#    response.write("%s\n\n" % (greeting))
#    response.write(cgi.escape(lines, quote=True))
    response.write("</xmp></body></html>")

#applicationdisable = webapp.WSGIApplication([('/(.*)', SiteDisable),], debug=_DEBUG)
#applicationredir = webapp.WSGIApplication([('/(.*)', RedirN),], debug=_DEBUG)
#applicationredir2 = webapp.WSGIApplication([('/(.*)', RedirN2),], debug=_DEBUG)
app = webapp.WSGIApplication([
      routes.DomainRoute(r'<:(upe\.lt|lt\.upe\.lt|us\.upe\.lt|www\.upe\.lt)>', [
          webapp.Route('/(.*)', handler=RedirN),
      ]),

      ('/install', WikiInstall),
      ('/'+cmspath2+'-env-(.*)', WikiEnv),
      ('/'+cmspath2+'-fb-(.*)', WikiFB),
      ('/'+cmspath2+'-li-(.*)', WikiLI),
      ('/'+cmspath2+'-vk-(.*)', WikiVK),
      ('/'+cmspath2+'-ver-(.*)', WikiExec),
      ('/'+cmspath2+'-login-(.*)', WikiLogin),
      ('/'+cmspath2+'-admin-(.*)', WikiAdmin),
      ('/'+cmspath2+'-mod(.*)-(.*)', WikiMod),
      ('/'+cmspath2+'-lietuvos(.*)-(.*)', WikiMod),
      ('/'+cmspath2+'-sitemapcp-(.*)', SiteMapControl),
      ('/'+cmspath2+'-sitemapcp2-(.*)', SiteMapControl2),
      ('/'+cmspath2+'-memberlistshort-(.*)', VartSarTrumpas),
      ('/'+cmspath2+'-fbmemberlistshort-(.*)', FBUserListSort),
      ('/'+cmspath2+'-limemberlistshort-(.*)', LIUserListSort),
      ('/'+cmspath2+'-vkmemberlistshort-(.*)', VKUserListSort),
      ('/'+cmspath2+'-memberlist-(.*)', VartSar),
      ('/'+cmspath2+'-usercontrolpanel-(.*)', UserControl),
      ('/'+cmspath2+'-usercpsubmit-(.*)', UserControlSend),
      ('/'+cmspath2+'-userpicacontrol-(.*)', UserPicaControl),
      ('/'+cmspath2+'-userpicasubmit-(.*)', UserPicaControlSend),
      ('/'+cmspath2+'-userpicapage-(.*)/([-\w]+)/([0-9_]+)', UserPicaPage),
      ('/'+cmspath2+'-useryoutpage-(.*)/([-\w]+)/([0-9_]+)', UserYoutPage),
      ('/'+cmspath2+'-usercommpage-(.*)/([-\w]+)/([0-9_]+)', UserCommPage),
      ('/'+cmspath2+'-usercommsubmit-(.*)/([-\w]+)/([0-9_]+)', UserCommSubmit),
      ('/'+cmspath2+'-usermailformpage-(.*)/([-\w]+)/([0-9_]+)', UserMailFormPage),
      ('/'+cmspath2+'-usersendmail-(.*)/([-\w]+)/([0-9_]+)', UserMailSend),
      ('/'+cmspath2+'-userpage-(.*)/([-\w]+)/([0-9_]+)', UserShowPage),
      ('/'+cmspath2+'-userimagemin/([-\w]+)/([0-9_]+)', UserShowImageMin),
      ('/'+cmspath2+'-userimage/([-\w]+)/([0-9_]+)', UserShowImageMax),
      ('/'+cmspath2+'-comments-(.*)', Comments),
      ('/'+cmspath2+'-atsiliepimai-(.*)', Comments),
      ('/'+cmspath2+'-commsubmit-(.*)', SubmitComments),
      ('/'+cmspath2+'-mailform-(.*)', MailForm),
      ('/'+cmspath2+'-siustilaiska-(.*)', MailForm),
      ('/'+cmspath2+'-sendmail-(.*)', MailSend),
#      ('/'+cmspath2+'-searchid-(.*)', VarId),
      ('/commswit', SwitComments),
      ('/commimg', CommentsImage),
      ('/codeimg', CodeImage),
      ('/(.*)favicon.ico', WikiFav),
      ('/'+cmspath2+'-guestbook-(.*)', WikiGuest),
      ('/'+cmspath2+'-sveciai-(.*)', WikiGuest),
      ('/'+cmspath2+'-sing-(.*)', SingGuestbook),
      ('/'+cmspath2+'-ls-(.*)', ListDir),
      ('/'+cmspath2+'-download-(.*)', WikiRedirDown),
#      ('/redir.php/(.*)', WikiRedir),
#      ('/redir(.*)', WikiRedir),    
      ('/'+cmspath2+'-([-\w]+)-(.*)', WikiPage),
      ('/(.*)', WikiRedirMain),
    ], debug=_DEBUG)

app.error_handlers[500] = handle_500

#    wsgiref.handlers.CGIHandler().run(application)
#    if redir:
#        applicationredir.run()
#        exit(0)
#    if redir2:
#        applicationredir2.run()
#        exit(0)
#    if appon:
#        app.run()
#        exit(0)
#    else:
#        applicationdisable.run()
#        exit(0)


#if __name__ == '__main__':
#    main()
#if __name__ == '__main__':
#  try:
#    main()
#  except:
#    applicationerror = webapp.WSGIApplication([('/(.*)', HttpError),], debug=_DEBUG)
#    run_wsgi_app(applicationerror)
#    exit(0)
 
