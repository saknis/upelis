#!/usr/bin/env python
import base64
import cgi
import datetime
import logging
import os
import time
#from datetime import datetime, date, time
import urllib
import wsgiref.handlers
import string



from google.appengine.api import users
from google.appengine.api.logservice import logservice
from google.appengine.ext import db
#from google.appengine.ext import webapp
import webapp2 as webapp


# This sample gets the app request logs up to the current time, displays 5 logs
# at a time, including all AppLogs, with a Next link to let the user "page"
# through the results, using the RequestLog offset property.

class MainPage(webapp.RequestHandler):

  def get(self):
    logging.info('Starting Main handler')
    # Get the incoming offset param from the Next link to advance through
    # the logs. (The first time the page is loaded, there won't be any offset.)
    start_time_set=False
    try:
      offset = self.request.get('offset') or None
      if offset:
        offset = base64.urlsafe_b64decode(str(offset))
    except TypeError:
      offset = None
    try:
      start_time = self.request.get('start_time') or None
      if start_time:
        start_time = float(base64.urlsafe_b64decode(str(start_time)))
        start_time_set=True
    except TypeError:
      start_time = None
      start_time_set=False
    try:
      filter = str(self.request.get('filter')) or None
    except TypeError:
      filter = None

    # Set up end time for our query.

    # Count specifies the max number of RequestLogs shown at one time.
    # Use a boolean to initially turn off visiblity of the "Next" link.
    count = 1000
    show_next = True
    last_offset = 5000

    dt=datetime.datetime.now()
    tt=dt.timetuple()
    year=tt[0]
    month=tt[1]
    ttt=time.strptime((("01 %s %s") % (month,year)), "%d %m %Y") 
    
    if not start_time_set:
      end_time = time.time()
      start_time = time.mktime(ttt)
    else:
      dt2=datetime.datetime.utcfromtimestamp(float(start_time))
      tt2=dt2.timetuple()
      year2=tt2[0]
      month2=tt2[1]
      month2=month2+1
      if month2==13:
        month2=1
        year2=year2+1
      ttt2=time.strptime((("01 %s %s") % (month2,year2)), "%d %m %Y")
      end_time=time.mktime(ttt2)
    dt3=datetime.datetime.utcfromtimestamp(float(start_time))
    tt3=dt3.timetuple()
    year3=tt3[0]
    month3=tt3[1]
    month3=month3-1
    if month3==0:
      month3=12
      year3=year3-1
    ttt3=time.strptime((("01 %s %s") % (month3,year3)), "%d %m %Y")
    start_time_next=time.mktime(ttt3)
    # Iterate through all the RequestLog objects, displaying some fields and
    # iterate through all AppLogs beloging to each RequestLog count times.
    # In each iteration, save the offset to last_offset; the last one when
    # count is reached will be used for the link.
    i = 0
    for req_log in logservice.fetch(start_time=start_time,end_time=end_time, offset=offset,
                                    minimum_log_level=logservice.LOG_LEVEL_INFO,
                                    include_app_logs=False):
      ip=req_log.ip
      status=str(req_log.status)
      if filter and status and not string.find(status, filter) == -1: 
#      self.response.out.write("<br /> REQUEST LOG <br />")
#      self.respons
        self.response.out.write("""%s <br />""" % (req_log.combined))
        i += 1
      else:
        if not filter:
          self.response.out.write("""%s <br />""" % (req_log.combined))
          i += 1
#      self.response.out.write("""IP: %s <br /> Method: %s <br />
#                       Resource: %s <br />""" % (req_log.ip,
#                       req_log.method, req_log.resource))
#      self.response.out.write("Date: "+datetime.datetime.fromtimestamp(req_log.end_time).strftime('%D %T UTC') +"<br />")

      last_offset= req_log.offset
      

      for app_log in req_log.app_logs:
        self.response.out.write("<br />APP LOG<br />")
        statslink = ("<a href=\"http://%s/stats/details?time=%s\">%s</a>" % (os.environ['HTTP_HOST'], app_log.time,app_log.time))
        self.response.out.write("<br />STATS DETAILS: %s<br />" % (statslink))
        self.response.out.write("Date: "+datetime.datetime.fromtimestamp(app_log.time).strftime('%Y-%m-%d %H:%M:%S UTC') +"<br />")
        self.response.out.write("<br />Message: "+app_log.message+"<br />")

      if i >= count:
        show_next = True
        break

    # Prepare the offset URL parameters, if any.
    if show_next:
      query = self.request.GET
      query['offset'] = base64.urlsafe_b64encode(last_offset)
      query['start_time'] = base64.urlsafe_b64encode(("%s")%(start_time_next))
      next_link = urllib.urlencode(query)
      self.response.out.write("<a href=\"/logs4?"+next_link+"\">Next</a>")
      self.response.out.write("<br />")


#def main():
logging.getLogger().setLevel(logging.DEBUG)

app = webapp.WSGIApplication([
      ('/logs4', MainPage),
      ], debug=True)
#  wsgiref.handlers.CGIHandler().run(application)


#if __name__ == '__main__':
#  main()