# DataScientest-project-DEC23
Repository for the final project of the DataScientest training program for cohort DEC23.


### EN COURS DE REDACTION ###

CONTEXTE

Initialement, nous travaillons sur le jeux de données Kaggle - Rain in Autralia
Données météo australiennes d'une période de 10 ans environ.
Fichier: 
   weatherAus.csv
Période: 
   du 01-12-2008 au 25-06-2017.


OBJET

Nous avons décidé d'étoffer ce jeux de données pour une période plus importante soit du 01-12-2008 à nos jours.
Nous devons donc compléter les données météo des stations autraliennes du 26-06-2017 à nos jours.


COMMENT

Via des appels aux API
du site http://OpenWeatherMap.org et traitement de ces données. 
Fichier: 
   - DailyAgregation.json: 
      Données brutes de l'APi OpenWeather DailyAgregation, pour une station météo autralienne, données agrégées d'une journée.
      Fichier à importer dans une BD MONGODB pour un accès permanent au données.
   - WeatherTimeStamp.json:
      Données brutes de l'API OpenWeather WeatherTimeStamp, pour une données d'une journée à  9h et 15h. 
      Fichier à importer dans une BD MONGODB pour un accès permanent au données.
   - Fichier villeAus.csv:
      On trouvera sur chaque enregistrement de ce fichier: 
      . id de la ligne.
      . L'id de la station météo (nom de la station sans espace).
      . les coordonnées GPS de la station.
      . Dernière date traitée = l'état d'avancement de la collecte de données, dernière date requêtée pour la station.
      . Libellé de la station météo.
   - OW_Collecte.csv: 
      A partir des données brutes collectées, traitées et formatées au format initial Kaggle (weatherAus.csv).
      Fichier à concaténer avec le fichier initial Kaggle en fin de projet.
   - weatherAus.ini:
      Fichier contenant les paramètres pour nos traitements.
Période: 
   du 26-06-2017 au 01-02-2023


Via du WebSrapping 
sur le site http://www.bom.gov.au/ et traitement de ces données, 
Depuis février 2024, nous récupérons des données météo tous les jours sur le site.
Nous récupérons également les données météo des 12 derniers mois sur ce même site, soit jusqu'à févier 2023.
Fichier: ?
Période: 
   du 01-02-2023 à fin du projet
