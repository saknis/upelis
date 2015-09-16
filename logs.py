#!/usr/bin/env python
import base64
import cgi
import datetime
import logging
import os
import time
import urllib
import wsgiref.handlers
#import locale



from google.appengine.api import users
from google.appengine.api.logservice import logservice
from google.appengine.ext import db
#from google.appengine.ext import webapp
import webapp2 as webapp

#locale.setlocale(locale.LC_ALL, 'lt_lt')
#locale.setlocale(locale.LC_ALL, "lt")


# This sample gets the app request logs up to the current time, displays 5 logs
# at a time, including all AppLogs, with a Next link to let the user "page"
# through the results, using the RequestLog offset property.

class MainPage(webapp.RequestHandler):

  def get(self):
    logging.info('Starting Main handler')
    # Get the incoming offset param from the Next link to advance through
    # the logs. (The first time the page is loaded, there won't be any offset.)
    try:
      offset = self.request.get('offset') or None
      if offset:
        offset = base64.urlsafe_b64decode(str(offset))
    except TypeError:
      offset = None

    # Set up end time for our query.
    end_time = time.time()

    # Count specifies the max number of RequestLogs shown at one time.
    # Use a boolean to initially turn off visiblity of the "Next" link.
    count = 500
    show_next = True
    last_offset = None
    url_map_entry = None

    # Iterate through all the RequestLog objects, displaying some fields and
    # iterate through all AppLogs beloging to each RequestLog count times.
    # In each iteration, save the offset to last_offset; the last one when
    # count is reached will be used for the link.
    i = 0
    for req_log in logservice.fetch(end_time=end_time, offset=offset,
                                    minimum_log_level=logservice.LOG_LEVEL_INFO,
                                    include_app_logs=True):

      self.response.out.write("<br /> REQUEST LOG <br />\n")
#      self.respons

#      self.response.out.write("Date: " + datetime.datetime.fromtimestamp(req_log.end_time).strftime('%D %T UTC') + " <br />\n")
      self.response.out.write("Date: " + datetime.datetime.fromtimestamp(req_log.end_time).strftime('%H:%M:%S %Y-%m-%d UTC') + " <br />\n")
#      if req_log.url_map_entry:
#        self.response.out.write((""" <a href=\"%s\">%s</a><br />\n""" % (req_log.url_map_entry, req_log.offset)))
#      else:
#        self.response.out.write(" <br />\n")
      self.response.out.write("""%s <br />\n""" % (req_log.combined))
#      self.response.out.write("""IP: %s <br /> Method: %s <br />
#                       Resource: %s <br />""" % (req_log.ip,
#                       req_log.method, req_log.resource))
#      self.response.out.write("Date: "+datetime.datetime.fromtimestamp(req_log.end_time).strftime('%D %T UTC') +"<br />")

      last_offset= req_log.offset
      i += 1

      for app_log in req_log.app_logs:
        self.response.out.write("APP LOG<br />\n")
#        self.response.out.write("Date: "+datetime.datetime.fromtimestamp(app_log.time).strftime('%D %T UTC') +"<br />\n")
        self.response.out.write("Date: "+datetime.datetime.fromtimestamp(app_log.time).strftime('%H:%M:%S %Y-%m-%d UTC') +"<br />\n")
        self.response.out.write("Message: "+app_log.message+"<br />\n")
        messagetxt = app_log.message
        messarray = messagetxt.split("; ")
        for messvalue in messarray:
           messvalue2=messvalue.split(": ")
           mess = {}
           if len(messvalue2)>1:
             [key,val]=messvalue2[:2]
             mess[key]=val
             if 'link' in mess:
               statslink = ("<a href=\"%s\">%s</a>" % (mess['link'],mess['link']))
               self.response.out.write("<br />STATS DETAILS: %s<br />" % (statslink))
           
      if i >= count:
        show_next = True
        break
    self.response.out.write("<br />\n")
    
    # Prepare the offset URL parameters, if any.
    if show_next:
      query = self.request.GET
      query['offset'] = base64.urlsafe_b64encode(last_offset)
      next_link = urllib.urlencode(query)
      self.response.out.write("<a href=\"/logs?"+next_link+"\">Next</a>")
      self.response.out.write("<br />\n")


#def main():
logging.getLogger().setLevel(logging.DEBUG)

app = webapp.WSGIApplication([
      ('/logs', MainPage),
      ], debug=True)
#  wsgiref.handlers.CGIHandler().run(application)


#if __name__ == '__main__':
#  main()