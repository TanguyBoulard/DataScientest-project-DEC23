from dotenv import load_dotenv
import os
from pymongo import MongoClient
from bson.objectid import ObjectId

# Load environment variables from .env
load_dotenv()

# Access environment variables
MONGO_DB_HOST = 'localhost'
MONGO_DB_PORT = 27017
MONGO_DB_USERNAME = os.getenv("MONGODB_USER")
MONGO_DB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGO_DB_DATABASE = os.getenv("MONGODB_DB")

# MongoDB connection
client = MongoClient(host=MONGO_DB_HOST, port=MONGO_DB_PORT, username=MONGO_DB_USERNAME, password=MONGO_DB_PASSWORD)

# Access database
db = client[MONGO_DB_DATABASE]

# Define a collection
collection = db["example_collection"]


# Example insertion method
def insert_document(document):
    try:
        # Insert document into the collection
        collection.insert_one(document)
        print("Document inserted successfully.")
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
