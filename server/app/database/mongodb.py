import os
import certifi

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set")

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)

db = client[MONGO_DB_NAME]

repositories_collection = db["repositories"]
code_chunks_collection = db["code_chunks"]