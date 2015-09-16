from google.appengine.ext import db  

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

