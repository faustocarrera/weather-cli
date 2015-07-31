#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import ConfigParser
import requests
import geoip2.database
import json
import datetime
from tabletext import to_text


def get_ip(ip_url):
    "check the external ip"
    result = {'status': 'ok', 'ip': 0}
    try:
        headers = {'Content-type': 'application/json'}
        req = requests.get(
            ip_url,
            headers=headers,
        )
        result['ip'] = req.text
    except Exception, error:
        sys.exit(error)
    return result


def get_geolocation(ipaddress):
    "check latitude and longitude of the ip"
    result = {'status': 'ok', 'lat': 0, 'lon': 0}
    reader = geoip2.database.Reader('./database/GeoLite2-City.mmdb')
    response = reader.city(ipaddress)
    try:
        result['city'] = str(response.city.name)
        result['lat'] = float(response.location.latitude)
        result['lon'] = float(response.location.longitude)
    except ValueError as error:
        sys.exit(error[0])
    except geoip2.errors.AddressNotFoundError as error:
        sys.exit(error[0])
    reader.close()
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


def output(weather, city):
    table = []
    table.append(['Weather for %s' % city])
    # header
    table.append(['date/time', 'summary', 'temp', 'term', 'humidity'])
    # current weather
    table.append([format_timestamp(weather['currently']['time']),
                  weather['currently']['summary'],
                  weather['currently']['temperature'],
                  weather['currently']['apparentTemperature'],
                  float(weather['currently']['humidity'])])
    # daily
    table.append(['Forecast next %s days' % len(weather['daily']['data'])])
    table.append(['date/time', 'summary', 'min', 'max', 'humidity'])
    for data in weather['daily']['data']:
        table.append([format_timestamp(data['time']),
                      data['summary'],
                      data['temperatureMin'],
                      data['temperatureMax'],
                      data['humidity']])
    print to_text(table, header=False, corners='+', hor='-', ver='|', formats=['', '', '>', '>', '>', '>'])


def format_timestamp(ts):
    "transform timestamp to datetime"
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')


def load_config():
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


def main():
    config = load_config()
    ip = get_ip(config['ip']['url'])
    geo = get_geolocation(ip['ip'])
    weather = get_weather(config['forecast'], geo)
    output(weather, geo['city'])


if __name__ == '__main__':
    main()
