
import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

MAIN_PAGE_FOOTER_TEMPLATE = """\
	<!doctype html>
	<html>
		<body>
			<form action='/sign?%s' method='post' >
				<div><textarea name='content' rows=3 cols=60 ></textarea><div>
				<div><input type='submit' value='firmar' ><div>
			</form>

			<hr>

			<form>Guestbook name:
				<input type='%s' name='Guestbook_name' >
				<input type=submit value='switch' >
			</form>

			<a href='%s' >%s </a>

		</body>
	</html>
"""

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def guestbook_key( guestbook_name=DEFAULT_GUESTBOOK_NAME ):
	return ndb.Key( 'Guestbook', guestbook_name )

class Gretting( ndb.Model ):
	author  = ndb.UserProperty() 
	content	= ndb.StringProperty( indexed=False )
	date 	= ndb.DateTimeProperty( auto_now_add=True )

class MainPage( webapp2.RequestHandler ):

	def get( self ):
		self.response.write( '<html><body>' )
		guestbook_name = self.request.get( 'guestbook_name', 
											DEFAULT_GUESTBOOK_NAME )

		gretting_query = Gretting.query(
			ancestor=guestbook_key(guestbook_name)).order(-Gretting.date)
		grettings =	gretting_query.fetch(10)

		for gretting in grettings:
			if gretting.author:
				self.response.write(
					'<b>%s</b> escribio: ' % gretting.author.nickname() )
			else:
				self.response.write( 'una persona anonima escribio: ' )

			self.response.write( 
				'<blockqoute>%s</blockqoute><br></br>' % cgi.escape( gretting.content ) )

		if users.get_current_user():
			url = users.create_logout_url( self.request.uri ) 
			url_linktext = 'logout'
		else:
			url = users.create_login_url( self.request.uri )
			url_linktext = 'login'

		sign_query_params = urllib.urlencode( {'guestbook_name': guestbook_name} )
		self.response.write( MAIN_PAGE_FOOTER_TEMPLATE %
								(sign_query_params, cgi.escape(guestbook_name),
									url, url_linktext) )

class Guestbook( webapp2.RequestHandler ):

	def post(self):
		guestbook_name = self.request.get( 'guestbook_name',
											DEFAULT_GUESTBOOK_NAME )
		gretting = Gretting(parent=guestbook_key(guestbook_name))

		if users.get_current_user():
			gretting.author = users.get_current_user()

		gretting.content = self.request.get('content')
		gretting.put()

		query_params = { 'guestbook_name': guestbook_name }
		self.redirect('/?' + urllib.urlencode( query_params ) ) 


application = webapp2.WSGIApplication([
	('/', MainPage),
	('/sign', Guestbook),
	], debug=True)
