import peewee
from dotenv import load_dotenv
import os

load_dotenv()

db = peewee.PostgresqlDatabase(
    os.getenv("DATABASE_NAME"),
    user=os.getenv("DATABASE_USER"),
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_HOST"),
    port=os.getenv("DATABASE_PORT"),
)


from playhouse.migrate import PostgresqlMigrator, migrate

migrator = PostgresqlMigrator(db)

migrate(
    migrator.add_column('groups', 'kick_bot', peewee.BooleanField(default=False)),
    migrator.add_column('groups', 'delete_message', peewee.BooleanField(default=False)),
)