import peewee

# any docker containers importing this file must map the same volume to /sqlite
DATABASE = '/sqlite/sqlite.db'
db = peewee.SqliteDatabase(DATABASE)

class BaseModel(peewee.Model):
	class Meta:
		database = db

class Source(BaseModel):
	"""Represents a source of data that was set up by a user"""
	source_id = peewee.BigAutoField()
	# url where the page can be retrieved
	url = peewee.CharField()
	# selector of the element containin the number
	selector = peewee.CharField()
	# number of seconds to wait between collection attempts
	period = peewee.IntegerField()
	# user entered title
	title = peewee.CharField()


class DataEntry(BaseModel):
	"""Represents a single recorded event from a scraped page"""
	entry_id = peewee.BigAutoField()
	# which source these data are collected from
	source_id = peewee.ForeignKeyField(Source, backref='pets')
	# parsed value scraped from the page
	value = peewee.FloatField()
	# time of last update in epoch seconds
	last_update = peewee.IntegerField()