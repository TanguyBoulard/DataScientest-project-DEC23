from dotenv import load_dotenv
import os
from pymongo import MongoClient
from bson.objectid import ObjectId

from models.database import db

load_dotenv()
# Determine the environment context
environment = os.getenv("ENVIRONMENT", "development")
if environment == "development":
    collection = db["my_collection"]
elif environment == "testing":
    collection = db["my_test_collection"]
else:
    raise ValueError("Invalid environment. Please set ENVIRONMENT to 'development' or 'testing'.")


# Example insertion method
def insert_document(document):
    try:
        # Insert document into the collection
        inserted_document = collection.insert_one(document)
        print("Document inserted successfully.")
        return inserted_document.inserted_id

    except Exception as e:
        print(f"Error inserting document: {e}")


def get_all_documents():
    try:
        documents = collection.find()
        return list(documents)
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return []


# Récupérer un document par son identifiant
def get_document_by_id(document_id):
    try:
        document = collection.find_one({"_id": ObjectId(document_id)})
        return document
    except Exception as e:
        print(f"Error retrieving document: {e}")
        return None


def update_document(document_id, update_data):
    try:
        collection.update_one({"_id": ObjectId(document_id)}, {"$set": update_data})
    except Exception as e:
        print(f"Error updating document: {e}")
        return None


# Delete operation
def delete_document(document_id):
    try:
        collection.delete_one({"_id": ObjectId(document_id)})
    except Exception as e:
        print(f"Error deleting document: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # Example document to insert
    example_document = {"key": "value"}

    # Call the insertion method
    insert_document(example_document)

    # Récupérer tous les documents
    all_documents = get_all_documents()
    print("All documents:")
    for doc in all_documents:
        print(doc)

    # Récupérer un document par son identifiant (supposons que document_id soit un identifiant existant)
    document_id = '65f30cb5aa48db250586bd91'
    document = get_document_by_id(document_id)
    if document:
        print(f"Document with id {document_id}:")
        print(document)
    else:
        print(f"No document found with id {document_id}")
