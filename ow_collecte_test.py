# DECLARATION DES MODULES
import requests
from pathlib import Path
import sys
import datetime
import pandas as pd
import json
import re  # Regular expression

# Import de modules perso
from API_OpenWeather import *
from ow_collecte import *

# DECLARATION DES VARIABLES GLOBALE
file_ref="dataWeatherAus.csv"
file_ini="ow_collecte.ini"
file_station="dataWeatherStation.csv"


# Init des parametres de référence
# Chargement du fichier de reference:  source Kaggle, weatherAus.csv
def param_ref_init(pFile_ref, pFile_ini):
    
    # Chargement du dataframe de référence
    df=pd.read_csv(pFile_ref,sep=";")
    # Apercu du dataframe
    print("\n",df.head(10))

    # Date mi du dataframe = Date début de période de référence
    date_debut=df['Date'].min()
    # Date max du dataframe = Date fin de période de référence = Date de début du traitement
    date_fin=df['Date'].max()
    
    # Sauvegarde des paramètres de référence
    param_dict={"debPeriode":date_debut,"finPeriode":date_fin}
    with open(pFile_ini,"w") as f:
        json.dump(param_dict,f)

    return df


# Spliter les mots contenant des Majuscules
def split_majuscule(pMot):
 
    # Splitting on UpperCase using re
    res_list = []
    res_list = re.findall('[A-Z][^A-Z]*', pMot)

    # Composition de la phrase
    phrase=""
    for mot in res_list:
        phrase+=mot+" "
    phrase=phrase[:-1]
    print(phrase)    
    return phrase


## Lister les villes
#def lister_villes(pdf):

# Initialisation de la Liste des stations meteo
def stations_init(pdf, pFile_station):

    # Extraction des ville du DataFrame de référence
    df_ville=pd.DataFrame([])
    serie_ville=pdf['Location'].value_counts()
    df_ville["Ville"]=serie_ville.index[:]

    # Calcul du nombre de ville
    nb_ville=df_ville["Ville"].count()
    print("\n Nombre de ville:",nb_ville)
    
    # Ajout de colonnes
    # Coordonnées Géographique (Pour éviter de les rechercher à chaque interrogation météo)
    df_ville["Latitude"]=""
    df_ville["Longitude"]=""
    # Dernière date traitée, on y stockera le dernier TimeStamp traité, pour pouvoir reprendre les traitements d'interrogation météo à partir de la bonne date
    df_ville["DerniereDateTraitee"]=""
    # Ville réelle, le nom des ville récupérer est sans espace, il faut reconstituer le nom de certaines ville ayant plusieurs mots
    df_ville["VilleReelle"]=df_ville["Ville"]
    print("\n",df_ville)

    # Sauvvegarde du fichier des station météo
    df_ville.to_csv(pFile_station,sep=";")
    
    return df_ville


# Corriger les stations météo
def stations_correct(pFile_station):

     # Charger le fichier des station météo
    df_ville=pd.read_csv(pFile_station,sep=";",index_col=0)

    # Correction du nom des stations
    df_ville["VilleReelle"]=df_ville["VilleReelle"].apply(split_majuscule)
    # Cas particulier
    df_ville['VilleReelle']=df_ville["VilleReelle"].replace(to_replace=["Nhil","Pearce R A A F"],value=["Nhill","Bullsbrook"])
    
    # Sauvegarde du fichier des stations météo
    df_ville.to_csv(pFile_station,sep=";")

    # Aperçu du fichier des stations météo
    print("\n",df_ville)


# Rechercher les coordonnées des stations météo
def stations_coordinates(pFile_station):

    # Charger le fichier des stations météo
    df_ville=pd.read_csv(pFile_station,sep=";",index_col=0)

    # Recherche des station météo qui n'ont pas de coordonnées
    df2=df_ville[df_ville['Latitude'].isna()]
    liste_ville=df2['VilleReelle'][:]
    #print(df2["VilleReelle"])
    #print(liste_ville)

    # Géolocalisation des stations météo sans coordonnées
    i=0
    country="AU"    
    for ville in liste_ville:
        print(ville)
        # Géolocalisation de la ville
        (latitude, longitude)=Geolocal_API(ville, country)
        df_ville.loc[i,"Latitude"]=float(latitude)
        df_ville.loc[i,"Longitude"]=float(longitude)
        i+=1
    
    #df_ville['VilleReelle']=df_ville["VilleReelle"].replace(to_replace=["Nhil","Pearce R A A F"],value=["Nhill","Bullsbrook"])
    
    # Sauvegarde du fichier des stations météo
    df_ville.to_csv(pFile_station,sep=";")

    # Aperçu du fichier des stations météo
    print("\n",df_ville)


# Rechercher les coordonnées des villes
def coord_villes(pTous=True):

    # Charger le fichier ville
    df=pd.read_csv("dataVilleAus.csv",sep=";",index_col=0)
         
    country="AU"    
    liste_ville=df["Ville"][:]
    i=0
    for ville in liste_ville:
        if (df.loc[i,"Latitude"]=="NaN") | (df.loc[i,"Latitude"]==""): 
            # Géolocalisation de la ville
            (latitude, longitude)=Geolocal_API(ville, country)
            df.loc[i,"Latitude"]=latitude
            df.loc[i,"Longitude"]=longitude
        i+=1
    
    # Sauver le fichier ville
    df.to_csv("dataVilleAus.csv",sep=";")

    # Aperçu du fichier ville
    print("\n",df)
    return df


# Liste des stations météo
def stations_list(pFile_station):    
    # Charger le fichier des stations météo
    df_ville=pd.read_csv(pFile_station,sep=";",index_col=0)
    print(df_ville)



# Menu général
# ------------
def MenuGeneral():
    print("\n===============================")
    print("Quelle données souhaitez vous ?")
    print("0. Charger le fichier de référence ", file_ref)
    print("1. Station météo - Inventaire")
    print("2. Station météo - Recherche des coordonnées")
    print("3. Station météo - Corriger le nom")
    print("4. Station météo - Liste")
    print("c. Collecte")
    print("t. Test")
    print("v. Changer de ville")
    print("w. Convertir du vent")
    print("x. Test Conversion du vent")
    print("q. Quitter")
    print("=================================")
    choix=input("Quel est votre choix:")
    
    return choix

# Traitements
# -----------
def TraitementChoix(pChoix):

    global city_name, country_code, date, hour, df

    match choix:
        case "0":
            # Voir le fichier de référence
            # Chargement du fichier de référence
            df=param_ref_init(file_ref)
        case "1":
            # liste des stations météo
            stations_list(df,file_station)
        case "2":
            # Coordonnées des stations météo
            stations_coordinates(file_station)
        case "3":
            # Corriger les stations météo
            stations_correct(file_station)
        case "4":
            # liste des stations météo
            stations_list(df,file_station)

        case "c":
            WA_collecte()    
        case "t":
            nom_fic="OW_AGEN_2024-01-01.json"
            fileObject = open(nom_fic, "r")
#            print("fileObject:",fileObject)
            jsonContent = fileObject.read()
 #           print("jsonContent:",jsonContent)
            obj_python = json.loads(jsonContent)
  #          print("obj_python:",obj_python)

            df=pd.DataFrame([],columns=['Date','Location','MinTemp','MaxTemp','Rainfall','Evaporation','Sunshine','WindGustDir','WindGustSpeed','WindDir9am','WindDir3pm','WindSpeed9am','WindSpeed3pm','Humidity9am','Humidity3pm','Pressure9am','Pressure3pm','Cloud9am','Cloud3pm','Temp9am','Temp3pm','RainToday','RainTomorrow'])
            df.loc[0, 'Date']=obj_python['date']
            df.loc[0, 'Location']=city_name
            
            # Daily Agregation
            df.loc[0, 'MinTemp']=obj_python['temperature']['min']
            df.loc[0, 'MaxTemp']=obj_python['temperature']['max']
            df.loc[0, 'Rainfall']=obj_python['precipitation']['total']
            df.loc[0, 'Evaporation']=""     # obj_python['precipitation']['total']
            df.loc[0, 'Sunshine']=""        # obj_python['precipitation']['total']

            # Weather TimeStamp
            df.loc[0, 'WindGustDir']=""     # obj_python['precipitation']['total']
            df.loc[0, 'WindGustSpeed']=""   # obj_python['precipitation']['total']
            df.loc[0, 'WindDir9am']=""      # obj_python['precipitation']['total']
            df.loc[0, 'WindDir3pm']=""      # obj_python['precipitation']['total']
            df.loc[0, 'WindSpeed9am']=""    # obj_python['precipitation']['total']
            df.loc[0, 'WindSpeed3pm']=""    # obj_python['precipitation']['total']
            df.loc[0, 'Humidity9am']=""     # obj_python['precipitation']['total']
            df.loc[0, 'Humidity3pm']=""     # obj_python['precipitation']['total']
            df.loc[0, 'Pressure9am']=""     # obj_python['precipitation']['total']
            df.loc[0, 'Pressure3pm']=""     # obj_python['precipitation']['total']
            df.loc[0, 'Cloud9am']=""        # obj_python['precipitation']['total']
            df.loc[0, 'Cloud3pm']=""        # obj_python['precipitation']['total']
            df.loc[0, 'Temp9am']=""         # obj_python['precipitation']['total']
            df.loc[0, 'temp3pm']=""         # obj_python['precipitation']['total']
#           pressure=obj_python['pressure']
#           wind=obj_python['wind']
            print(df)
         

        case "v":
            (city_name,country_code)=VilleChoix()    
        case "w":
            WindDir=VentDirection()    
        case "x":
            VentTest()    
        case "q":
            print("A bientôt")
        case _:
            print("Mauvais choix")


# =====
# MAIN
# =====



choix=""
while choix!="q":

    # Menu
    choix=MenuGeneral()

    # Traitement
    TraitementChoix(choix)






