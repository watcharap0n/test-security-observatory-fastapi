from typing import Optional
from pymongo import MongoClient
import pymongo


class MongoDB:
    def __init__(
            self, database_name, client
    ):
        self.client = client
        self.database = self.client[database_name]

    def database_config(self):
        return self.database

    def get_collection_names(self):
        return self.database.list_collection_names()

    @staticmethod
    def find_dictionary(programming, query):
        return programming.find(query)

    async def find_one(self, collection: str, query: dict, remove_field: Optional[dict] = None):
        return self.database[collection].find_one(query, remove_field)

    async def find_one_lasted(self, collection: str, query: dict):
        return self.database[collection].find_one(
            query, sort=[("_id", pymongo.DESCENDING)]
        )

    async def aggregate(self, collection: str, key: str, value: Optional[str] = None):
        return self.database[collection].aggregate([
            {'$group': {'_id': key, 'count': {'$sum': 1}}},
            {'$match': {'_id': {'$ne': value}, 'count': {'$gt': 1}}},
            {'$project': {'name': '$_id', '_id': 0}}
        ])

    async def find(self, collection: str, query: dict, quantity: Optional[dict] = None):
        return self.database[collection].find(query, quantity)

    async def insert_one(self, collection: str, data: dict):
        try:
            result = self.database[collection].insert_one(data)
            return result.inserted_id
        except Exception as e:
            print(str(e))

    async def insert_many(self, collection: str, data: list):
        try:
            result = self.database[collection].insert_many(data)
            return result.inserted_ids
        except Exception as e:
            print(str(e))

    async def update_many(self, collection: str, query: dict, values):
        try:
            self.database[collection].update_many(query, values)
        except Exception as e:
            print(str(e))

    async def update_one(self, collection: str, query: dict, values):
        try:
            return self.database[collection].update_one(query, values).modified_count
        except Exception as e:
            print(str(e))

    async def delete_one(self, collection: str, query: dict):
        try:
            return self.database[collection].delete_one(query).deleted_count
        except Exception as e:
            print(str(e))

    async def delete_many(self, collection: str, query: dict):
        try:
            self.database[collection].delete_many(query).deleted_count
        except Exception as e:
            print(str(e))
