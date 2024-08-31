""" Datalake """


import os
from pymongo import MongoClient


class MongoDBManager:
    """ MongoDB Manager class """
    def __init__(self):
        self.user = os.getenv('MONGO_USER')
        self.password = os.getenv('MONGO_PASSWORD')
        self.host = os.getenv('MONGO_HOST')
        self.port = os.getenv('MONGO_PORT')
        self.dbname = os.getenv('MONGO_INITDB_DATABASE')

        self.client = MongoClient(
            f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}/"
        )

        self.db = self.client[self.dbname]

    def create_collection(self, collection_name):
        """ Create a collection in a database """
        collection = self.db[collection_name]
        return collection

    def insert_document(self, collection_name, document):
        """ Insert a document into a collection """
        collection = self.db[collection_name]
        document_id = collection.insert_one(document).inserted_id
        return document_id

    def find_document(self, collection_name, query):
        """ Find a document in a collection """
        collection = self.db[collection_name]
        document_found = collection.find_one(query)
        return document_found

    def find_documents(self, collection_name, query):
        """ Find multiple documents in a collection """
        collection = self.db[collection_name]
        documents_found = list(collection.find(query))
        return documents_found

    def update_document(self, collection_name, query, new_values):
        """ Update a document in a collection """
        collection = self.db[collection_name]
        updated_result = collection.update_one(query, {'$set': new_values})
        update_result = updated_result.modified_count
        return update_result

    def delete_document(self, collection_name, query):
        """ Delete a document from a collection """
        collection = self.db[collection_name]
        deletion_result = collection.delete_one(query)
        delete_result = deletion_result.deleted_count
        return delete_result

    def delete_documents(self, collection_name, query):
        """ Delete multiples documents from a collection """
        collection = self.db[collection_name]
        deletion_result = collection.delete_many(query)
        delete_result = deletion_result.deleted_count
        return delete_result


if __name__ == "__main__":
    mongo_manager = MongoDBManager()
