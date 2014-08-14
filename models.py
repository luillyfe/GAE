
# -*- coding: utf-8 -*-
# Aqui reposan los modelos que utilizara la aplicacion para 
# soportar cada una de sus funcionalidades

from google.appengine.ext import ndb
from google.appengine.api import users

class UserApp( ndb.Model ):
	"""Modela un usuario de la aplicación."""
	user 	 = ndb.UserProperty()
	name 	 = ndb.StringProperty()
	lastname = ndb.StringProperty()


class Greeting(ndb.Model):
    """Modela una entrada individual en el libro de invitados."""
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

