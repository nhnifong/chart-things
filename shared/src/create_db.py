import peewee
from schema import Source, DataEntry, DATABASE

db = peewee.SqliteDatabase(DATABASE)

db.connect()
db.create_tables([Source, DataEntry])

db.close()
