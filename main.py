import json, pprint, requests, random
import xmltodict
from pymongo import MongoClient

# on a heavier project one should:
# create a module for http requests
# create a module for database work

#https://www.weatherapi.com/my/
# API Key: 011f134e8ef6447eaae54738202411
#Base URL: http://api.weatherapi.com/v1/
#Search for cities starting with Lond: JSON:
# http://api.weatherapi.com/v1/search.json?key=<YOUR_API_KEY>&q=lond


def get_xml_weather_from_api(city):
    key = '011f134e8ef6447eaae54738202411'
    request_string = 'http://api.weatherapi.com/v1/current.xml?key='
    request_string += key
    request_string += '&q='
    request_string += city
    request_response = requests.get(request_string)
    return request_response

def get_json_weather_from_api(city):
    key = '011f134e8ef6447eaae54738202411'
    request_string = 'http://api.weatherapi.com/v1/current.json?key='
    request_string += key
    request_string += '&q='
    request_string += city
    request_response = requests.get(request_string)
    return request_response


def create_city_weather(request_response, city, format='json'):
    if request_response.status_code == 200:
        if format == 'xml':
            weather = xmltodict.parse(request_response.text)
            weather = json.dumps(weather, indent=4, default='str')
            weather = json.loads(weather)
            weather = weather['root']
            city_weather = set_weather_dictionary(weather)
        else:
            weather = json.loads(request_response.text)
            city_weather = set_weather_dictionary(weather)
        if city_weather['city'] == city.lower().capitalize():
            return city_weather
        else:
            print("I don't know this city")
            return None
    else:
        print("I don't know this city")
        return None


def set_weather_dictionary(weather):
    city_weather = {
        'city': weather['location']['name'],
        'temp_c': weather['current']['temp_c'],
        'temp_f': weather['current']['temp_f'],
        'condition': weather['current']['condition']['text'],
        'wind_kph': weather['current']['wind_kph'],
        'wind_mph': weather['current']['wind_mph'],
        'wind_degree': weather['current']['wind_degree'],
        'wind_dir': weather['current']['wind_mph']
    }
    return city_weather


def get_db_city_weather(city, cities_weather):
    result = cities_weather.find_one({'city':city.lower().capitalize()})
    if result is None:
        choose_parsing_number = random.randint(0,1)
        if choose_parsing_number > 0.5:
            response = get_xml_weather_from_api(city)
            city_weather = create_city_weather(response, city, 'xml')
        else:
            response = get_json_weather_from_api(city)
            city_weather = create_city_weather(response, city)

        if city_weather is not None:
            cities_weather.insert_one(city_weather).inserted_id
            pprint.pprint(cities_weather.find_one({'city':city.lower().capitalize()}))
    else:
        pprint.pprint(result)


def get_weather_db_table():
    client = MongoClient()
    weather_db = client.weather_database
    cities_weather = weather_db['cities_weather_table']
    return cities_weather


def run_city_weather_info():
    print("Press enter to end")
    city = input('Enter a city to get its weather info: ')
    if len(city) == 0:
        print("Goodbye")
        return False
    get_db_city_weather(city, cities_weather_table)
    return True


cities_weather_table = get_weather_db_table()

while run_city_weather_info(): continue
