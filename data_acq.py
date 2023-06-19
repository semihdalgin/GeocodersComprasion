import csv
import requests
from math import radians, cos, sin, asin, sqrt, atan2
from geopy.geocoders import Nominatim
import numpy as np


geolocator = Nominatim(user_agent='my_geocoder')
cf = 'db_station_address.csv'
output_file = 'geocoded_add.csv'


def geocode_address(address):
    api_key = 'API'
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'

    params = {
        'address': address,
        'key': api_key
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        result = data['results'][0]
        lat = result['geometry']['location']['lat']
        lng = result['geometry']['location']['lng']
        return lat, lng
    else:
        return None, None


def haversine(lon1, lat1, lon2, lat2):
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    r = 6371000  # Radius of earth in meters.
    return c * r


# Function to geocode an address using the QGIS geocoding API
def qgis_address(address):
    try:
        location = geolocator.geocode(address)
        if location is not None:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Error geocoding address '{address}': {str(e)}")
    return None, None


# Function to geocode an address using the HERE Geocoding API
def here_address(address):
    api_key = 'API'
    base_url = 'https://geocode.search.hereapi.com/v1/geocode'

    # Construct the request URL
    params = {
        'q': address,
        'apiKey': api_key
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if 'items' in data and len(data['items']) > 0:
        item = data['items'][0]
        position = item['position']
        lat = position['lat']
        lng = position['lng']
        return lat, lng
    else:
        return None, None


# Read addresses from CSV file and geocode them
def geocode_addresses(cf, limit=100):
    count = 0

    with open(cf, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file, delimiter=';')
        header = next(reader)
        header.extend(['Google Latitude', 'Google Longitude', 'gerror', 'Google Distance',
                       'Qgis Lat', 'Qgis Lng', 'qerror', 'Qgis Distance',
                       'Here Lat', 'Here Lng', 'herror', 'Here Distance'
                       ])
        rows = []
        for row in reader:
            if count >= limit:
                break
            address = row[1]
            lat, lng = geocode_address(address)

            # Google API
            row.extend([lat, lng])  # Add latitude and longitude values to the row
            if lat is not None:
                diflat = float(row[2]) - float(lat)
                diflng = float(row[3]) - float(lng)
                gerror= np.sqrt(diflat ** 2+diflng ** 2)
                row.extend([gerror])  # Add error
                dist = haversine(float(lng), float(lat), float(row[3]), float(row[2]))
                row.extend([dist])
            else:
                continue

            # Qgis API (geocoder)
            lat2, lng2 = qgis_address(address)
            row.extend([lat2, lng2])  # Add latitude and longitude values to the row
            if lat2 is not None:
                diflat2 = float(row[2]) - float(lat2)
                diflng2 = float(row[3]) - float(lng2)
                qerror = np.sqrt(diflat2 ** 2 + diflng2 ** 2)
                row.extend([qerror])  # Add error
                dist2 = haversine(float(lng2), float(lat2), float(row[3]), float(row[2]))
                row.extend([dist2])
            else:
                continue

            # HERE API (geocoder)
            lat3, lng3 = here_address(address)
            row.extend([lat3, lng3])  # Add latitude and longitude values to the row
            if lat3 is not None:
                diflat3 = float(row[2]) - float(lat3)
                diflng3 = float(row[3]) - float(lng3)
                herror = np.sqrt(diflat3 ** 2 + diflng3 ** 2)
                row.extend([herror])  # Add error
                dist3 = haversine(float(lng3), float(lat3), float(row[3]), float(row[2]))
                row.extend([dist3])
            else:
                continue

            rows.append(row)
            count += 1

    with open(output_file, 'w', newline='', encoding='utf-8') as output:
        writer = csv.writer(output, delimiter=',')  # Specify the delimiter as ','
        writer.writerow(header)  # Write the header row
        writer.writerows(rows)  # Write the data rows

    print(f'Geocoded addresses saved to: {output_file}')


geocode_addresses(cf, limit=100)
