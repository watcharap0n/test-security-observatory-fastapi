"""
database and authentication master
    - mongodb
    - firebase realtime
    - firebase admin (authentication)

"""

import os
from .database import MongoDB
from .object_str import CutId, PyObjectId
from pymongo import MongoClient

client = MongoClient(
    host=os.getenv('MONGODB_URI', 'mongodb://localhost:27018'),
    username=os.getenv('MONGO_INITDB_USERNAME', None),
    password=os.getenv('MONGO_INITDB_PASSWORD', None)
)

db = MongoDB(
    database_name="DB",
    client=client
)


def generate_token(engine):
    """

    :param engine:
    :return:
    """
    obj = CutId(_id=engine)
    Id = obj.dict()["id"]
    return Id
