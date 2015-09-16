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
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types



class Pauksciai(db.Model):
  pauksnr = db.StringProperty()
  burys = db.StringProperty()
  buryslot = db.StringProperty()
  seima = db.StringProperty()
  seimalot = db.StringProperty()
  rusis = db.StringProperty()
  rusisen = db.StringProperty()
  rusisru = db.StringProperty()
  rusislot = db.StringProperty()
  wikiurl = db.StringProperty()
  wikiurlru = db.StringProperty()
  wikiurlen = db.StringProperty()
  raudona = db.BooleanProperty()


class modobjpauksciai(object):
  def cont(self,req):
#req.request.get('test')
    aaa=""
    result=dict(name="lietuvospauksciai", fpput=True, title=u'Lietuvos pauk\u0161\u010Diai', descr=u'   ',cont='')
    if req.request.get('cmd') == '1':
        aaa = aaa + "<br /><table border=\"0\"><tbody>\n"
        greetings = db.GqlQuery("SELECT * FROM Pauksciai  WHERE rusis = :1", req.request.get('paukstis'))
        head = u'<h1>Lietuvos pauk\u0161\u010Diai</h1><p>'
        for greeting in greetings:
          result['title']=u'Lietuvos pauk\u0161\u010Diai - ' + greeting.rusis
          head = (u'<h1>Lietuvos pauk\u0161\u010Diai: %s</h1>' % (greeting.rusis))
          if greeting.raudona:
            raud = "Taip"
          else:
            raud = "Ne"
          aaa=aaa+(u"<tr><td>Burys</td><td>%s</td></tr>\n" % (greeting.burys))
          aaa=aaa+(u"<tr><td>\u0160eima</td><td>%s</td></tr>\n" % (greeting.seima))
          aaa=aaa+(u"<tr><td>R\u016B\u0161is</td><td><strong>%s<strong></td></tr>\n" % (greeting.rusis))
          aaa=aaa+(u"<tr><td>Burys lotin.</td><td>%s</td></tr>\n" % (greeting.buryslot))
          aaa=aaa+(u"<tr><td>\u0160eima lotin.</td><td>%s</td></tr>\n" % (greeting.seimalot))
          aaa=aaa+(u"<tr><td>R\u016B\u0161is lotin.</td><td>%s</td></tr>\n" % (greeting.rusislot))
          aaa=aaa+(u"<tr><td>R\u016B\u0161is angl.</td><td>%s</td></tr>\n" % (greeting.rusisen))
          aaa=aaa+(u"<tr><td>R\u016B\u0161is rus.</td><td>%s</td></tr>\n" % (greeting.rusisru))
          aaa=aaa+(u"<tr><td>Wiki liet.</td><td><a href=\"%s\">Wikipedia liet. - %s</a></td></tr>\n" % ('https://lt.wikipedia.org/wiki/'+greeting.wikiurl,greeting.rusis))
          aaa=aaa+(u"<tr><td>Wiki rus.</td><td><a href=\"%s\">Wikipedia rus. - %s</a></td></tr>\n" % ('https://ru.wikipedia.org/wiki/'+greeting.wikiurlru,greeting.rusisru))
          aaa=aaa+(u"<tr><td>Wiki angl.</td><td><a href=\"%s\">Wikipedia angl. - %s</a></td></tr>\n" % ('https://en.wikipedia.org/wiki/'+greeting.wikiurlen,greeting.rusisen))
          aaa=aaa+(u"<tr><td>Foto</td><td><a href=\"https://www.google.lt/search?num=10&hl=lt&site=imghp&tbm=isch&source=hp&biw=1054&bih=330&q=%s\">Foto</a></td></tr>\n" % (greeting.rusislot))
          aaa=aaa+(u"<tr><td>Foto arialas</td><td><a href=\"https://www.google.lt/search?num=10&hl=lt&site=imghp&tbm=isch&source=hp&biw=1054&bih=330&q=%s\">Foto arialas</a></td></tr>\n" % (greeting.rusislot+' distribution map'))
          aaa=aaa+(u"<tr><td>Video</td><td><a href=\"http://www.youtube.com/results?search_query=%s\">Video</a></td></tr>\n" % (greeting.rusislot))
#          aaa=aaa+(u"<tr><td>Raudonojoje knygoje</td><td>%s</tr>\n" % (raud))
        aaa = aaa + "</tbody></table>\n"
        aaa =head +'<div>'+aaa+"</div>"
        aaa = aaa + ("<p><a href=\"%s\">Back to List</p></a>\n" % ('http://'+os.environ['HTTP_HOST']+os.environ['PATH_INFO']))
    else:
        aaa = aaa + "<br /><table border=\"0\"><tbody>\n"
        aaa=aaa+u"<tr><td>Burys</td><td>\u0160eima</td><td>R\u016B\u0161is</td><td>Wiki</td><td>Foto</td><td>Video</td><td>Info</td></tr>\n"

        greetings = db.GqlQuery("SELECT * "
        						"FROM Pauksciai "
        						"ORDER BY pauksnr ")
        for greeting in greetings:
            aaa=aaa+("<tr><td>%s<br>  (lot. %s)</td><td>%s<br>  (lot. %s)</td><td>%s<br>  (lot. %s)</td><td><a href=\"http://lt.wikipedia.org/wiki/%s\">Wiki</a></td><td><a href=\"https://www.google.lt/search?num=10&hl=lt&site=imghp&tbm=isch&source=hp&biw=1054&bih=330&q=%s\">Foto</a></td><td><a href=\"http://www.youtube.com/results?search_query=%s\">Video</a></td><td><a href=\"%s\">Info</a></td></tr>\n" %
            						(greeting.burys,greeting.buryslot,greeting.seima,greeting.seimalot,greeting.rusis,greeting.rusislot,greeting.wikiurl,urllib.quote(greeting.rusislot),urllib.quote(greeting.rusislot),'http://'+os.environ['HTTP_HOST']+os.environ['PATH_INFO']+"?cmd=1&paukstis="+urllib.quote((greeting.rusis).encode("utf-8"))))
        aaa = aaa + "</tbody></table>\n"
        aaa = u'<h1>Lietuvos pauk\u0161\u010Diai</h1><div>'+aaa+"</div>"
    result['cont']=aaa
    return result

   
