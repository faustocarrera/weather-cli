#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Weather cli - Weather from the command line
Basically the script checks your ip, geolocate the ip and
checks the weather based on that information, so cool!
"""

import os
import sys
import ConfigParser
import argparse
import requests
from requests.exceptions import ConnectionError
from geoip import geolite2
import json
import datetime
from tabletext import to_text

IP_URL = 'http://ipecho.net/plain'
FORECAST_URL = 'https://api.forecast.io/forecast'


def get_ip():
    "check the external ip"
    result = 0
    try:
        headers = {'Content-type': 'application/json'}
        req = requests.get(
            IP_URL,
            headers=headers,
        )
        result = req.text
    except ConnectionError, error:
        sys.exit(error)
    return result


def get_geolocation(ipaddress):
    "check latitude and longitude of the ip"
    result = {'lat': 0, ' lon': 0}
    try:
        match = geolite2.lookup(ipaddress)
        result['lat'] = float(match.location[0])
        result['lon'] = float(match.location[1])
    except ValueError as error:
        sys.exit(error)
    return result


def get_weather(config, geolocation):
    "request weather based on the location"
    # check config key
    if config['key'] == '':
        sys.exit('You have to provide a Forecast.io API key')
    forecast_url = '%s/%s/%s,%s/%s' % (
        FORECAST_URL,
        config['key'],
        geolocation['lat'],
        geolocation['lon'],
        '?units=si'
    )
    headers = {'Content-type': 'application/json'}
    # force disable insecure request warning
    requests.packages.urllib3.disable_warnings()
    req = requests.get(
        forecast_url,
        headers=headers,
    )
    try:
        return json.loads(req.text)
    except ConnectionError, error:
        sys.exit(error)


def output(weather, data_type):
    "format and output the weather"
    table = []
    # city name
    city = str(weather['timezone']).replace('_', ' ')
    # hourly limit
    if len(weather['hourly']['data']) > 12:
        hourly = weather['hourly']['data'][0:12]
    else:
        hourly = weather['hourly']['data']
    # current weather
    if data_type == 'now':
        print ''
        print '%s now' % city
        table.append(['summary', 'temp', 'term', 'humidity'])
        table.append([weather['currently']['summary'],
                      format_temp(weather['currently']['temperature']),
                      format_temp(weather['currently']['apparentTemperature']),
                      format_hmid(weather['currently']['humidity'])])

    # next 24 hours
    if data_type == 'hourly':
        print ''
        print '%s forecast next %s hours' % (city, len(hourly))
        table.append(['day', 'summary', 'temp', 'term', 'humidity'])
        for data in hourly:
            table.append([format_timestamp(data['time'], 'hour'),
                          data['summary'],
                          format_temp(data['temperature']),
                          format_temp(data['apparentTemperature']),
                          format_hmid(data['humidity'])])

    # next few days
    if data_type == 'forecast':
        print ''
        print '%s forecast next %s days' % (city, len(weather['daily']['data']))
        table.append(['day', 'summary', 'min', 'max', 'humidity', 'rain'])
        for data in weather['daily']['data']:
            table.append([format_timestamp(data['time']),
                          data['summary'],
                          format_temp(data['temperatureMin']),
                          format_temp(data['temperatureMax']),
                          format_hmid(data['humidity']),
                          format_hmid(data['precipProbability'])])
    print to_text(table, header=False, corners='+', hor='-', ver='|',
                  formats=['', '', '>', '>', '>', '>'])


def format_timestamp(timestamp, data_type='day'):
    "transform timestamp to datetime"
    date_timestamp = datetime.datetime.fromtimestamp(timestamp)
    today = datetime.date.today()
    # day
    if date_timestamp.strftime('%Y-%m-%d') == today.strftime('%Y-%m-%d'):
        day = 'Today'
    else:
        day = date_timestamp.strftime('%A')
    # hour
    hour = date_timestamp.strftime('%H:%M')
    # check type
    if data_type == 'hour':
        return hour
    return day


def format_temp(temp):
    "format temperature"
    return str(temp) + ' C'


def format_hmid(hmid):
    "format humidity"
    return str(int(float(hmid) * 100)) + '%'


def load_config():
    "load configuration"
    script_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    if not script_path:
        script_path = os.path.abspath('.')
    filename = r'%s/config/weather.conf' % script_path
    config_parser = ConfigParser.RawConfigParser()
    config_parser.read(filename)
    config = {
        'forecast': {
            'key': config_parser.get('forecast', 'key'),
        },
        'geolocation': {
            'lat': config_parser.get('forecast', 'latitude'),
            'lon': config_parser.get('forecast', 'longitude'),
        }
    }
    return config


def arguments():
    "Parse cli arguments"
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description='How is outside? Use the weather cli to figure it out.')
    parser.add_argument(
        '--weather', required=False, type=str, help='What you want to know?',
        default='now', choices=['now', 'hourly', 'forecast'])
    parsed_args = parser.parse_args()
    return parsed_args


def main():
    "entry point"
    args = arguments()
    config = load_config()
    # check if we have a lat and long defined on the config
    if config['geolocation']['lat'] == '' and config['geolocation']['lon'] == '':
        ip_address = get_ip()
        geo = get_geolocation(ip_address)
    else:
        geo = config['geolocation']
    weather = get_weather(config['forecast'], geo)
    output(weather, args.weather)


if __name__ == '__main__':
    main()
