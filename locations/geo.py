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


def add_locations_with_coordinates(*locations_groups, stored_locations):
    """Adding new locations to database
        and returning a dict of all stored locations addresses with coordinates
            to reduce the number of database queries"""

    addresses_with_coordinates = {}

    if stored_locations.count():
        for location in stored_locations:
                addresses_with_coordinates[location.address] = {
                    'lon': location.lon,
                    'lat': location.lat,
                }

    for group in locations_groups:
        if group.count():
            for location_object in group:
                if not addresses_with_coordinates or not any(
                    location_object.address == address
                        for address in addresses_with_coordinates.keys()):
                    try:
                        lon, lat = fetch_coordinates(location_object.address)
                        Location.objects.create(
                            address=location_object.address,
                            lon=lon,
                            lat=lat,
                        )
                    except requests.exceptions.HTTPError:
                        lon, lat = 0, 0
                    addresses_with_coordinates[location_object.address] = {
                        'lon': lon,
                        'lat': lat,
                    }
    return addresses_with_coordinates
