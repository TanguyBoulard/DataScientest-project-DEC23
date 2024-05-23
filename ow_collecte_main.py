# DECLARATION DES MODULES
import requests
from pathlib import Path
import sys
import datetime
import pandas as pd
import json
import re  # Regular expression
import time

# Import de modules perso
from API_OpenWeather import *
from ow_collecte import *


i=0
while i<=16:    # 16 pour 1000 requetes
    i+=1
    WA_collecte(False,20)    
    time.sleep(120)
