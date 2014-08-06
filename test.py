
import webapp2

class Main( webapp2.RequestHandler ):
	def get(self):
		self.response.write('hola')

	def put(self):
		self.response.write( 'funciono!!' )

"""def post(self):
		picture = self.get_uploads('file')[0]

		self.redirect( '/users/img/%s' % picture.key() )"""





application = webapp2.WSGIApplication([
	webapp2.Route('/', handler=Main, handler_method='put'),
	], debug=True)