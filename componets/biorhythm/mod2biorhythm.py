#!/usr/bin/env python
# -*- coding:utf8 -*-
#
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


_DEBUG = True

__author__ = 'Nerijus Terebas'

import re
import datetime
import time
from google.appengine.ext.webapp import template


import urllib
import os
import locale 
import gettext 
from upelis_settings import *
from wiki import Page

import cgi
from datetime import timedelta
from datetime import date
import sys
import codecs
import cStringIO
import math
from pngcanvas import PNGCanvas
from gdfont import GDFont



error_log = "/home/upe/data/errorb.log"
referers = ["upelis-new.appspot.com","upelis.org"]

uselog = False	# 1 = YES; 0 = NO


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

_titauth = TITAUTH

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
def urlhost2():
	if os.environ['HTTPS']=="off":
		return str('http://'+os.environ['HTTP_HOST'])
	else:
		return str('https://'+os.environ['HTTP_HOST'])


class modobj2biorhythm(object):
  def cont(self,req,modname,rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    modname2 = 'custommodule'

    if not req.request.get('cmd'):
		page = Page.loadnew(modname2)
    
		greeting = ''
		bio_cgi_url = "/bioview"
		bio_cgi_url = ("%s/%s-mo2%s-%s.%s" % (urlhost2(), cmspath2,modname,lang, fileext))

		gimmet=''
		gimmen=''
		gimdien=''
		simbsafe  = re.compile("[^0-9a-zA-Z]")
		mazosios  = re.compile("[^a-z]")
		skaic  = re.compile("[^0-9]")
		handler = {}
		if 'HTTP_COOKIE' in os.environ:
			cookies = os.environ['HTTP_COOKIE']
			cookies = cookies.split('; ')
			for cookie in cookies:
				cookie = cookie.split('=')
				handler[cookie[0]] = cookie[1]
		if 'terebasGimd' in handler:
			gimd = handler['terebasGimd']
			gimd = "%s" % (skaic.sub("", gimd))
		try:
			gimmet=gimd[0,4]
			gimmen=gimd[4,6]
			gimdien=gimd[6,8]
		except:
			zerr = True
		unixtime=time.time()
		d = datetime.datetime.fromtimestamp(unixtime)
		lang = req.request.get('lang') or 'lt'
		gimmet = req.request.get('gmet') or gimmet
		gimmen = req.request.get('gmem') or gimmen
		gimdien = req.request.get('gdien') or gimdien
		siemet = req.request.get('smet') or d.strftime('%Y')
		men = req.request.get('men') or d.strftime('%m')
		biohtml=''
		if not lang:
			lang = 'lt'
		else:
			lang = mazosios.sub("", lang)
		if not gimmet:
			gimmet = '1970'
		else:
			gimmet = skaic.sub("", gimmet)
		if not gimmen:
			gimmen = '06'
		else:
			gimmen = skaic.sub("", gimmen)
		if not gimdien:
			gimdien = '20'
		else:
			gimdien = skaic.sub("", gimdien)
		if not siemet:
			format = '%Y'
			siemet = d.strftime(format)
		else:
			siemet = skaic.sub("", siemet)
		if not men:
			format = '%m'
			men = d.strftime(format)
		else:
			men = skaic.sub("", men)
		if req.request.get('gmet') and req.request.get('gmem') and req.request.get('gdien'):
			bioduom = "lang="+lang+"&amp;gmet="+gimmet+"&amp;gmem="+gimmen+"&amp;gdien="+gimdien+"&amp;smet="+siemet+"&amp;men="+men
			biohtml = "<img src=\""+bio_cgi_url+"?cmd=1&amp;"+bioduom+"\" height=\"256\" width=\"256\" alt=\"\" />\n"
		template_values2 = {
			'biohtml': biohtml,
			'gimmet': gimmet,
			'gimmen': gimmen,
			'gimdien': gimdien,
			'siemet': siemet,
			'men': men
		}
		directory = os.path.dirname(__file__)
		path = os.path.join(directory,  "bio.html")
		cont1 = template.render(path, template_values2, debug=_DEBUG)

		page.content = cont1
		page_name2 = 'menu'+'-'+lang+'.'+fileext
		page2 = Page.load(page_name2)
		page3 = Page.loadnew("kalbos")
		textaps=''
		if len(aps)>0:
			textaps=aps+'.'
		text=''
		for name, value in kalbossort:
			text = text + (_kalbhtml % ('mo2'+modname, textaps+name, ext, name, name))
		page3.content = text
		req.generate('view.html', lang, {
			'imgshar': False,
			'noedit': '1',
			'application_name': siteauth(),
			'kalbos': page3,
			'menu': page2,
			'page': page,
			})
    elif req.request.get('cmd') == '1':
		
		unixtime=time.time()
		d = datetime.datetime.fromtimestamp(unixtime)
		lang = req.request.get('lang') or 'lt'
		gimmet = req.request.get('gmet') or '1970'
		gimmen = req.request.get('gmem') or '06'
		gimdien = req.request.get('gdien') or '20'
		siemet = req.request.get('smet') or d.strftime('%Y')
		men = req.request.get('men') or d.strftime('%m')
		simbsafe  = re.compile("[^0-9a-zA-Z]")
		mazosios  = re.compile("[^a-z]")
		skaic  = re.compile("[^0-9]")
		if not lang:
			lang = 'lt'
		else:
			lang = mazosios.sub("", lang)
		if not gimmet:
			gimmet = '1970'
		else:
			gimmet = skaic.sub("", gimmet)
		if not gimmen:
			gimmen = '06'
		else:
			gimmen = skaic.sub("", gimmen)
		if not gimdien:
			gimdien = '20'
		else:
			gimdien = skaic.sub("", gimdien)
		if not siemet:
			format = '%Y'
			siemet = d.strftime(format)
		else:
			siemet = skaic.sub("", siemet)
		if not men:
			format = '%m'
			men = d.strftime(format)
		else:
			men = skaic.sub("", men)



		format = '%H:%i:%s %m/%d/%Y %O'
		date = d.strftime(format)


		if lang == 'en':
			bio_new = 'bio_en8.png'
			strbio = "Biorhythms"
			strfiz = "Physical State"
			stremo = "Emotional State"
			strint = "Intellect"
			strmd = "Days of the Month"
			strid = "Survived Days"
			strgd = "Date of Birth"
			strm = "Month"
		else:
			bio_new = 'bio_lt8.png'
			strbio = "Bioritmai"
			strfiz = "Fizin\xEB bukl\xEB"
			stremo = "Emocin\xEB b\xFBsena"
			strint = "Intelektas"
			strmd = "Menesio dienos"
			strid = "I\xF0gyventa dien\xF8"
			strgd = "Gimimo data"
			strm = "M\xEBnuo"
		bio_new = '1m.png'
		color1 = [106, 0,0,0]
		color2 = [0xff, 0xff, 0, 0xff]
		color3 = [128, 255, 0, 0xff]
		color4 = [0,128,255, 0xff]
		color5 = [255,128,255, 0xff]
		color6 = [255,255,0, 0xff]
		color1 = [0x00, 0x30,0xd2,0xFF]
		color2 = [0xf6, 0xf3, 0x00, 0xff]
		color3 = [0xfe, 0x7f, 0xfe, 0xff]
		color4 = [0x7f, 0xfe, 0x00, 0xff]
		color5 = [255,128,255, 0xff]
		color6 = [255,255,0, 0xff]
		color1 = [0xAC, 0x2F,0x93,0xFF]
		color1 = [0x00, 0x00,0x8e,0xFF]
		color2 = [0xCA, 0x45, 0x46, 0xff]
		color3 = [0xd3, 0xa5, 0x6a, 0xff]
		color4 = [0x71, 0xa4, 0xcf, 0xff]
		color5 = [0xfd, 0xd9, 0x13, 0xff]
		color1 = [0x00, 0x00,0x8e,0xFF]
		color2 = [0x2b, 0xf6, 0x42, 0xff]
		color3 = [0xfc, 0xf1, 0x33, 0xff]
		color4 = [0xf8, 0x01, 0xd6, 0xff]
		color5 = [0xff, 0x0e, 0x06, 0xff]
		color6 = [255,255,0, 0xff]
#f6f300
#fe7ffe
#000000
#7ffe00
#0030d2

#00008e - fonas melyna
# ff0e06 raud
#2bf642 zalia
#fcf133 gel
#f801d6 viol


		cikfiz = 23
		cikemo = 28
		cikint = 33
		ilg = [0,31,28,31,30,31,30,31,31,30,31,30,31]

		ys=0
		derr = False
		if gimmet<1970:
			ys=1970-int(gimmet)
		try:
			year=int(gimmet)+ys
			tt1 = datetime.date(int(year), int(gimmen), int(gimdien))
			year=int(siemet)+ys
			tt2 = datetime.date(int(year), int(men), 1)
			t1=time.mktime(tt1.timetuple())
			t2=time.mktime(tt2.timetuple())
			dienu=int((int(t2)-int(t1))/86400)
		except:
			derr = True
#      errtext =  cgi.escape(str(sys.exc_info()[0])) + ' ' + cgi.escape(str(sys.exc_info()[1])) + ' ' + cgi.escape(str(sys.exc_info()[2]))
#      req.response.out.write(errtext)
#      sys.exit(0)
		if derr:
			dienu=0


		ref=False
		if 'HTTP_REFERER' in os.environ:
			for referer in referers:
				pos = os.environ['HTTP_REFERER'].find(referer) # The offset is optional
				if not(pos < 0): # not found
					ref = True
		else:
			ref = True

		if not ref:
      #if uselog:
       #log()
			width = 256
			height = 256
			im = PNGCanvas(256, 256, [255, 255,255,255])
			im.color = [0xff,0,0,0xff]
			im.rectangle(0,0,width-1,height-1)
			im.verticalGradient(1,1,width-2, height-2,[0xff,0,0,0xff],[0x20,0,0xff,0x80])
			im.color = [0,0,0,0xff]
			im.line(0,0,width-1,height-1)
			im.line(0,0,width/2,height-1)
			im.line(0,0,width-1,height/2)
			im.copyRect(1,1,width/2-1,height/2-1,0,height/2,im)
			im.blendRect(1,1,width/2-1,height/2-1,width/2,0,im)
			str = "Bad referer"
			y = 5
			x = 256 / 2 - len(str) * 9 / 2
			x = "%u" % x
			font=GDFont()
			font.load( 'giant_w57.gd','gdfonts')
			im=GDFont.gdfontstring(font,im,str,x,y,[0, 0, 0, 0xff])
		else:
			zerr=False
			im = False
		try:
			directory = os.path.dirname(__file__)
			path = os.path.join(directory, os.path.join('gdfonts', bio_new))
			imghex=file(path,'rb').read()
			f = cStringIO.StringIO(imghex)
			im = PNGCanvas(256, 256, [0, 0,0,0])
			im.load(f)
		except:
			zerr = True
		if zerr:
#        im = PNGCanvas(256, 256, [0, 0,0,0])
			im = PNGCanvas(256, 256, color1)
		zerr=True
		str = strbio
		y = 10
		x = 256 / 2 - len(str) * 9 / 2
		x = "%u" % x
		font5=GDFont()
		font5.load( 'giant_w57.gd','gdfonts')
		font4=GDFont()
		font4.load( 'large_w57.gd','gdfonts')
		font3=GDFont()
		font3.load( 'medium_w57.gd','gdfonts')
		font2=GDFont()
		font2.load( 'small_w57.gd','gdfonts')
		font1=GDFont()
		font1.load( 'tiny_w57.gd','gdfonts')
		if zerr:
			im=GDFont.gdfontstring(font5,im,str,x,y,color2)
		str = strfiz
		y = 130 + 10
		x = 256 / 2 - len(str) * 6 / 2
		x = "%u" % x
		if zerr:
			im=GDFont.gdfontstring(font2,im,str,x,y,color3)
		str = stremo
		y = 130 + 10 + 5 + 12
		x = 256 / 2 - len(str) * 6 / 2
		x = "%u" % x
		if zerr:
			im=GDFont.gdfontstring(font2,im,str,x,y,color4)
		str = strint
		y = 130 + 10 + 5 + 12 + 5 + 12
		x = 256 / 2 - len(str) * 6 / 2
		x = "%u" % x
		if zerr:
			im=GDFont.gdfontstring(font2,im,str,x,y,color5)
		str = strmd
		y = 82 + 4 + 8 + 4
		x = 256 / 2 - len(str) * 5 / 2
		x = "%u" % x
		if zerr:
			im=GDFont.gdfontstring(font1,im,str,x,y,color2)
		str = strid+':'
		y = 130 + 10 + 5 + 12 + 5 + 12 + 5 + 12
		x = 256 / 2 - len(str) * 6
		x = "%u" % x
		if zerr:
			im=GDFont.gdfontstring(font2,im,str,x,y,color2)
		str = " %s" % dienu
		y = 130 + 10 + 5 + 12 + 5 + 12 + 5 + 12
		x = 256 / 2
		x = "%u" % x
		im=GDFont.gdfontstring(font2,im,str,x,y,color2)
		str = strgd+':'
		y = 130 + 10 + 5 + 12 + 5 + 12 + 5 + 12 + 8 + 12
		x = 256 / 2 - len(str) * 7
		x = "%u" % x
		if zerr:
			im=GDFont.gdfontstring(font3,im,str,x,y,color2)
		str = " %s/%s/%s" % (gimmet, gimmen, gimdien)
		y = 130 + 10 + 5 + 12 + 5 + 12 + 5 + 12 + 8 + 12
		x = 256 / 2
		x = "%u" % x
		im=GDFont.gdfontstring(font3,im,str,x,y,color2)
		str = strm+':'
		y = 130 + 10 + 5 + 12 + 5 + 12 + 5 + 12 + 8 + 12 + 6 + 13
		x = 256 / 2 - len(str) * 7
		x = "%u" % x
		if zerr:
			im=GDFont.gdfontstring(font3,im,str,x,y,color2)
		str = " %s/%s" % (siemet,men)
		y = 130 + 10 + 5 + 12 + 5 + 12 + 5 + 12 + 8 + 12 + 6 + 13
		x = 256 / 2
		x = "%u" % x
		im=GDFont.gdfontstring(font3,im,str,x,y,color2)
		prad = 10
		gal = 256 - prad
		im.color = color2
		im.line(prad,80,gal,80)
		ii = ilg[int(men)]
		if int(men) == 2 and int(int(siemet) % 4) == 0:
			ii+=1
		y = 82 + 4
		str = 1
		x = prad - len("%s" % str) * 5 / 2
		x = "%u" % x
		im=GDFont.gdfontstring(font1,im,str,x,y,color2)
		for i in range(5, ii, 5):
			str = i
			x = prad + (i - 1) * (256 - prad - prad) / (ii - 1)
			x = x - len("%s" % str) * 5 / 2
			x = "%u" % x
			im=GDFont.gdfontstring(font1,im,str,x,y,color2)
		pi = math.pi
		x = prad
		xsen = "%u" % x
		y = 80 - 50 * math.sin((1 + dienu) * 2 * pi / cikfiz)
		yfiz = "%u" % y
		y = 80 - 50 * math.sin((1 + dienu) * 2 * pi / cikemo)
		yemo = "%u" % y
		y = 80 - 50 * math.sin((1 + dienu) * 2 * pi / cikint)
		yint = "%u" % y
		for i in range(1, ii):
			x = prad + (i - 1) * (256 - prad - prad) / (ii - 1)
			x = "%u" % x
			im.color = color2
			im.line(x,78,x,82)
			y = 80 - 50 * math.sin((i + dienu) * 2 * pi / cikfiz)
			y = "%u" % y
			im.color = color3
			im.line(xsen,yfiz,x,y)
			yfiz = y
			y = 80 - 50 * math.sin((i + dienu) * 2 * pi / cikemo)
			y = "%u" % y
			im.color = color4
			im.line(xsen,yemo,x,y)
			yemo = y
			y = 80 - 50 * math.sin((i + dienu) * 2 * pi / cikint)
			y = "%u" % y
			im.color = color5
			im.line(xsen,yint,x,y)
			yint = y
			xsen = x

		sgimmet = "%04d" % int(gimmet)
		sgimmen =  "%02d" % int(gimmen)
		sgimdien =  "%02d" % int(gimdien)


		gimd=sgimmet+sgimmen+sgimdien
		expiration = datetime.datetime.now() + timedelta(seconds=3600*24*90)
		exp=expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
		req.response.headers['Content-Type'] = "image/png"
		req.response.headers['Set-Cookie'] = "terebasGimd=%s; path=/; expires=%s" % (gimd,exp)
		req.response.out.write(im.dump())


 


