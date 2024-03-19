import os
from dotenv import load_dotenv
import os
import sys

from app.models.postgres_model import User


def test_delete_user(db_session):
    # Given
    # Créer un nouvel utilisateur avec des données fictives
    user_data = {
        "username": "testuser",
        "password": "password123",
        "email": "test@example.com"
    }
    user = User(**user_data)

    # Ajouter l'utilisateur à la base de données
    db_session.add(user)
    db_session.commit()

    # When
    # Supprimer l'utilisateur de la base de données
    db_session.delete(user)
    db_session.commit()

    # Then
    # Vérifier que l'utilisateur n'existe plus dans la base de données en recherchant par son nom d'utilisateur
    deleted_user = db_session.query(User).filter(User.username == "testuser").first()
    assert deleted_user is None, "L'utilisateur devrait avoir été supprimé de la base de données"


def test_create_user(db_session):
    # Given
    user_data = {

        "username": "testuser",
        "password": "password123",
        "email": "test@example.com"
    }

    # When
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()

    # Then
    assert user.id is not None


def test_get_user_by_username(db_session):
    # Given
    user_data = {
        "username": "testuser",
        "password": "password123",
        "email": "test@example.com"
    }
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()

    # When
    retrieved_user = db_session.query(User).filter(User.username == "testuser").first()

    # Then
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"
    assert retrieved_user.email == "test@example.com"
