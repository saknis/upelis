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


__author__ = 'Nerijus Terebas'


import urllib
import os
import locale 
import gettext 
from upelis_settings import *
from wiki import Page

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


class modobj2test(object):
  def cont(self,req,modname,rparameters):
    param=urlparam(rparameters)
    ext=param['ext']
    lang=param['lang']
    aps=param['aps']
    kalb=param['kalb']
    lang1 = gettext.translation (cmstrans2, locale_path, [kalb] , fallback=True) 
    _ = lang1.ugettext
    modname2 = 'custommodule'
    page = Page.loadnew(modname2)
    page.content = "<h1>test %s</h1>test" % (req.request.get('info'))
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
