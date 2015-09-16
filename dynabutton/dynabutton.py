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


import _imaging, ImageFont, ImageDraw, ImageFilter
import os, sys

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
                   align = CENTER):
    button_text = unicode (button_text, "utf-8")
    raw_button = Image.open (button_filename)
    if height is None:
        height = raw_button.size[1]
    if left_width is None:
        left_width = raw_button.size[0] / 2 - 1
    if right_width is None:
        right_width = raw_button.size[0] / 2 - 1
    if center_slice is None:
        center_slice = (left_width, raw_button.size[0] - right_width)
    font = ImageFont.truetype (font_file, font_size)
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

def cgi_button ():
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

    #http header:
    sys.stdout.write ("Content-Type: image/%s\n\n" % image_type)

    #check if this button was already generated and is cached:
    glyphs = ascii_letters + digits
    #generates a unique printable string based on the button passed parameters:
    cached_filename = "".join ([glyphs [ord(i) % 62]
                                for i in  md5.new(
                                      cPickle.dumps(param_dict, 2)).digest()])
    cached_filename = "%s%s%s.%s" % (BUTTON_CACHE_PATH, os.path.sep, cached_filename, image_type)
    try:
        button_time = os.stat(cached_filename)[-2]
    except OSError:
        button_time = 0
    except IOError:
        button_time = 0
    if param_dict.has_key ("button_filename"):
        button_filename = param_dict["button_filename"]
    else:
        button_filename = DEFAULT_BUTTON
    template_time = os.stat (button_filename) [-2]

    if button_time >= template_time:
        sys.stdout.write (open (cached_filename,"r").read())
    else:
        button = create_button (**param_dict)
        button.save (sys.stdout, image_type)
        try:
            button.save (cached_filename)
        except OSError:
            pass
        except IOError:
            pass

if os.environ.has_key("SCRIPT_NAME"):
    #assume we are running as cgi!
    import cgi
    import cPickle, md5
    from string import ascii_letters, digits

    cgi_button ()
    

elif __name__ == "__main__":
    d_parameters = {}
    l_parameters = []
    display = False
    for parameter in sys.argv[2:]:
        if parameter=="display":
            display = True
            continue
        if parameter.find (":") == -1:
            l_parameters.append (parameter)
            continue
        key, val = parameter.split(":")
        if "color" in key:
            val = tuple ([int (component) for component in val.split(",")])
        elif key !="button_text":
            try:
                val = int(val)
            except:
                pass
        d_parameters[key] = val
    image = create_button (*l_parameters, **d_parameters)
    image.save (sys.argv[1])
    if display:
        image.show ()