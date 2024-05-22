# DECLARATION DES MODULES
import requests
from pathlib import Path
import sys
import datetime
import pandas as pd
import json
import re  # Regular expression

# Import de modules perso
from OpenWeather_API import *
from OW_Collecte import *

# DECLARATION DES VARIABLES GLOBALE
fichier_ref="weatherAus.csv"


# Chargement du fichier weatherAus.csv
def charge_fichier_reference():
    
    # Chargement du dataframe
    df=pd.read_csv(fichier_ref,sep=";")
    # Apercu du dataframe
    print("\n",df.head(30))
    # Date max du dataframe = Date de début du traitement
    date_debut=df['Date'].min()
    date_fin=df['Date'].max()
    param_dict={"debPeriode":date_debut,"finPeriode":date_fin}
    with open("weatherAus.ini","w") as f:
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


# Lister les villes
def lister_villes(pdf):

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

    # Sauver le fichier ville
    df_ville.to_csv("villeAus.csv",sep=";")
    
    return df_ville


# Corriger les villes
def corriger_villes():

     # Charger le fichier ville
    df_ville=pd.read_csv("villeAus.csv",sep=";",index_col=0)

    # Recherche des villes qui n'ont pas de coordonnées
    #df2_ville=df_ville['Latitude'].isna()
    #print(df2_ville)

    df_ville["VilleReelle"]=df_ville["VilleReelle"].apply(split_majuscule)
    df_ville['VilleReelle']=df_ville["VilleReelle"].replace(to_replace=["Nhil","Pearce R A A F"],value=["Nhill","Bullsbrook"])
    
    """
    df2=df_ville[df_ville['Latitude'].isna()]
    liste_ville=df2['Ville'][:]

    i=0
    for ville in liste_ville:
        print(df_ville.loc[i,"VilleReelle"])
        df_ville.loc[i,"VilleReelle"]=split_majuscule(ville)
        i+=1
    """

    # Sauver le fichier ville
    df_ville.to_csv("villeAus.csv",sep=";")

    # Aperçu du fichier ville
    print("\n",df_ville)


# Rechercher les coordonnées des villes
def coord_villes_2(pTous=True):

    # Charger le fichier ville
    df_ville=pd.read_csv("villeAus.csv",sep=";",index_col=0)

    # Recherche des villes qui n'ont pas de coordonnées
    df2=df_ville[df_ville['Latitude'].isna()]
    liste_ville=df2['VilleReelle'][:]
    print(df2["VilleReelle"])
    print(liste_ville)

    i=0
    country="AU"    
    for ville in liste_ville:
        print(ville)
        # Géolocalisation de la ville
        (latitude, longitude)=Geolocal_API(ville, country)
        df_ville.loc[i,"Latitude"]=float(latitude)
        df_ville.loc[i,"Longitude"]=float(longitude)
        i+=1
    
    df_ville['VilleReelle']=df_ville["VilleReelle"].replace(to_replace=["Nhil","Pearce R A A F"],value=["Nhill","Bullsbrook"])
    # Sauver le fichier ville
    df_ville.to_csv("villeAus.csv",sep=";")

    # Aperçu du fichier ville
    print("\n",df_ville)


# Rechercher les coordonnées des villes
def coord_villes(pTous=True):

    # Charger le fichier ville
    df=pd.read_csv("villeAus.csv",sep=";",index_col=0)
         
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
    df.to_csv("villeAus.csv",sep=";")

    # Aperçu du fichier ville
    print("\n",df)
    return df


# Liste des villes
    
def liste_ville():    
    # Charger le fichier ville
    df_ville=pd.read_csv("villeAus.csv",sep=";",index_col=0)
    print(df_ville)





# Menu général
# ------------
def MenuGeneral():
    print("\n===============================")
    print("Quelle données souhaitez vous ?")
    print("0. Charger le fichier ", fichier_ref)
    print("1. Villes - Rechercher les villes")
    print("2. Villes - Rechercher les coordonnées")
    print("3. Villes - Corriger les noms")
    print("4. Villes - Liste")
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
            df=charge_fichier_reference()
        case "1":
            # lister les villes
            lister_villes(df)
        case "2":
            # Coordonnées des villes
            coord_villes_2()
        case "3":
            # Corriger les villes
            corriger_villes()
        case "4":
            # Lister les villes
            liste_ville()    

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






