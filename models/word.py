from peewee import *

db = SqliteDatabase('word.db')


class Word(Model):
    content = CharField()
    user_id = CharField()

    class Meta:
        database = db
