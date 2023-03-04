import requests

from geopy.distance import distance, lonlat

from star_burger.settings import YANDEX_API_KEY


def fetch_coordinates(address):
    apikey = YANDEX_API_KEY
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def calculate_distance(a, b):
    if a == (0, 0) or b == (0, 0):
        return 0
    return distance(lonlat(*a), lonlat(*b)).km
