
# -*- coding: utf-8 -*-
import os
import urllib
import cgi

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)


def isUser(self):
		if users.get_current_user():
			url = ['users/nominee', 'users/register',
				users.create_logout_url( self.request.uri )]
			url_linktext = ['Envio', 'Registrar', 'Salir']

		else:
			url = ['', '',  users.create_login_url( self.request.uri )]
			url_linktext = ['', '', 'Ingresar']

		values = { 'url' : url, 'url_linktext' : url_linktext, }

		return values


class Person( db.Model ):
	name 	 = db.StringProperty(required=True)
	lastname = db.StringProperty(required=True)
	neighborhood = db.StringProperty()
	school   = db.StringProperty(required=True)
	grade    = db.StringProperty()
	landline = db.StringProperty()
	cellPhone = db.StringProperty()
	# Porque la propiedad db.emailProperty no me permite un valor vacio
	email 	 = db.StringProperty()
	address  = db.StringProperty()
	picture  = blobstore.BlobReferenceProperty()


class MainPage( webapp2.RequestHandler ):
	def get(self):
		values = isUser(self)

		template = JINJA_ENVIRONMENT.get_template( "app/views/layout.afs" )
		self.response.write( template.render(values) )


class Register( webapp2.RequestHandler ):
	def get( self ):
		upload_url = blobstore.create_upload_url('/users/Nominee')
		values = isUser(self)
		values['upload_url'] = upload_url

		template = JINJA_ENVIRONMENT.get_template( 'app/views/users/register.afs' )
		self.response.write( template.render(values) )


class Nominee( blobstore_handlers.BlobstoreUploadHandler ):
	def get(self):
		persons = Person.all()
		
		values = isUser(self)	
		values['persons'] = persons
		template = JINJA_ENVIRONMENT.get_template( 'app/views/users/nominee.afs' )
		self.response.write( template.render(values) )

	def post( self ):
		name 	  = cgi.escape(self.request.get('name'))
		lastname  = cgi.escape(self.request.get('lastname'))
		neighborhood = cgi.escape(self.request.get('neighborhood'))
		school    = cgi.escape(self.request.get('school'))
		grade     = cgi.escape(self.request.get('grade'))
		landline  = cgi.escape(self.request.get('landline'))
		cellPhone = cgi.escape(self.request.get('cellPhone'))
		email 	  = cgi.escape(self.request.get('email'))
		address   = cgi.escape(self.request.get('address'))
		picture   = self.get_uploads('file')

		if picture:
			picture = picture[0].key()
		
			person = Person(name=name, lastname=lastname, email=email, 
				neighborhood=neighborhood, school=school, address=address, 
				grade=grade, landline=landline, cellPhone=cellPhone, picture=picture)

		else: person = Person(name=name, lastname=lastname, email=email, 
				neighborhood=neighborhood, school=school, address=address, 
				grade=grade, landline=landline, cellPhone=cellPhone)
		person.put()

		self.redirect( '/users/Nominee'  )
	"""def post(self):
		picture = self.get_uploads('file')[0]

		self.redirect( '/users/img/%s' % picture.key() )"""


class Show( webapp2.RequestHandler ):
	def get(self, resource):
		values = isUser(self)
		person = ''

		try: person = Person.get(urllib.unquote(resource))
		except: view = ''

		if person:
			values['person'] = person
			view = 'app/views/users/show.afs'
		else: view = 'app/views/not_found.afs'

		template = JINJA_ENVIRONMENT.get_template( view )
		self.response.write( template.render(values) )

		
class ServeBlob( blobstore_handlers.BlobstoreDownloadHandler ):
    def get(self, resource):
    	try: person = db.get(urllib.unquote(resource))
        except: person = ''

    	if person.picture:
    		self.send_blob(person.picture.key())
    	else: self.send_blob('hipJSqDGbFwkr0UYB-lgHQ==')





application = webapp2.WSGIApplication([
	('/', MainPage),
	('/users/register', Register),
	('/users/nominee', Nominee),
	('/users/([^/]+)?', Show),
	('/users/img/([^/]+)?', ServeBlob),
	], debug=True)
