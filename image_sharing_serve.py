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

_DEBUG = True

import StringIO
#from PIL import Image, ImageDraw, ImageFont
from google.appengine.api import images
import webapp2 as webapp
import wsgiref.handlers
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import os, sys
import cgi
from google.appengine.ext import db
import dynabuttonapp
from image_sharing import Album, Picture
from upelis_settings import *

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

def button():
    param_dict = {}
    text = os.environ["HTTP_HOST"].lower()
    parameters = {'button_text': text, 'button_filename': 'cloud.png', 'text_color': '0,48,255', 'font_file': DYNABFONT, 'font_size': '20', 'left_width': '10', 'right_width': '10'}
    image_type = "png"

    for key in parameters:
        val = parameters[key]
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

    button = dynabuttonapp.create_button (**param_dict)
    return button


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
#      from bindata import LogoButton
#      imagelogo=LogoButton()
#      data2=imagelogo.data
      outnew = StringIO.StringIO()
      button2 = button()
      image_type = "png"
      button2.save(outnew, image_type)
      outnew.seek(0)
      data2=outnew.read()
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

url_map = [('/upelis-pic2(thumbnail|image)-(.*)/([-\w]+)', ImageSharingServeImage)]
app = webapp.WSGIApplication(url_map,debug=True)
