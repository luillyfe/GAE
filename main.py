
from google.appengine.api import users
import webapp2

class Gretting( webapp2.RequestHandler ):
	def get( self ):
		user = users.get_current_user()

		if user:
			gretting = ('hola soy %s<br> (<a href=%s >Salir</a>)' %
							(user.nickname(), users.create_logout_url('/')))
		else:
			gretting = ('hola no estoy logueado<br> (<a href=%s >Ingresar</a>)' %
							users.create_login_url('/'))

		self.response.write( gretting+'<br>' )
		self.response.write( self.request.uri )



application = webapp2.WSGIApplication([
	('/', Gretting),
	], debug=True)
