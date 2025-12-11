from peewee import AutoField, Model, CharField, IntegerField, BooleanField
from .db import db


class App(Model):
    app_id = AutoField()
    app_type = CharField()
    app_name = CharField()
    app_time = IntegerField()
    app_day = CharField()
    app_top = BooleanField(default=False)

    class Meta:
        database = db
        table_name = 'app'
