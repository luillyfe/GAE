
import cgi
import datetime
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import users


class Greeting(db.Model):
    """Models a Guestbook entry with an author, content, avatar, and date."""
    author = db.StringProperty()
    content = db.StringProperty(multiline=True)
    avatar = db.BlobProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>')
        greetings = Greeting.all()

        for greeting in greetings:
            #self.response.headers['Content-Type'] = 'image/jpg'
            #self.response.out.write( greeting.avatar )
            self.response.out.write('<div><img src="img?img_id=%s"></img>' %
                                    greeting.key())
        self.response.out.write('</body></html>')


class Image(webapp2.RequestHandler):
    def get(self):
        greeting = db.get(self.request.get('img_id'))
        if greeting.avatar:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(greeting.avatar)
        else:
            self.response.out.write('No image')


class Guestbook(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name')
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = users.get_current_user().nickname()

        greeting.content = self.request.get('content')
        avatar = images.resize(self.request.get('img'), 32, 32)
        greeting.avatar = db.Blob(avatar)
        greeting.put()
        self.redirect('/?' + urllib.urlencode(
            {'guestbook_name': guestbook_name}))


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/img', Image),
                               ('/sign', Guestbook)],
                              debug=True)