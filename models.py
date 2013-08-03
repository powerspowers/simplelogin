from google.appengine.ext import db
  
class SimpleAccount(db.Model):
    dateCreated = db.DateTimeProperty(auto_now_add=True)
    simpleid = db.StringProperty()
    password = db.StringProperty()
    emailLower = db.StringProperty()
    firstName = db.StringProperty()
    lastName = db.StringProperty()

