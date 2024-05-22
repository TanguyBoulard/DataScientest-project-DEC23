
# DECLARATION DES MODULES
import requests
from pathlib import Path
import sys
import datetime
import pandas as pd
import json


# DECLARATION DES VARIABLES D'ENVIRONNEMENT

# Site OpenWeather: token
api_url="http://api.openweathermap.org" 
api_key='16b85e20fdb7580f13202c7796d5e016'

city_name=""
country_code=""
date=""
hour=""

# FONCTIONS

# Horodatege UNIX
# ---------------
def unix_timestamp(pTimeStamp):

 #   print("timeStamp",pTimeStamp)

    # assigned regular string date
    date_time = datetime.datetime(int(pTimeStamp[0:4]), int(pTimeStamp[4:6]), int(pTimeStamp[6:8]), int(pTimeStamp[8:10]), int(pTimeStamp[10:12]))
    
#    # print regular python date&time
#    print("date_time =>",date_time)

    
    # displaying unix timestamp after conversion
    #print("unix_timestamp => ",
    #    (time.mktime(date_time.timetuple())))
    #return str(time.mktime(date_time.timetuple()))

#    print("unix_timestamp",str.split(str(datetime.datetime.timestamp(date_time)),".")[0])

    return  str.split(str(datetime.datetime.timestamp(date_time)),".")[0]


# Interrogation de l'API OpenWeather: Géolocalisation de ville
# ------------------------------------------------------------
def Geolocal_API(pCity_name, pCountry_code='fr'):

    # Affectations automatique ds paramètres
    StateCode=''
    Limit='10'
    # Composition de la requête
    req=api_url+"/geo/1.0/direct?q="+pCity_name+","+StateCode+","+pCountry_code+"&limit="+Limit+"&appid="+api_key

    # REQUETE
    res=requests.get(req)

    # RESULTAT
    res_json=res.json()
    ds_city=pd.DataFrame(res_json)
    try:
       longitude=str(ds_city["lon"][0])
       latitude=str(ds_city["lat"][0])
    except:
       longitude="NaN"
       latitude="NaN"

    return (latitude, longitude)


# Interrogation de l'API OpenWeather: infos météo instantannées FREE
# ------------------------------------------------------------------
def CurrentWeather_FREE_API(pCity_name, pCountry_code):

    # Géolocalisation de la ville
    (latitude, longitude)=Geolocal_API(pCity_name, pCountry_code)

    # REQUETE
    req=api_url+"/data/2.5/weather?lat="+latitude+"&lon="+longitude+"&appid="+api_key+"&units=metric"

    # RESULTAT
    res=requests.get(req)
    
    return res.json()

# Interrogation de l'API OpenWeather: infos météo instantannées
# -------------------------------------------------------------
def CurrentWeather_API(pCity_name, pCountry_code):

    # Géolocalisation de la ville
    (latitude, longitude)=Geolocal_API(pCity_name, pCountry_code)

    # REQUETE
    req="https://api.openweathermap.org/data/3.0/onecall?lat="+latitude+"&lon="+longitude+"&exclude=minutely,hourly,daily,alerts"+"&appid="+api_key+"&units=metric"

    # RESULTAT
    res=requests.get(req)
    
    return res.json()

# Interrogation de l'API OpenWeather: infos météo journalière
# -----------------------------------------------------------
def DailyAgregation_API(pCity_name, pCountry_code, pDate):

    # Géolocalisation de la ville
    (latitude, longitude)=Geolocal_API(pCity_name, pCountry_code)

    # REQUETE
    req=api_url+"/data/3.0/onecall/day_summary?lat="+latitude+"&lon="+longitude+"&date="+pDate+"&appid="+api_key+"&units=metric"

    # RESULTAT
    res=requests.get(req)
    
    return res.json()


# Interrogation de l'API OpenWeather: infos météo instantannées
# -------------------------------------------------------------
def WeatherTimeStamp_API(pCity_name, pCountry_code, pDate, pHour):

    # Géolocalisation de la ville
    (latitude, longitude)=Geolocal_API(pCity_name, pCountry_code)

    # Formatage de l'horodatage
    timestamp=unix_timestamp(pDate+pHour)

    # REQUETE
    req=api_url+"/data/3.0/onecall/timemachine?lat="+latitude+"&lon="+longitude+"&dt="+timestamp+"&appid="+api_key+"&units=metric"

    # RESULTAT
    res=requests.get(req)
    
    return res.json()


# Choix de la ville
# -----------------
def VilleChoix():
    
    global city_name, country_code, latitude, longitude
    
    print("Choisissez votre localisation?")
    city_name=input("City name:")
    country_code=input("Country code:")
    # Géolocalisation de la ville
    (latitude, longitude)=Geolocal_API(city_name, country_code)

    return (city_name,country_code,latitude,longitude)


# Conversion de direction du vent
# -------------------------------
def WindOrientation(pwind_dir):

    div=11.25
    t_wind=["N","NNE","NNE","NE","NE","ENE","ENE","E","E","ESE","ESE","SE","SE","SSE","SSE","S","S","SSO","SSO","SO","SO","OSO","OSO","O","O","ONO","ONO","NO","NO","NNO","NNO","N"]

    pwind_dir=int(pwind_dir % 360)

    i_wind=(int(pwind_dir) // div)
    wind_orient=t_wind[int(i_wind)]

    return wind_orient


# Test de conversion de direction du vent
# ---------------------------------------
def VentDirection():

    print("Direction du vent en degrés ?")
    wind_dir=input("Vent direction:")
    (wind_orient)=WindOrientation(wind_dir)
    print(wind_orient)

def VentTest():
    for i in range(0,361):
        print(i,WindOrientation(i))



# TEST de l'API Current weather FREE
# ----------------------------------
def Test_CurrentWeather_FREE_API():
    print("\n 0. Quel temps fait-il (FREE)?")
    weather_infos=CurrentWeather_FREE_API(city_name,country_code)
    print("\n","Current weather on "+date+" at ",city_name+"("+country_code+")","\n","\n",weather_infos)
    

# TEST de l'API Current weather
# =============================    
def Test_CurrentWeather_API():
    print("\n 1. Quel temps fait-il?")
    weather_infos=CurrentWeather_API(city_name,country_code)
    print("\n","Current weather on "+date+" at ",city_name+"("+country_code+")","\n","\n",weather_infos)


# TEST de l'API DailyWeather
# --------------------------
def Test_DailyAgregation_API():
    print("\n 2. Quel temps faisait-il la journée du ...?")
    date=input("Date (YYYYMMJJ): ")
    date=date[0:4]+"-"+date[4:6]+"-"+date[6:8]
    weather_infos=DailyAgregation_API(city_name,country_code,date)
    print("\n","Current weather on "+date+" at ",city_name+"("+country_code+")","\n","\n",weather_infos)

    directory = Path(__file__).parent
    print("\n Rep:",directory)
                     
    # Sauvegarde les données dans un fichier json
    try:
        nom_fic="OW_"+city_name+"_"+date+".json"
        with open(nom_fic,"w") as f:
            json.dump(weather_infos,f)
                    
    except:
        e = sys.exc_info()[1]
        print(e.args[0])


# TEST de l'API WeatherTimestamp
# ------------------------------
def Test_WeatherTimeStamp_API():
    print("\n 3. Quel temps faisait-il le ... à ... heure?")
    date=input("Date (YYYYMMJJ): ")
    hour=input("Hour (HHMM):")
            
    weather_infos=WeatherTimeStamp_API(city_name,country_code,date,hour)
    print("\n","Current weather on "+date+" "+hour+" at ",city_name+"("+country_code+")","\n","\n",weather_infos)
    
    
         

