#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import ConfigParser
import argparse
import requests
from geoip import geolite2
import json
import datetime
from tabletext import to_text


def get_ip(ip_url):
    "check the external ip"
    result = 0
    try:
        headers = {'Content-type': 'application/json'}
        req = requests.get(
            ip_url,
            headers=headers,
        )
        result = req.text
    except Exception, error:
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
    forecast_url = '%s/%s/%s,%s/%s' % (
        config['url'],
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
    except (ValueError, KeyError, TypeError):
        sys.exit(req.json())


def output(weather, data_type):
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
        table.append(['', 'Weather for %s' % city, '', '', ''])
        table.append(['date/time', 'summary', 'temp', 'term', 'humidity'])
        table.append([format_timestamp(weather['currently']['time']),
                      weather['currently']['summary'],
                      weather['currently']['temperature'],
                      weather['currently']['apparentTemperature'],
                      float(weather['currently']['humidity'])])

    # next 24 hours
    if data_type == 'hourly':
        table.append(
            ['', 'Forecast next %s hours' % len(hourly), '', '', ''])
        table.append(['date/time', 'summary', 'temp', 'term', 'humidity'])
        for data in hourly:
            table.append([format_timestamp(data['time']),
                          data['summary'],
                          data['temperature'],
                          data['apparentTemperature'],
                          float(data['humidity'])])

    # next few days
    if data_type == 'forecast':
        table.append(
            ['', 'Forecast next %s days' % len(weather['daily']['data']), '', '', ''])
        table.append(['date/time', 'summary', 'min', 'max', 'humidity'])
        for data in weather['daily']['data']:
            table.append([format_timestamp(data['time']),
                          data['summary'],
                          data['temperatureMin'],
                          data['temperatureMax'],
                          data['humidity']])
    print to_text(table, header=False, corners='+', hor='-', ver='|',
                  formats=['', '', '>', '>', '>', '>'])


def format_timestamp(ts):
    "transform timestamp to datetime"
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')


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
            'url': config_parser.get('forecast', 'url'),
            'key': config_parser.get('forecast', 'key')
        },
        'ip': {
            'url': config_parser.get('ip', 'url')
        }
    }
    return config


def arguments():
    "Parse cli arguments"
    parser = argparse.ArgumentParser(
        prog=sys.argv[0], description='How is outside? Use the weather cli to figure it out.')
    parser.add_argument(
        '--weather', required=False, type=str, help='What you want to know?', default='now', choices=['now', 'hourly', 'forecast'])
    parsed_args = parser.parse_args()
    return parsed_args


def main():
    args = arguments()
    config = load_config()
    ip = get_ip(config['ip']['url'])
    geo = get_geolocation(ip)
    weather = get_weather(config['forecast'], geo)
    output(weather, args.weather)


if __name__ == '__main__':
    main()
