#!/usr/bin/env python
# -*- coding:utf8 -*-

import cgi
#import datetime
#import glob, os
import os
import cStringIO
#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2 as webapp
from pngcanvas import PNGCanvas
from gdfont import GDFont
#from StringIO import StringIO
import base64

class Image(webapp.RequestHandler):
 def get(self):
#  f = open("ttt.zip", "rb")

  bio1_b64 = \
  """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
  AAAASUVORK5CYII=
  """
  png1_b64 = \
  """iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAIAAADTED8xAAAABnRSTlP///////+evUsyAAADtElE
  QVR42u3YgY0DQQzDQPdftLFdGAtwiCsglqhP7mcHaGMDqJtvA6j/3bcB1H/12ADqv/ltAPU3XhtA
  134bQN1+G0DdfhtA3X4bQN1+G0DdfhtA3X4bQN1+G0DdfhtA3X4bQN1+G0DdfhtA3X4bQN1+G0Dd
  fhtA3X4bAPdsAKyzAfDNBlA3zQZQd8wGULfLBlD3ygZQN8oGUHfJBlC3yAZQ98cGUDfHBlB3xgZQ
  t8UGUPfEBlA3xAZQd8MGULfCBlD3wQZQN8EGsO6H9qUAvcsCGpcIdC0XaFk60K+MoFlJQafygjal
  Bj3KDhqUIHQnR2hNmtCXTKEpyUJH8oV2pAy9yBoakTh0IXdoQfqQvw4geU1A5vqAtLUCOesGEtYQ
  ZKsnSFVbkKfOIEnNQYb6kx60KDfoUmLQqKygVylBu/KBjiUDTcsE+pYGtC4H6F4CYIDbwQNXgw3u
  BSdcCma4EfxwHVjiLnDFRWCMW8AbV4A9Pj845JODSewHn9gPVrEf3GI/GMZ+8Iz9YBv7wTn2g3ns
  R9o/9qO7AfajuwH2o7sB9qO7AfajuwH2o7sB9qO7AfajuwH2o7sB9qO7AfajuwH2o7sB9qO7Afaj
  uwH2n7bi8WQf/PU9oBJ0N8B+dDfAfu8AHo93gN73gBrgtxDgGwDeATwe7wD+CwT0fvfbAOpvvTbg
  HcDj8Q7Q/o+nYtC13wZQt98GULffBlC33wZQt98GULffBlC33wZQt98GULffBlC33wZQt98GULff
  BlC33wZQt98GULffBsA8GwDnbABsswHUPbMB1A2zAdTdsgHUrbIB1H2yAdRNsgHUHbIB1O2xAdS9
  sQHUjbEB1F2xAdQtsQHU/bAB1M2wAdSdsAHUbbAB1D2wAfZLALqXA7QuDehbJtC0ZKBj+UC7UoJe
  ZQWNSgy6lBu0KD3oT4bQnCShM3lCW1KFnmQLDUkYupEztCJt6EPm0ITkoQP5Q/pagNx1AYlrBLLW
  C6SsHchXR5CspiBTfUGaWoMcdQcJalB20KPUoE15QaeSgmZlBP1KB1qWC3QtEWhcFtC7FKB994MD
  LgcT3Aw+uBascCe44UIwxG3giavAFveAMy4Bc9wA/vj0YJHPDS6xH4xiP3jFfrCL/eAY+8E09oNv
  7Afr2A/usR9lA9mP7gbYj+4G2I/uBtiP7gbYj+4G2I/uBtiP7gbYj+4G2I/uBtiP7gbYj+4G2I/u
  BtiP7gbYj+4G2I/uBtiP7gbYj+4G2I/uBtiP7gbYj+wGHstS6mBKh9nJAAAAAElFTkSuQmCC
  """
  imghex=base64.decodestring(bio1_b64)
  f = cStringIO.StringIO(imghex)

#  f=cStringIO.StringIO() 
#  f.write(img)
#  img = PNGCanvas(256, 256)
  img = PNGCanvas(256, 256, [0, 0,0,0])
  img.load(f)
  f.close()
  font=GDFont()
  font.load( 'giant_w57.gd','gdfonts')
  img=GDFont.gdfontstring(font,img,"Bioritmai",5,5,[0xff, 0xff, 0, 0xff])
  font2=GDFont()
  font2.load( 'medium_w57.gd','gdfonts')
  img=GDFont.gdfontstring(font2,img,"ABCabc",5,25,[0xff, 0xff, 0, 0xff])

  for i in range(0, 256):
   img.point(i, i, [0xff, 0, 0, 0xff])
   ii = 256 - i
   img.point(ii, i, [0xff, 0, 0, 0xff])
   img.point(122, i, [0xff, 0, 0, 0xff])
   img.point(126, i, [0xff, 0, 0, 0xff])
   img.point(130, i, [0xff, 0, 0, 0xff])
   img.point(134, i, [0xff, 0, 0, 0xff])
   img.point(i, 122, [0xff, 0, 0, 0xff])
   img.point(i, 126, [0xff, 0, 0, 0xff])
   img.point(i, 130, [0xff, 0, 0, 0xff])
   img.point(i, 134, [0xff, 0, 0, 0xff])
  self.response.headers['Content-Type'] = "image/png"
  self.response.out.write(img.dump())
app = webapp.WSGIApplication([
  ('/ttt', Image)
 ], debug=True)
#def main():
#  run_wsgi_app(application)
#if __name__ == '__main__':  
#  main()