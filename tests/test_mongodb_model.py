import unittest
from pymongo import MongoClient
from app.models.database import db, MongoClient as client
from models.mongodb_model import collection, insert_document, get_all_documents, get_document_by_id, update_document, \
    delete_document


class MyTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        cls.client = client
        cls.db = db
        cls.collection = collection

    def tearDown(self):
        # Supprimer la collection après chaque test
        self.collection.drop()

    def test_insert_document(self):
        document = {"key": "value"}
        inserted_id = insert_document(document)
        self.assertIsNotNone(inserted_id)

    def test_get_all_documents(self):
        # Insert some documents for testing
        self.collection.insert_many([{"key": "value1"}, {"key": "value2"}])

        documents = get_all_documents()
        self.assertEqual(len(documents), 2)

    def test_get_document_by_id(self):
        # Insert a document for testing
        document = {"key": "value"}
        inserted_id = self.collection.insert_one(document).inserted_id

        retrieved_document = get_document_by_id(str(inserted_id))
        self.assertIsNotNone(retrieved_document)

    def test_update_document(self):
        # Insert a document for testing
        document = {"key": "value"}
        inserted_id = self.collection.insert_one(document).inserted_id

        update_data = {"key": "new_value"}
        update_document(str(inserted_id), update_data)

        updated_document = self.collection.find_one({"_id": inserted_id})
        self.assertEqual(updated_document["key"], "new_value")

    def test_delete_document(self):
        # Insert a document for testing
        document = {"key": "value"}
        inserted_id = self.collection.insert_one(document).inserted_id

        delete_document(str(inserted_id))

        deleted_document = self.collection.find_one({"_id": inserted_id})
        self.assertIsNone(deleted_document)
