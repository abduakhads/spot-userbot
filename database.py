import os

import peewee
import peewee_async

from dotenv import load_dotenv


load_dotenv()


db = peewee_async.PooledPostgresqlDatabase(
    database=os.getenv("DATABASE_NAME"),
    user=os.getenv("DATABASE_USER"),
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_HOST"),
    port=os.getenv("DATABASE_PORT"),
    sslmode='require',
    channel_binding='require',
)


class BaseModel(peewee_async.AioModel):
    class Meta:
        database = db


class User(BaseModel):
    id = peewee.BigIntegerField(primary_key=True)

    class Meta:
        table_name = "users"


class Group(BaseModel):
    id = peewee.BigIntegerField(primary_key=True)
    user = peewee.ForeignKeyField(
        User,
        backref="groups",
        on_delete="CASCADE"
    )

    class Meta:
        table_name = "groups"
