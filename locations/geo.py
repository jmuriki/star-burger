import requests

from geopy.distance import distance, lonlat

from star_burger.settings import YANDEX_API_KEY
from locations.models import Location


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


def fetch_locations_with_coordinates(objects, loc_lon_lat=None):
    locations_with_coordinates = {}
    if loc_lon_lat is None and not objects.count():
        return locations_with_coordinates
    elif loc_lon_lat is None:
        for obj in objects:
            locations_with_coordinates[obj.address] = {
                'lon': obj.lon,
                'lat': obj.lat,
            }
        return locations_with_coordinates
    for obj in objects:
        if not any(obj.address == location
                for location in loc_lon_lat.keys()):
            try:
                lon, lat = fetch_coordinates(obj.address)
                Location.objects.create(
                    address=obj.address,
                    lon=lon,
                    lat=lat,
                )
            except requests.exceptions.HTTPError:
                lon, lat = 0, 0
            locations_with_coordinates[obj.address] = {
                'lon': lon,
                'lat': lat,
            }
    return locations_with_coordinates
