#! /usr/bin/env python
# -*- coding: utf-8 -*-
#    DynaButton - dynamically creates themed buttons, for web or other UI
#    Copyright 2006 - João S. O. Bueno Calligaris
#
#    This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""
This program is Free Software - see the file LICENSE for details

Dynabutton  creates dinamic buttons for WEB or other UIs in real time.
Copyright 2006 - João S. O. Bueno

It can be used either from command line, or as a cgi program.
The accepted parameters are:
                   button_filename     = DEFAULT_BUTTON,
                   button_text         = "OK",
                   font_file           = "VeraSeBd.ttf",
                   font_size           = 18,
                   text_color          = (255, 255, 255),
                   use_shadow          = True,
                   shadow_color        = (0, 0, 0, 192),
                   fuzzy_shadow        = None,
                   shadow_offset       = 1,
                   width               = None,
                   height              = None,
                   left_width          = None,
                   right_width         = None,
                   center_slice        = None,
                   align = CENTER

button_filename    - The filename on the server side which contains a
       template to the button that will be used. The program uses the
       left and right endings of this template as the button caps
       and copies/replicates the middle section. Over this middle
       section, it renders the button text

button_text        - The button text per se. Use utf-8 encoding
font_file          - the font file (currently  ttf files only) on the
       server side which contains the font to be used to render the text.

font_size          - the font size, in pixels
text_color         - The color to render the text. An optional 4 number
       as alpha is accepted

use_shadow         - Whether to render or not a shadow for the text
shadow_color       - the color for the shadow
fuzzy_shadow       - Whether to blur the rendered shadow or not.
shadow_offset      - shadow offset in both x and y directions relative
       to the text.

width              - Button width in pixels. Automatic if not specified.
height             - Button height in pixels. Equal to the one of the
       button template image, if not specified

left_width         - Instead of taking the template's entire left
       half as button cap, use this many pixels. The remaining pixel columns
       up to the ones that make up the right button cap will be replicated/
       resized as needed to create the middle section.

right_width        - The same as left_width, but for the right button cap

center_slice       - Explicit slice of pixel columns on the image template
       that will be replicated as the button center. If not specified, it
       it is auto computed from the left_width and right_width values. (NB,
       if those are also empty, the central pixel column is just stretched
       over to make for the central button area)

align = Text alignment. Allowed values= LEFT, CENTER, RIGHT
        (v.1.2, not implemented for command line mode - use 0,1 or 2 for now)

when used as cgi, the extra parameter "image_type" specifies which image
type will be generated. From the command line, the first parameter is the
output file name, and file_type is based on its extension.
ex.: "png", "jpeg", "gif"  -

Example of CGI usage:

<html>
Teste:
<img src="http://myhost.com/dynabutton.py?button_text=APPLE&
button_filename=botao2.png&text_color=0,48,255"style="vertical-align: middle"
/>
</html>
The various parameters are encoded in the src url!

Example for command line usage:

./dynabutton.py crewind.png  cloud.png REWIND text_color:0,0,0 left_width:15
right_width:15 display

The extra "display" parameters attempts to show the result on the screen.
Python imaging library uses the 'xv' app by default to that. You can
symbolic link another app to xv if you prefer.
"""


import StringIO
#from PIL import Image, ImageDraw, ImageFont
from google.appengine.api import images
import webapp2 as webapp
import wsgiref.handlers
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import os, sys
import cgi
import re
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.api import users
import cPickle, md5
from string import ascii_letters, digits
import datetime

FONT_PATH = "."
#when installing as cgi, create a directory to work as cache:
# default: ./cache/ - make sure the cgi has rw access to it.
BUTTON_CACHE_PATH = "cache"
DEFAULT_BUTTON = "tab.png"

VERSION = "1.2"
LEFT = 0
CENTER = 1
RIGHT = 2

#as of version 1.2, there are 4 button templates:
# "tab.png", "botao2.png", "zap.png" and "cloud.png"
#tab.png should be used with left_width=22 and right_width=21
#cloud.png should be used with left_width=15 and right_width=15

def create_button (button_filename     = DEFAULT_BUTTON,
                   button_text         = "OK",
                   font_file           = "VeraSeBd.ttf",
                   font_size           = 18,
                   text_color          = (38,27,15),
                   use_shadow          = True,
                   shadow_color        = (0, 0, 0, 192),
                   fuzzy_shadow        = None,
                   shadow_offset       = 1,
                   width               = None,
                   height              = None,
                   left_width          = None,
                   right_width         = None,
                   center_slice        = None,
                   align = CENTER):
#    simbsafe  = re.compile("[^0-9a-zA-Z\x2D\x5F\x2E\x2C]")
#    font_file = simbsafe.sub("", font_file)
#    button_filename = simbsafe.sub("", button_filename)
    button_text = unicode (button_text, "utf-8")
    directory = os.path.dirname(__file__)
    button_filename_path = os.path.join(directory, os.path.join('dynabutton', button_filename))
    font_file_path = os.path.join(directory, os.path.join('dynabutton', font_file))

    raw_button = Image.open (button_filename_path)
    if height is None:
        height = raw_button.size[1]
    if left_width is None:
        left_width = raw_button.size[0] / 2 - 1
    if right_width is None:
        right_width = raw_button.size[0] / 2 - 1
    if center_slice is None:
        center_slice = (left_width, raw_button.size[0] - right_width)
    font = ImageFont.truetype (font_file_path, font_size)
    text_size = font.getsize (button_text)
    text_width = text_size[0]
    if width is None:
        width = left_width + text_width + right_width
    center_width = width - left_width - right_width
    bg_color = shadow_color[0:3] + (0,)
    text = Image.new ("RGBA", (text_width, height), bg_color)
    textdraw = ImageDraw.Draw (text)
    textdraw.setfont (font)
    textdraw.setink (text_color)
    #draw text vertically centered:
    textdraw.text ((0, (height - text_size[1]) / 2), button_text )
    if use_shadow:
        if fuzzy_shadow is None:
            #the smooth filter in PIL is buggy and always treat transparent
            # pixels as black.
            #disabling fuzzy shadow for colors other than black.
            if shadow_color[:3] == (0, 0, 0):
                fuzzy_shadow = True
            else:
                fuzzy_shadow = False
        shadow = text
        text = text.copy()
        textdraw.setink (shadow_color)
        textdraw.text ((0, (height - text_size[1]) / 2), button_text )

    if width < left_width + text_width + right_width:
        text = text.resize ((center_width, height),Image.ANTIALIAS)
        if use_shadow:
            shadow = shadow.resize ((center_width, height),Image.ANTIALIAS)
    if use_shadow:
        l_shadow = Image.new ("RGBA", (shadow.size[0] + 6 ,shadow.size[1]), (0, 0, 0, 0))
        l_shadow.paste (shadow, (3,0), shadow)
        if fuzzy_shadow:
            shadow = l_shadow.filter (ImageFilter.SMOOTH_MORE).filter (ImageFilter.SMOOTH_MORE)
        else:
            shadow = l_shadow

    button = Image.new ("RGBA", (width, height), (0,0,0,0))
    slice_width = center_slice[1] - center_slice[0]
    if slice_width < 3:
        #attention: the resize bellow does not use "antialias" - it was giving buggy results,
        #and is not needed for this resize.
        center = (raw_button.crop ((center_slice[0], 0, center_slice[1], height)).
                      resize ((center_width,height)))
    else: #fancy center replication
        local_center_width = center_width
        local_center_width -= center_width % slice_width
        if center_width % slice_width < center_width / 2:
            local_center_width += slice_width
        if local_center_width < slice_width:
            local_center_width = slice_width
        center = Image.new ("RGBA", (local_center_width, height), (0, 0, 0, 0))
        img_slice = raw_button.crop ((center_slice[0], 0, center_slice[1], height))
        for i in range (local_center_width / slice_width):
            center.paste (img_slice,(i * slice_width, 0), img_slice)
        if local_center_width != center_width:
            center = center.resize ((center_width, height), Image.ANTIALIAS)
    button.paste (center, (left_width, 0), center)

    img = raw_button.crop ((0, 0, left_width, height))
    button.paste (img, (0, 0), img)
    img = raw_button.crop ((raw_button.size[0] - right_width, 0,
                                    raw_button.size[0], height))
    button.paste (img, (width - right_width, 0), img)
    if align == LEFT:
        padding = 0
    elif align == CENTER:
        padding = (center_width - text.size[0]) / 2
    elif align == RIGHT:
        padding = center_width - text_size[0]
    else:
        padding = 0
    if use_shadow:
        button.paste (shadow, (left_width + padding + shadow_offset, 0 + shadow_offset), shadow)

    button.paste (text, (left_width + padding, 0), text)
    return button


    


class Gele(webapp.RequestHandler):
  def get(self):
      param_dict = {}
      parameters = cgi.FieldStorage()
      #as of 07/2006, internet explorer still does not workk with
      #trasnaprent png.s downgrading to gif:
      if "ie" in os.environ["HTTP_USER_AGENT"].lower():
          image_type = "gif"
      else:
          image_type = "png"
  
      for key in cgi.FieldStorage():
          val = parameters[key].value
#          if key in  ("button_text"):
#              pass
#          if key in  ("button_filename", "font_file", "text_color", "use_shadow", "shadow_color", "fuzzy_shadow", "shadow_offset", "width", "height", "left_width", "right_width", "center_slice", "align"):
#              simbsafe  = re.compile("[^0-9a-zA-Z\x2D\x5F\x2E\x2C]")
#              val = simbsafe.sub("", val)
#              continue
#          else:
#              val = ""
          if key == "image_type":
              image_type = val
              continue

          if "color" in key:
              try:
                  val = tuple ([int (component) for component in val.split(",")])
              except:
                  val= (0, 0, 0)
          elif key in  ("button_text", "button_filename"):
              pass
          elif key == "font_file":
              val = os.path.join (FONT_PATH, val)
          elif val in ("None", "True","False", "CENTER", "RIGHT", "LEFT"):
              val = eval (val)
          else:
              try:
                  val = int(val)
              except ValueError:
                  val = 0
          param_dict[key] = val

        
      #check if this button was already generated and is cached:
      glyphs = ascii_letters + digits
      #generates a unique printable string based on the button passed parameters:
      but_filename = "".join ([glyphs [ord(i) % 62]
                                  for i in  md5.new(
                                        cPickle.dumps(param_dict, 2)).digest()])
      but_filename = "%s.%s" % (but_filename, image_type)
      filedate = datetime.datetime.now() + datetime.timedelta(days=-14)
      try:
          buvesbut = db.GqlQuery("SELECT * FROM Button WHERE filename = :1", but_filename)
#          buvesbut = db.GqlQuery("SELECT * FROM Button WHERE filename = :1", "pYFJEaJKIoNIUN3u.png")
          for app in buvesbut:
              author = app.author
              filename = app.filename
              fileext = app.fileext
              filedata = app.filedata
              filedate = app.date
              ipadresas = str(app.ipadresas)
      except:
          filedate = datetime.datetime.now() + datetime.timedelta(days=-14)

        
      #http header:
      #sys.stdout.write ("Content-Type: image/%s\n\n" % image_type)
      self.response.headers['Content-Type'] = ("image/%s" % image_type)
      if filedate >= datetime.datetime.now() + datetime.timedelta(days=-7):
#          self.response.out.write('\x89PNG\x0D\x0A\x1A\x0A\x00\x00\x00\x0DIHDR\x00\x00\x00t\x00\x00\x00\x1A\x08\x02\x00\x00\x00\xE9\x06\xEFZ\x00\x00\x00\x06tRNS\xFF\xFF\xFF\xFF\xFF\xFF\x9E\xBDK2\x00\x00\x00\xECIDATx\xDA\xED\x98A\x0E\xC2P\x08D\xB9\xFF\xDD\xBC\x90\x1BMtc\x7E\xAB2\x03T\x8D\xAFa\xD9\x16x\x0C\x94\xDF\xB8\x9CO\xD8\x90\x05\x08\x80\x0B\x5C\x0C\xB8\xC0\x05.\x06\x5C\xE0\xFE1\xDC\xB8\x5D\xDF\x9E\x8C\x1E\xE1h\x5E\x91t\x7F\x8F\x20\x19J\x3C\xB9\x92t\xD4\x84U\x2Fv\x5Ej\x3DB\x7D\x91W\xE7L\x40\x5E\xB6\xCB\x9D\xB6\x12\x25w\x3Dpw\xBDNt\x9F\xE7e\xB7\xF6v\x9B\xE7\xCB\xDF\x06w\xF1jD\x2F\xCD\x04CG\x9E\xAC\xFCf\xEFU\xEER1c\x20\x8Ev\xF7\x12Xe\xF26\x27\x25u\x8A\xF7\xA9\xF1ZR\x12\xF2\xA3\xA3\xE4\x7C\xAF\x28\xBD\x01\xEEVM\x13\xE5\xCD\xC0j\xCC\xDC\xD8\x2B\x8EP\xEE\xD0\xBE\xF2\xDA\xAF1\xAC\x25\x99\x7F\x18\xAE\xBDB\xD6\xA3W\xBF0\xEA\x23\xC5\xC6z\xBF\x02\x0D\x9D\x94\xEA\xC7\x9E\xA1\xE1\x5E\x7C\xB0\x7F\x15\xFB\x89\x83\x2C\x3Fn\xF8q\x83\x01\x17\xB8\xC0\xC5f\xEC\x0A\x3EB\xAA\x97\x88\xFB\xC6\xF0\x00\x00\x00\x00IEND\xAEB\x60\x82')
          self.response.out.write(filedata)
      else:
          button = create_button (**param_dict)
          outnew = StringIO.StringIO()
          button.save(outnew, image_type)
          outnew.seek(0)
          image_data=outnew.read()
          self.response.out.write(image_data)
          try:
              but = Button()
              if users.get_current_user():
                  but.author = users.get_current_user()
              but.filename = but_filename
              but.fileext = image_type
              but.filedata = image_data
              but.ipadresas = os.environ['REMOTE_ADDR']
              but.date = datetime.datetime.now()
              but.put()
          except:
              pass
      

class Button(db.Model):
  author = db.UserProperty()
  filename = db.StringProperty(multiline=False)
  fileext = db.StringProperty(multiline=False)
  filedata = db.BlobProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  ipadresas = db.StringProperty()


url_map = [('/dynab', Gele)]
app = webapp.WSGIApplication(url_map, debug=True)
