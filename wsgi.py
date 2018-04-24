#-- How to set 2 apps in Openshift

from flask import Flask
import redis
import time
import os
from bs4 import BeautifulSoup
import requests

application = Flask(__name__)
cache = redis.StrictRedis(host=os.environ.get("REDIS_SERVICE_HOST","NOT FOUND"),
                          port=os.environ.get("REDIS_SERVICE_PORT_REDIS","NOT_FOUND"),
                          password=os.environ.get("REDIS_PASSWORD","NOT_FOUND"),
                          db=0)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

def init_table():
    url = r"https://en.wikipedia.org/wiki/List_of_stations_of_the_Paris_M%C3%A9tro"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find('table')

    data = []
    nbr_stations = 0
    for tr in table.findAll('tr'):

        index = 0
        station = ""
        lignes = []
        for td in tr.findAll('td')[::3]:
            for a in td.findAll('a'):
                if index == 0:
                    station = a.text
                    nbr_stations +=1
                else:
                    lignes.append(a.text)

                    #print(lignes)
                    index += 1
                    data.append([station, lignes])

    return nbr_stations



@application.route("/")
def hello():
    count = init_table()
    return 'Hi desu! There\'s {} stations desu!.\n'.format(count)

if __name__ == "__main__":
    application.run()
