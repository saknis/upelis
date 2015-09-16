#!/usr/bin/env python
import os
from pngcanvas import PNGCanvas
class GDFont(object):

  __font_file = None
  __font_data = None
  __font_count = None
  __font_start = None
  __font_width = None
  __font_height = None

  def __init__(self, file=None, data=None, count=None, start=None, width=None, height=None):

    self.__font_file = file
    self.__font_data = data
    self.__font_count = count
    self.__font_start = start
    self.__font_width = width
    self.__font_height = height


  def data(self):
    return self.__font_data
  def count(self):
    return self.__font_count
  def start(self):
    return self.__font_start
  def width(self):
    return self.__font_width
  def height(self):
    return self.__font_height
  def load(self,name,dir):
    directory = os.path.dirname(__file__)
    filepath = os.path.join(dir, name)
    path = os.path.join(directory, filepath)
    data = file(path,'rb').read()
    hex2=""
    for c in data:
      code=ord(c)
      hex2 += "%02x" % code
    code=hex2[0:8]
    if len(code) == 0:
      code="0"
    count= int(code, 16)
    code=hex2[8:16]
    if len(code) == 0:
      code="0"
    start= int(code, 16)
    code=hex2[16:24]
    if len(code) == 0:
      code="0"
    width= int(code, 16)
    code=hex2[24:32]
    if len(code) == 0:
      code="0"
    height= int(code, 16)
    self.__font_file = filepath
    self.__font_data = hex2
    self.__font_count = count
    self.__font_start = start
    self.__font_width = width
    self.__font_height = height
#    return GDFont(name, file=filepath, data=hex2, count=count, start=start, width=width, height=height)
  def gdfontstring(self,pic,str,x,y,color):
    str="%s" % str
    x=int(x)
    y=int(y)
    data=self.__font_data
    count=self.__font_count
    start=self.__font_start
    width=self.__font_width
    height=self.__font_height
    z=0
    for c in str:
      codesim=ord(c)
      for i2 in range(0, height):
        for i3 in range(0, width):
          z0=(codesim*width*height+i2*width+i3)*2+32;
          code=data[z0:(z0+2)]
          if len(code) == 0:
            code="0"
          x0= int(code, 16)
          if x0>0:
            PNGCanvas.point(pic,(x+z*width+i3),(y+i2),color)
      z+=1
    return pic

