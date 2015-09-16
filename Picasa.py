#!/usr/bin/python
#
# Copyright 2008 Wepoco.  http://www.wepoco.org/
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
#

import sys
import time
import re
import urllib
from datetime import datetime, timedelta
from StringIO import StringIO
from datetime import datetime
from xml.etree.ElementTree import parse
from xml.etree.ElementTree import Element, SubElement, ElementTree, fromstring


class Photo:
    def __init__(self, id=None):
        self.id = id
        self.title = None
        self.published = None # When published on picasweb
        self.timestamp = None  # Probably original image file timestamp on PC 
        self.icon = None
        self.thumbnail = None
        self.webpage = None
        self.extime = None # EXIF timestamp from camera
        self.when = None
        self.lat = None
        self.lon = None
        return
    def getDatetime(self):
        if self.extime:
            return self.extime
        elif self.timestamp:
            return self.timestamp
        else:
            return self.published

class Album:
    def __init__(self, name, title=None, thumbnail=None, icon=None, when=None):
        self.name = name
        self.title = title
        self.thumbnail = thumbnail
        self.icon = icon
        self.when = when

class Picasa:
    def ns_tag( self, el ):
        if el.tag[0] == '{':
            return el.tag[1:].split("}")
        else:
            return (None, el.tag)
        pass

    def __init__( self, xml_in=None ):
        if xml_in:
            self.tree = parse(StringIO(xml_in))
            pass
        return

    def albums( self, xml_in ):
        tree = parse(StringIO(xml_in))
        results = {}
        for entry in tree.getroot().findall('{http://www.w3.org/2005/Atom}entry'):
            name = entry.findtext('{http://schemas.google.com/photos/2007}name')
            title = entry.findtext('{http://www.w3.org/2005/Atom}title')
            groupEl = entry.find('{http://search.yahoo.com/mrss/}group')
            thumbEl = groupEl.find('{http://search.yahoo.com/mrss/}thumbnail')
            thumbnail = thumbEl.attrib['url']
            results[name]= Album(name,title=title,thumbnail=thumbnail)
            #for etag in groupEl:
            #    (ns,tag) = self.ns_tag(etag)
            #    print " ", self.ns_tag(etag)
            #    pass
            pass
        return results

    def photos( self, xml_in=None, tree=None ):
        if tree:
            self.tree = tree
        elif xml_in:
            self.tree = parse(StringIO(xml_in))
            pass
        results = []
        for entry in self.tree.getroot().findall('{http://www.w3.org/2005/Atom}entry'):
            photo = Photo(id=entry.findtext('{http://schemas.google.com/photos/2007}id'))
            photo.title = entry.findtext('{http://www.w3.org/2005/Atom}title')
            try:
                # NB this Atom timestamp includes milliseconds and timezone code 'Z'
                # The reg expr discards these parts.
                pubtxt = entry.findtext('{http://www.w3.org/2005/Atom}published')
                pubtxt = "%s" % re.match("(.*)\.(\d+)(.)",pubtxt).group(1)
                photo.published = datetime.strptime(pubtxt, '%Y-%m-%dT%H:%M:%S')
                photo.when = photo.published
            except:
                photo.published = None 
                pass
            try:
                photo.timestamp = datetime.fromtimestamp(0.001 * float(
                        entry.findtext('{http://schemas.google.com/photos/2007}timestamp')))
                photo.when = photo.timestamp
            except:
                photo.timestamp = None
                pass
            try:
                exif = entry.find('{http://schemas.google.com/photos/exif/2007}tags')
                photo.extime = datetime.fromtimestamp(0.001 * float(
                        exif.findtext('{http://schemas.google.com/photos/exif/2007}time')))
                photo.when = photo.extime
            except:
                photo.extime = None
                pass
            try:
                picurl =  entry.find('*/{http://search.yahoo.com/mrss/}content')
                photo.webpage = picurl.attrib['url']
            # Find thumbnail
            except:
                pass
            try:
                thumbs = entry.findall('*/{http://search.yahoo.com/mrss/}thumbnail')
                # The zeroth thumbnail is very small
                photo.icon = thumbs[0].attrib['url']
                photo.thumbnail = thumbs[1].attrib['url']
            except:
                photo.thumbnail = None
                pass
            results.append(photo)
            pass
        return results

    def dataXML( self, out_f, track_key, slip=0, pics=None ):
        if pics == None:
            pics = self.photos()
        data = Element( 'data' )
        try:
            delta = timedelta(seconds=int(slip))
        except:
            delta = timedelta(0)
            pass
        for pic in pics:
            event = SubElement( data, 'event' )
            pictime =  pic.getDatetime() + delta
            pictime.replace(tzinfo=None)        
            event.attrib['start'] = pictime.strftime("%a %b %d %Y %H:%M:%S")
            event.attrib['title'] = pic.title.split(".")[0]
            event.attrib['isDuration'] = "false"
            event.attrib['image']= pic.thumbnail
            #event.attrib['icon'] = pic.icon
            event.attrib['link'] = "?lat=%s&lon=%s" % (pic.lat, pic.lon)
            event.text = """<img src="%s" />""" % (pic.thumbnail)
            pass
        out_f.write( '<?xml version="1.0" encoding="UTF-8"?>\n' )
        ElementTree( data ).write( out_f )
        return

    def getStartDatetimeStr( self, slip=0 ):
        pics = self.photos()
        try:
            delta = timedelta(seconds=int(slip))
        except:
            delta = timedelta(0)
            pass
        return (pics[0].getDatetime()+delta).strftime("%a %b %d %Y %H:%M:%S")

    # Generate requests to update timestamps according to filename pattern.
    # Useful for mobile phones.
    def fixPhotoTimes( self, xml_in ):
        return None
    
def main():
    import urllib
    if len(sys.argv) == 2:
        f = urllib.urlopen("http://picasaweb.google.com/data/feed/api/user/%s?kind=album" % sys.argv[1])
        list = Picasa().albums(f.read())
        for name in list.keys():
            album = list[name]
            print album.title, "(", name, ")" # , album.thumbnail
            pass
        pass
    elif len(sys.argv) == 3:
        f = urllib.urlopen("http://picasaweb.google.com/data/feed/api/user/%s/album/%s?kind=photo" % (sys.argv[1],sys.argv[2]))
        print f.headers
        list = Picasa().photos(f.read())
        for photo in list:
            print photo.title, photo.getDatetime(), photo.webpage, photo.thumbnail
            pass
        pass
    
if __name__ == '__main__':
    main()
