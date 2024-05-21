# EXPLORATION DES JEUX DE DONNEES

# Déclaration des modules
import pandas as pd
import datetime
import time
import requests


# DECLARATION DES VARIABLES D'ENVIRONNEMENT

# Site OpenWeather: token
ApiKey='16b85e20fdb7580f13202c7796d5e016'



# FONCTIONS

# Horodatege UNIX
def unix_timestamp(pTimeStamp):

    print("timeStamp",pTimeStamp)

    # assigned regular string date
    date_time = datetime.datetime(int(pTimeStamp[0:4]), int(pTimeStamp[4:6]), int(pTimeStamp[6:8]), int(pTimeStamp[8:10]), int(pTimeStamp[10:12]))
    
    # print regular python date&time
    print("date_time =>",date_time)

    
    # displaying unix timestamp after conversion
    #print("unix_timestamp => ",
    #    (time.mktime(date_time.timetuple())))

    #return str(time.mktime(date_time.timetuple()))
    print("unix_timestamp",str.split(str(datetime.datetime.timestamp(date_time)),".")[0])

    return  str.split(str(datetime.datetime.timestamp(date_time)),".")[0]


# Interrogation de l'API OpenWeather: Géolocalisation de ville
def OpenWeather_API_Geolocal(pCity_name, pCountry_code='fr'):

    # Affectations automatique ds paramètres
    StateCode=''
    Limit='10'
    # Composition de la requête
    req="http://api.openweathermap.org/geo/1.0/direct?q="+pCity_name+","+StateCode+","+pCountry_code+"&limit="+Limit+"&appid="+ApiKey

    # REQUETE
    res=requests.get(req)

    # RESULTAT
    res_json=res.json()
    ds_city=pd.DataFrame(res_json)
    longitude=str(ds_city["lon"][0])
    latitude=str(ds_city["lat"][0])

    return (latitude, longitude)


# Interrogation de l'API OpenWeather: infos météo instantannées
def OpenWeather_API_WeatherTimeStamp(pCity_name, pCountry_code, pDate, pHour):

    # Géolocalisation de la ville
    (latitude, longitude)=OpenWeather_API_Geolocal(pCity_name, pCountry_code)

    # Formatage de l'horodatage
    timestamp=unix_timestamp(pDate+pHour)

    # REQUETE
    req="https://api.openweathermap.org/data/3.0/onecall/timemachine?lat="+latitude+"&lon="+longitude+"&dt="+timestamp+"&appid="+ApiKey+"&units=metric"

    # RESULTAT
    res=requests.get(req)
    
    return res.json()


# MAIN =====================================================================

# Divers
date=datetime.datetime.now().strftime("%c")    

# Saisie des paramètres
print("Quel temps fait-il ?")
city_name=input("City name:")
country_code=input("Country code:")
date=input("Date: ")
hour=input("Hour:")

# Current weather
weather_infos=OpenWeather_API_WeatherTimeStamp(city_name,country_code,date,hour)
print("\n","Current weather on "+date+" "+hour+" at ",city_name+"("+country_code+")","\n","\n",weather_infos)

