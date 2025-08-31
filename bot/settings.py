import os
import logging

from dotenv import load_dotenv


load_dotenv()


logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


BOT_TOKEN = os.getenv("BOT_TOKEN")
USE_WEBHOOK = eval(os.getenv("USE_WEBHOOK", "False"))
DEVELOPER_ID = os.getenv("DEVELOPER_ID")

WEB_SERVER_HOST = "127.0.0.1" if USE_WEBHOOK else None
WEB_SERVER_PORT = 8080 if USE_WEBHOOK else None
WEBHOOK_PATH = "/webhook" if USE_WEBHOOK else None
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET") if USE_WEBHOOK else None
BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL") if USE_WEBHOOK else None