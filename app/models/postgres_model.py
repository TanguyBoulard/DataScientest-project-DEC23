import os

from sqlalchemy import Column, Integer, String
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()
from database import Base,SessionLocal


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String, index=True)
    email = Column(String, index=True)

if __name__ == "__main__":
    # Créer un moteur SQLAlchemy pour se connecter à votre base de données PostgreSQL
    # Créer une session SQLAlchemy
    session = SessionLocal()


    # Créer une instance de votre modèle Item avec les données que vous souhaitez enregistrer
    nouvel_utilisateur = User(username="utilisateur1", password="mot_de_passe1",email="ddiopdjibi@gmail.com")

    # Ajouter l'instance à la session
    session.add(nouvel_utilisateur)

    # Valider la transaction pour enregistrer les données dans la base de données
    session.commit()

    users = session.query(User).all()

    # Parcourez les résultats et imprimez-les, ou effectuez d'autres opérations selon vos besoins
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Password: {user.password}")

    # Fermer la session
    session.close()