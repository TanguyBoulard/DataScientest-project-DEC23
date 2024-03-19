import csv
import requests
import datetime
import time


def write_data_to_csv(output_csv_file, data):
    try:
        # Ouvrir le fichier CSV en mode écriture
        # Écrire les données JSON dans le fichier CSV
        with open(output_csv_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())

            # Écrire l'en-tête du fichier CSV
            writer.writeheader()

            # Écrire les données dans le fichier CSV
            writer.writerows(data)
    except Exception as e:
        print(f"Erreur lors de l'écriture des données dans le fichier CSV : {e}")
