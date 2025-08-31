import os
import socket

import peewee
import peewee_async

from dotenv import load_dotenv


load_dotenv()

# Force IPv4 resolution for the database host
def force_ipv4_resolution(hostname):
    """Resolve hostname to IPv4 address only"""
    try:
        # Get IPv4 address for the hostname
        ipv4_addr = socket.getaddrinfo(hostname, None, socket.AF_INET)[0][4][0]
        return ipv4_addr
    except Exception:
        return hostname

DATABASE_HOST = os.getenv("DATABASE_HOST")
# Try to resolve to IPv4 if possible
if DATABASE_HOST:
    DATABASE_HOST = force_ipv4_resolution(DATABASE_HOST)

# Extract endpoint ID from Neon hostname for SNI support
ENDPOINT_ID = None
if DATABASE_HOST and "neon.tech" in os.getenv("DATABASE_HOST", ""):
    # Extract endpoint ID from hostname like "ep-rapid-cell-a2y2fcad-pooler.eu-central-1.aws.neon.tech"
    hostname_parts = os.getenv("DATABASE_HOST").split("-")
    if len(hostname_parts) >= 4 and hostname_parts[0] == "ep":
        ENDPOINT_ID = f"ep-{hostname_parts[1]}-{hostname_parts[2]}-{hostname_parts[3]}"


db = peewee_async.PooledPostgresqlDatabase(
    database=os.getenv("DATABASE_NAME"),
    user=os.getenv("DATABASE_USER"),
    password=os.getenv("DATABASE_PASSWORD"),
    host=DATABASE_HOST,
    port=os.getenv("DATABASE_PORT"),
    sslmode='require',
    # Add endpoint ID for Neon SNI support
    options=f'endpoint={ENDPOINT_ID}' if ENDPOINT_ID else None,
    # Add connection parameters for better reliability
    connect_timeout=10,
    keepalives_idle=600,
    keepalives_interval=30,
    keepalives_count=3,
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
