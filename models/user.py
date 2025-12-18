from peewee import AutoField, Model, CharField
from .db import db


class User(Model):
    user_id = AutoField()
    user_name = CharField(unique=True)
    user_password = CharField()

    class Meta:
        database = db
        table_name = 'user'