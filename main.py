
# -*- coding: utf-8 -*-
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
import models


# 
JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

# Una costante que representa el nombre del libro
DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
	"""Construye una clave de Datastore para una entidad Guestbook con guestbook_name."""
	return ndb.Key('Guestbook', guestbook_name)


# Las clases que heredan de RequestHandler se encargan de procesar
# la solicitud y construir una respuesta. 
class MainPage( webapp2.RequestHandler ):
	
	def get(self):
		self.response.write('<html><body>')
		guestbook_name = 'guestbook_name'

		# Las consultas Ancestor, como se muestra quí, tienen consistencia fuerte
		# con el Hight Replication Datastore. Las consultas que abarcan grupos de
		# entidades son eventualmente consistentes. Si omitimos el Ancestor de 
		# esta consulta habría una ligera propabilidad de que el saludo que acaba 
		# de ser escrito no se presente en una consulta.
		greetings_query = models.Greeting.query(
			ancestor=guestbook_key(guestbook_name)).order(-models.Greeting.date)
		greetings = greetings_query.fetch(10)
		
		for greeting in greetings:
			if greeting.author:
				self.response.write(
					'<b>%s</b> escribío:'.decode('utf-8') % greeting.author.nickname())
			else:
				self.response.write( 'Un anonimo escribío:'.decode('utf-8') )
			self.response.write('<blockquote>%s</blockquote>' % greeting.content)
		
		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
		
		template_values = {
			'greetings': greetings,
			'guestbook_name': urllib.quote_plus(guestbook_name),
			'url': url,
			'url_linktext': url_linktext, 
		}
		template = JINJA_ENVIRONMENT.get_template('/app/views/index.html')
		self.response.write(template.render(template_values))

	def post(self):
    	# Fijamos la misma clave padre en el 'Saludo' para garantizar que cada
    	# Saludo esta en el mismo gurpo de entidades. Las consultas a través 
    	# del grupo de entidades individuales seran consistentes. Sin embargo,
    	# la tasa de escritura para un grupo de entidades individuales debera 
    	# limitarse a ~1/segundo.
		guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)
		greeting = models.Greeting( parent=guestbook_key(guestbook_name) )

		if users.get_current_user(): 
			greeting.author = users.get_current_user()
		
		greeting.content = self.request.get('content')
		greeting.put()
		
		query_params = {'guestbook_name': guestbook_name}
		self.redirect('/?' + urllib.urlencode(query_params))
		

# Una instancia de WSGIAplication que dirige las solicitudes entrantes 
# a un controlador basado en la URL
application = webapp2.WSGIApplication([
	('/', 		MainPage),
	('/sign', 	MainPage),
], debug=True)
