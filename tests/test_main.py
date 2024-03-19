from fastapi.testclient import TestClient
from app.main import app
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()
os.environ["ENVIRONMENT"] = 'testing'
client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
