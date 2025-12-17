from peewee import Model, CharField, AutoField
from .db import db

class User(Model):
    user_id = AutoField(primary_key=True)
    user_name = CharField(unique=True)
    user_password = CharField()

    class Meta:
        database = db