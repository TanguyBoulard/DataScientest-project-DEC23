
import pandas as pd
import json
import datetime
import os.path
from os import path
from OpenWeather_API import *

# Collecte des infos OpenWeather

# Traitement lancé toutes les minutes
# via crontab

# Prérequis
# 1 - la liste des villes est complète (NomVille, lat, long, NomVille corrigé)
# les latitudes et longitudes manquantes sont saisies à la main 
# Traitement fait au préalable
# 2 - les paramètres principaux sont initialisés
# debPériode et finPériode 
# nombre de boucle de traitement par minute


# Lecture générique de paramétres
def parametres_charge(pNomFic):

    ficIni=pNomFic
    fileObject = open(ficIni, "r")
    jsonContent = fileObject.read()
    paramDict = json.loads(jsonContent)
    fileObject.close()
    return paramDict


# Init des parametres de l'application
def parametres_init(pNomFic):

    global gDebPeriode, gFinPeriode, gFinPeriodeRecherche

    paramDict=parametres_charge(pNomFic)
    gDebPeriode=str(paramDict["debPeriode"])
    gFinPeriode=str(paramDict["finPeriode"])
    gFinPeriodeRecherche=str(paramDict["finPeriodeRecherche"])
    

# Calcul du jour suiavnt une date
def jour_suivant(pDate):

    pDate=pDate.split("-")
    year=int(pDate[0])
    month=int(pDate[1])
    day=int(pDate[2])
    pDate=datetime.date(year,month,day)
    pDate=(pDate + datetime.timedelta(1)).isoformat()
    return pDate


# Charger le fichier ville
def villes_charger(pNomFic):

    df_ville=pd.read_csv(pNomFic,sep=";",index_col=0)
    df_ville=df_ville.fillna("")

    return df_ville



def WA_DailyAgregation(pdf):


    return pdf



def WA_WeatherTimestamp(pdf):

    return pdf



def WA_collecte(test,nbReq):

    # INIT DE LA COLLECTE

    # Chargement des paramètres
    parametres_init("weatherAus.ini")
    ville=""
    print("PERIODE DE REFERENCE:",gDebPeriode,gFinPeriode,gFinPeriodeRecherche)

    # Chargement des villes
    df_villes=villes_charger("villeAus.csv")

    # Chargement du fichier de référence
    df_ref=pd.read_csv("weatherAUS.csv",sep=";")
    listeColonnes=df_ref.columns

    # Ouverture du fichier de collecte DailyAgregation.json
    fichier_DA = open("DailyAgregation.json", "a")
    # Ouverture du fichier de collecte WeatherTimeStamp.json
    fichier_WTS = open("WeatherTimeStamp.json", "a")
    
    # DEBUT DE BOUCLE DE TRAITEMENT ===============================
    
    for c in range(0,nbReq):

        # La ville n'est pas renseigné, changement de ville
        if (ville==""):

            # Ville à traiter et date de début de traitement
            # Recherche de la dernière ville traitée
            # si (ville.date<>"" et ville.date<finPériode) ou (date="") 
            ville2 = df_villes[((df_villes["DerniereDateTraitee"]!="") & (df_villes["DerniereDateTraitee"]<gFinPeriodeRecherche))]

            if len(ville2.index)>0:
                ville2= ville2.iloc[0]
                dateTrait=ville2["DerniereDateTraitee"]
                dateTrait=jour_suivant(dateTrait)
            else:
                ville2 = df_villes[(df_villes["DerniereDateTraitee"]=="")]
                if len(ville2.index)>0:
                    ville2= ville2.iloc[0]
                    dateTrait=gFinPeriode
                    dateTrait=jour_suivant(dateTrait)
                else:
                    print("Fin du traitement")   

            # => Ville = ville.nom
            # => Lat = ville.lat
            # => Long = ville.long
            # => dateInitiale = ville.DerniereDateTraitée
            ville=ville2["VilleReelle"]
            lat=ville2["Latitude"]
            long=ville2["Longitude"]

            # Calcul du nom du fichier résultat
            # => ficVille = weatherAus_Ville.csv
            ficDfVille="OW_collecte.csv"
            
            # Initialisation du fichier collecte    
            i=0    
            df_trait=pd.DataFrame([],columns=listeColonnes)
            if not path.exists(ficDfVille):
                df_trait.to_csv(ficDfVille,sep=";",mode='a',index=False)


        print("\n A TRAITER: ",ville, dateTrait)

    
        # TRAITEMENT DE COLLECTE
 
        if test==False:


            # DailyAgregation
            # Collecte et traitements des données ( Ville, ville.Lat, ville.Long, dateRech )
            weather_infos=DailyAgregation_API(ville,"au",dateTrait)
            obj_python = weather_infos
            # Sauvegarde des données brute DailyAgregation
            fichier_DA.write(json.dumps(obj_python))
            fichier_DA.write("\n")
            # Traitement des données externes
            df_trait.loc[i, 'Date']=obj_python['date']
            df_trait.loc[i, 'Location']=ville
            # Traitement et intégration des données DailyAgregation
            df_trait.loc[i, 'MinTemp']=obj_python['temperature']['min']
            df_trait.loc[i, 'MaxTemp']=obj_python['temperature']['max']
            df_trait.loc[i, 'Rainfall']=obj_python['precipitation']['total']
            df_trait.loc[i, 'Evaporation']=""     # obj_python['precipitation']['total']
            df_trait.loc[i, 'Sunshine']=""        # obj_python['precipitation']['total']
            df_trait.loc[i, 'WindGustDir']=WindOrientation(obj_python['wind']['max']["direction"])
            df_trait.loc[i, 'WindGustSpeed']=obj_python['wind']['max']["speed"]


            # WeatherTimeStamp 9h
            # Collecte et traitements des données ( Ville, ville.Lat, ville.Long, dateRech, heureRech (9 et 15))
            dateTrait2=dateTrait[0:4]+dateTrait[5:7]+dateTrait[8:10] 
            weather_infos=WeatherTimeStamp_API(ville,"au",dateTrait2,"0900")
            obj_python = weather_infos
            # Sauvegarde des données brutes WeatherTimeStamp
            fichier_WTS.write(json.dumps(obj_python))
            fichier_WTS.write("\n")
            # Traitement et intégration des données WeatherTimeStamp
            df_trait.loc[i, 'WindDir9am']=WindOrientation(obj_python['data'][0]['wind_deg'])
            df_trait.loc[i, 'WindSpeed9am']=obj_python['data'][0]['wind_speed']
            df_trait.loc[i, 'Humidity9am']=obj_python['data'][0]['humidity']
            df_trait.loc[i, 'Pressure9am']=obj_python['data'][0]['pressure']
            df_trait.loc[i, 'Cloud9am']=obj_python['data'][0]['clouds']
            df_trait.loc[i, 'Temp9am']=obj_python['data'][0]['temp']
            

            # WeatherTimeStamp 15h
            # Collecte et traitements des données ( Ville, ville.Lat, ville.Long, dateRech, heureRech (9 et 15))
            weather_infos=WeatherTimeStamp_API(ville,"au",dateTrait2,"1500")
            obj_python = weather_infos
            # Sauvegarde des données brutes WeatherTimeStamp
            fichier_WTS.write(json.dumps(obj_python))
            fichier_WTS.write("\n")
            # Traitement et intégration des données WeatherTimeStamp
            df_trait.loc[i, 'WindDir3pm']=WindOrientation(obj_python['data'][0]['wind_deg'])
            df_trait.loc[i, 'WindSpeed3pm']=obj_python['data'][0]['wind_speed']
            df_trait.loc[i, 'Humidity3pm']=obj_python['data'][0]['humidity']
            df_trait.loc[i, 'Pressure3pm']=obj_python['data'][0]['pressure']
            df_trait.loc[i, 'Cloud3pm']=obj_python['data'][0]['clouds']
            df_trait.loc[i, 'Temp3pm']=obj_python['data'][0]['temp']

            # Va-t-il pleuvoir demain ?
            # Déduction et intégration de l'info
            if (df_trait.loc[i, 'Rainfall']>1):
                df_trait.loc[i, 'RainToday']="Yes"
                if (i>1):
                    df_trait.loc[i-1, 'RainTomorrow']="Yes"
            else:
                df_trait.loc[i, 'RainToday']="No"
                if (i>1):
                    df_trait.loc[i-1, 'RainTomorrow']="No"


        # Mise à jour de la liste des villes
        # Recherche de la ville en cours de traitement
        # => Mise à jour de DerniereDateTraitée
        df_villes.loc[(df_villes["VilleReelle"]==ville),["DerniereDateTraitee"]]=dateTrait

        # Passage à la date suivante    
        dateTrait=jour_suivant(dateTrait)
        i+=1
        if dateTrait>gFinPeriodeRecherche:
            ville="" 


    # FIN DE LA COLLECTE

    # Sauver les données collectées
    df_trait.to_csv(ficDfVille,sep=";",mode='a',index=False, header=False)


    # => Enregistrement de la liste des villes
    # Sauver le fichier ville
    df_villes.to_csv("villeAus.csv",sep=";")

    # Fermeture du fichier DailyAgregation.json
    fichier_DA.close()
    # Fermeture du fichier WeatherTimeStamp.json
    fichier_WTS.close()

