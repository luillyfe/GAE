
# -*- coding: utf-8 -*-
import os
import urllib
import cgi

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from datetime import datetime, date, time

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

def isUser(self):
		if users.get_current_user():
			url = users.create_logout_url( self.request.uri )
			url_linktext = 'Salir'

		else:
			url = users.create_login_url( self.request.uri )
			url_linktext = 'Ingresar'

		values = { 'url' : url, 'url_linktext' : url_linktext, }

		return values


rolValues = ["candidato para intercambio", "participante extranjero", "voluntario"]
class Person( db.Model ):
	name 	 		= db.StringProperty(required=True)
	lastname 		= db.StringProperty(required=True)
	neighborhood 	= db.StringProperty()
	school   		= db.StringProperty(required=True)
	grade   	 	= db.StringProperty()
	landline 		= db.StringProperty()
	cellPhone 		= db.StringProperty()
	# Porque la propiedad db.emailProperty no me permite un valor vacio
	email 	 		= db.StringProperty()
	address  		= db.StringProperty(multiline=True)
	picture  		= blobstore.BlobReferenceProperty()
	rol 			= db.StringProperty(choices=set(rolValues))


class Meeting( db.Model ):
	name 			= db.StringProperty(required=True)
	datetime_create = db.DateTimeProperty(auto_now_add=True)
	datetime_begin  = db.DateTimeProperty(required=True)
	datetime_end	= db.DateTimeProperty()
	location		= db.StringProperty()
	details			= db.StringProperty(multiline=True)


class PersonForMeeting( db.Model ):
	meeting 	= db.ReferenceProperty( Meeting )
	person 		= db.ReferenceProperty( Person )
	invited 	= db.BooleanProperty()
	attended 	= db.BooleanProperty()

		
class MainPage( webapp2.RequestHandler ):
	def get(self):
		values = isUser(self)

		template = JINJA_ENVIRONMENT.get_template( "app/views/layout.afs" )
		self.response.write( template.render(values) )


class NewNominee( webapp2.RequestHandler ):
	def get(self):
		upload_url = blobstore.create_upload_url('/nominees/')
		values = isUser(self)
		values['upload_url'] = upload_url
		values['rolValues']  = rolValues
						
		template = JINJA_ENVIRONMENT.get_template( 'app/views/nominees/new.afs' )
		self.response.write( template.render(values) )


class ShowNominee( webapp2.RequestHandler ):
	def get(self, resource):
		values = isUser(self)

		try: 
			person = Person.get(urllib.unquote(resource))
			if person:
				values['person'] = person
				view = 'app/views/nominees/show.afs'	
			else: view = 'app/views/not_found.afs'

		except: view = 'app/views/not_found.afs'

		template = JINJA_ENVIRONMENT.get_template( view )
		self.response.write( template.render(values) )


class EditNominee( blobstore_handlers.BlobstoreUploadHandler ):
	def get(self, resource):
		person = Person.get(urllib.unquote(resource))
		upload_url = blobstore.create_upload_url('/nominees/update')
		
		values = isUser(self)
		values['person'] = person
		values['upload_url'] = upload_url
		values['rolValues']  = rolValues

		template = JINJA_ENVIRONMENT.get_template( 'app/views/nominees/edit.afs' )
		self.response.write( template.render(values) )

	def post(self):
		person = Person.get(cgi.escape(self.request.get('key')))

		person.name 	  = cgi.escape(self.request.get('name'))
		person.lastname  = cgi.escape(self.request.get('lastname'))
		person.neighborhood = cgi.escape(self.request.get('neighborhood'))
		person.school    = cgi.escape(self.request.get('school'))
		person.grade     = cgi.escape(self.request.get('grade'))
		person.landline  = cgi.escape(self.request.get('landline'))
		person.cellPhone = cgi.escape(self.request.get('cellPhone'))
		person.email 	  = cgi.escape(self.request.get('email'))
		person.rol 	  = cgi.escape(self.request.get('rol'))
		person.address   = cgi.escape(self.request.get('address')).strip()

		if self.get_uploads('file'):
			person.picture = self.get_uploads('file')[0].key()

		person.put()
		self.redirect( '/nominees/' )


class DeleteNominee( webapp2.RequestHandler ):
	def get(self, resource):
		person = db.get(urllib.unquote(resource))

		person.delete()

		self.redirect( '/nominees/' )


class Nominee( blobstore_handlers.BlobstoreUploadHandler ):
	def get(self):
		persons = db.Query(Person)

		values = isUser(self)	
		values['persons'] = persons
		template = JINJA_ENVIRONMENT.get_template( 'app/views/nominees/index.afs' )
		self.response.write( template.render(values) )

	def post(self):
		name 	  = cgi.escape(self.request.get('name'))
		lastname  = cgi.escape(self.request.get('lastname'))
		neighborhood = cgi.escape(self.request.get('neighborhood'))
		school    = cgi.escape(self.request.get('school'))
		grade     = cgi.escape(self.request.get('grade'))
		landline  = cgi.escape(self.request.get('landline'))
		cellPhone = cgi.escape(self.request.get('cellPhone'))
		email 	  = cgi.escape(self.request.get('email'))
		address   = cgi.escape(self.request.get('address')).strip()
		rol 	  = cgi.escape(self.request.get('rol'))
		picture   = ''

		if self.get_uploads('file'):
			picture = self.get_uploads('file')[0].key()
		
			person = Person(name=name, lastname=lastname, email=email, rol=rol, 
				neighborhood=neighborhood, school=school, address=address, 
				grade=grade, landline=landline, cellPhone=cellPhone, picture=picture)

		else: person = Person(name=name, lastname=lastname, email=email, rol=rol, 
				neighborhood=neighborhood, school=school, address=address, 
				grade=grade, landline=landline, cellPhone=cellPhone)
		person.put()

		self.redirect( '/nominees/' )

		
class ServeBlob( blobstore_handlers.BlobstoreDownloadHandler ):
    def get(self, resource):
    	try: person = db.get(urllib.unquote(resource))
        except: person = Person()

    	try: person.picture.key()

    	except:
    		persons = Person.all() 
    		person = persons.filter('name =', 'default')[0] 

    	self.send_blob( person.picture.key() )


class NewMeeting( webapp2.RequestHandler ):
	def get(self):
		upload_url = blobstore.create_upload_url('/meetings/new')
		values = isUser(self)
		values['upload_url'] = upload_url
						
		template = JINJA_ENVIRONMENT.get_template( 'app/views/meetings/new.afs' )
		self.response.write( template.render(values) )

	def post(self):
		name = cgi.escape(self.request.get('name'))
		
		date_begin = cgi.escape(self.request.get('date_begin'))
		time_begin = cgi.escape(self.request.get('time_begin'))
		datetime_begin = datetime.strptime(date_begin +' '+time_begin, "%Y-%m-%d %H:%M")

		date_end = cgi.escape(self.request.get('date_end'))
		time_end = cgi.escape(self.request.get('time_end'))
		datetime_end = datetime.strptime(date_end +' '+time_end, "%Y-%m-%d %H:%M")
		
		location = cgi.escape(self.request.get('location'))
		details  = cgi.escape(self.request.get('details'))

		meeting = Meeting(name=name, datetime_begin=datetime_begin, 
			datetime_end=datetime_end, location=location, details=details)
		
		meeting.put()
		self.redirect( '/meetings/' )


class Meetings( webapp2.RequestHandler ):
	def get(self):
		meetings = Meeting.all()

		values = isUser(self)	
		values['meetings'] = meetings
		template = JINJA_ENVIRONMENT.get_template( 'app/views/meetings/index.afs' )
		self.response.write( template.render(values) )


class ShowMeeting( webapp2.RequestHandler ):
	def get(self, resource):
		values 	= isUser(self)

		meeting = Meeting.get( urllib.unquote( resource ) )		
		values['meeting'] = meeting
 
		pxms = PersonForMeeting.all()
		pxms.filter('meeting =', meeting.key())
		values['pxms'] = pxms
		
		template = JINJA_ENVIRONMENT.get_template( 'app/views/meetings/show.afs' )
		self.response.write( template.render( values ) )


class EditMeeting( webapp2.RequestHandler ):
	def get( self, resource ):
		values 		= isUser(self)

		meeting 	= Meeting.get( urllib.unquote( resource ) )
		upload_url 	= blobstore.create_upload_url( '/meetings/update/' )
		nominees    = Person.all()
		
		values['meeting'] 	 = meeting
		values['upload_url'] = upload_url
		values['nominees']   = nominees

		template = JINJA_ENVIRONMENT.get_template( 'app/views/meetings/edit.afs' )
		self.response.write( template.render( values ) )


class UpdateMeeting( webapp2.RequestHandler ):
	def post( self ):
		meeting = Meeting.get(cgi.escape(self.request.get('key')))

		meeting.name 		= cgi.escape( self.request.get('name') )
		meeting.location 	= cgi.escape( self.request.get('location') )
		meeting.details 	= cgi.escape( self.request.get('details') )

		date_begin 	= cgi.escape( self.request.get('date_begin') )
		time_begin 	= cgi.escape( self.request.get('time_begin') )
		meeting.datetime_begin = datetime.strptime(date_begin +' '+time_begin, "%Y-%m-%d %H:%M:%S")

		date_end 	= cgi.escape( self.request.get('date_end') )
		time_end 	= cgi.escape( self.request.get('time_end') )
		meeting.datetime_end = datetime.strptime(date_end +' '+time_end, "%Y-%m-%d %H:%M:%S")		

		meeting.put()

		guests  = self.request.get_all('invited[]')
		
		for guest in guests:
			#It's important to scape special characters here?
			person 	= Person.get(db.Key(encoded=guest))
			pxms 	= PersonForMeeting.all()
			pxms.filter( 'meeting =', meeting.key() )
			
			#If the person already exist do nothing
			if pxms.filter( 'person =', person.key() ).count():
				pass

			else: 
				pxm    = PersonForMeeting(person=person.key(), meeting=meeting.key(), 
						invited=True )
				pxm.put()
				
		self.redirect( '/meetings/' )


class MeetingNominee( webapp2.RequestHandler ):
	def get(self):
		values = isUser(self)
		values['nominees'] = nominees = Person.all()

		template = JINJA_ENVIRONMENT.get_template( 'app/views/meetings/nominees.afs' )
		self.response.write( template.render( values ) )


class DeleteMeeting( webapp2.RequestHandler ):
	def get( self, resource ):
		meeting = Meeting.get( urllib.unquote( resource ) )
		meeting.delete()

		self.redirect( '/meetings/' )


class OnlyOne( blobstore_handlers.BlobstoreUploadHandler ):
	def get(self):
		"""persons = Person.all()
		
		for person in persons:
			person.rol = rolValues[0]
			person.put()

		self.response.write( 'OK again' )"""
		values = { 'upload_url' : blobstore.create_upload_url('/nominees/only') }
		template = JINJA_ENVIRONMENT.get_template( 'app/views/nominees/onlyone.afs' )
		self.response.write( template.render(values) )

	def post(self):
		person = Person(name='default', lastname='default', school='default', 
			address='default', picture=self.get_uploads('file')[0].key())
		person.put()
		self.redirect( '/nominees/' )


""" Definicion de una aplicacion WSGI """
application = webapp2.WSGIApplication([
		(	'/', 					MainPage),
		('/nominees/new', 			NewNominee),
		('/nominees/',	 			Nominee),
		('/nominees/([^/]+)?/delete',		DeleteNominee),
		('/nominees/update',		EditNominee),
		('/nominees/only', 			OnlyOne),
		('/nominees/([^/]+)?', 		ShowNominee),
		('/nominees/([^/]+)?/edit',	EditNominee),
		('/nominees/img/([^/]+)?', 	ServeBlob),
		('/meetings/new',			NewMeeting),
		('/meetings/',				Meetings),
		('/meetings/update/',		UpdateMeeting),
		('/meetings/nominees',		MeetingNominee),
		('/meetings/([^/]+)?',		ShowMeeting),
		('/meetings/([^/]+)?/edit',	EditMeeting),
		('/meetings/([^/]+)?/delete',	DeleteMeeting),		
	], debug=True)
