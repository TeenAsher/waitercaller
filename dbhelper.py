import pymongo
from bson.objectid import ObjectId

DATABASE = "waitercaller"

class DBHelper:

    def __init__(self):
        client = pymongo.MongoClient('localhost', 27017)
        self.db = client[DATABASE]

    def get_user(self, email):
        return self.db.users.find_one({"email": email})

    def add_user(self, email, password):
        self.db.users.insert_one({"email": email, "password": password})

    def add_table(self, number, owner):
        result = self.db.tables.insert_one({"number": number, "owner": owner})
        new_id = result.inserted_id
        return new_id

    def update_table(self, _id, url):
        self.db.tables.update_one({"_id": _id}, {"$set": {"url": url}})

    def get_tables(self, owner_id):
        return list(self.db.tables.find({"owner": owner_id}))

    def get_table(self, table_id):
        return self.db.tables.find_one({"_id": ObjectId(table_id)})

    def delete_table(self, table_id):
        self.db.tables.delete_one({"_id": ObjectId(table_id)})

    def add_request(self, table_id, time):
        table = self.get_table(table_id)
        self.db.requests.insert_one({"owner": table['owner'], "table_number": table['number'],
                                     "table_id": table_id, "time": time})

    def get_requests(self, owner_id):
        return list(self.db.requests.find({"owner": owner_id}))

    def delete_request(self, request_id):
        self.db.requests.delete_one({"_id": ObjectId(request_id)})

