# DECLARATION DES MODULES
import requests
from pathlib import Path
import sys
import datetime
import pandas as pd
import json

# Import de modules perso
from OpenWeather_API import *


# Menu général
# ------------
def MenuGeneral():
    print("\n===============================")
    print("Quelle données souhaitez vous pour ",city_name,"("+country_code+") ?")
    print("0. Quel temps fait-il (FREE)?")
    print("1. Quel temps fait-il?")
    print("2. Quel temps faisait-il la journée du ...?")
    print("3. Quel temps faisait-il le ... à ... heure?")
    print("t. Test")
    print("v. Changer de ville")
    print("q. Quitter")
    print("=================================")
    choix=input("Quel est votre choix:")
    
    return choix

# Traitements
# -----------
def TraitementChoix(pChoix):

    global city_name, country_code, date, hour, latitude, longitude

    if (city_name=="NaN"):
        pChoix="v"

    match pChoix:
        case "0":
            # Current weather FREE
            Test_CurrentWeather_FREE_API()
        case "1":
            # Current weather
            Test_CurrentWeather_API()
        case "2":
            # DailyWeather
            Test_DailyAgregation_API()
        case "3":
            # WeatherTimestamp
            Test_WeatherTimeStamp_API()
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
            df.loc[0, 'MinTemp']=obj_python['temperature']['min']
            df.loc[0, 'MaxTemp']=obj_python['temperature']['max']
            df.loc[0, 'Rainfall']=obj_python['precipitation']['total']
            df.loc[0, 'Location']=city_name
#            pressure=obj_python['pressure']
 #           wind=obj_python['wind']
            print(df)
         

        case "v":
            (city_name,country_code,latitude,longitude)=VilleChoix()
            print("latitude:",latitude,"longitude:",longitude)    
            if latitude=="#":
                print("Ville inconnue !") 
                city_name="#"
        case "q":
            print("A bientôt")
        case _:
            print("Mauvais choix")


# =====
# MAIN
# =====

# Divers
date=datetime.datetime.now().strftime("%c")    

choix="v"
while choix!="q":

    # Traitement
    TraitementChoix(choix)

    # Menu
    choix=MenuGeneral()

 





