# Utilisez une image de base Python
FROM python:3.9

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez les fichiers nécessaires dans le conteneur
COPY ./app /app

# Installez les dépendances Python
RUN pip install fastapi uvicorn

# Exposez le port utilisé par l'application FastAPI
EXPOSE 8000

# Commande pour exécuter l'application FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
