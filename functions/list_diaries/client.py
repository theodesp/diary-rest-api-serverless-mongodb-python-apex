import os
from pymongo import MongoClient

__all__ = ["db"]

client = MongoClient("mongodb://{}:{}@{}:35243/diary".format(
    os.environ['DB_USER'], 
    os.environ['DB_PASS'], 
    os.environ['DB_HOST']))

# Set database
db = client.get_database()
