from peewee import AutoField, Model, CharField, IntegerField, BooleanField, ForeignKeyField
from .db import db
from .user import User


class App(Model):
    app_id = AutoField()
    user = ForeignKeyField(User, backref='apps', null=True)
    app_type = CharField()
    app_name = CharField()
    app_time = IntegerField()
    app_day = CharField()
    app_top = BooleanField(default=False)

    class Meta:
        database = db
        table_name = 'app'
