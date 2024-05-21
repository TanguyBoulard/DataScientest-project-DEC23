# EXPLORATION DES JEUX DE DONNEES

# Déclaration des modules
import pandas as pd
import datetime
import requests


# DECLARATION DES VARIABLES D'ENVIRONNEMENT

# Site OpenWeather: token
ApiKey='16b85e20fdb7580f13202c7796d5e016'



# FONCTIONS

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
def OpenWeather_API_CurrentWeather(pCity_name, pCountry_code):

    # Géolocalisation de la ville
    (latitude, longitude)=OpenWeather_API_Geolocal(pCity_name, pCountry_code)

    # REQUETE
    req="https://api.openweathermap.org/data/3.0/onecall?lat="+latitude+"&lon="+longitude+"&exclude=minutely,hourly,daily,alerts"+{part}+"&appid="+ApiKey+"&units=metric"

    # RESULTAT
    res=requests.get(req)
    
    return res.json()


# MAIN

# Divers
date=datetime.datetime.now().strftime("%c")    

# Saisie des paramètres
print("Quel temps fait-il ?")
city_name=input("City name:")
country_code=input("Country code:")

# Current weather
weather_infos=OpenWeather_API_CurrentWeather(city_name,country_code)
print("\n","Current weather on "+date+" at ",city_name+"("+country_code+")","\n","\n",weather_infos)





