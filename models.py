from google.appengine.ext import ndb


class Message(ndb.Model):
    text = ndb.TextProperty(required=True)
    email = ndb.StringProperty()
    name = ndb.StringProperty(default="Anonymous")
    created = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default=False)
