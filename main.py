
import webapp2

class MainPage( webapp2.RequestHandler ):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.write( 'Hola, Fermin.' )


# El controlador MainPage se hace cargo	de las peticiones a 
# la raiz (/) del dominio en este caso es localhost
application = webapp2.WSGIApplication([
	('/', MainPage),
], debug=True)