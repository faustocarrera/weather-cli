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
import requests
from requests.exceptions import ConnectionError
from geoip import geolite2
import json
import datetime
from tabletext import to_text
import click


class Weather(object):

    "The weather class"

    ip_url = 'http://ipecho.net/plain'
    forecast_url = 'https://api.forecast.io/forecast'
    forecast_api_key = None
    geo = None

    def __init__(self):
        pass

    def magic(self, data_type):
        "check for weather"
        weather_data = self.get_weather()
        self.output(weather_data, data_type)

    def api_key(self, forecast):
        "set forecast.io api key"
        self.forecast_api_key = forecast['key']

    def geolocation(self, geo):
        "set geolocation"
        self.geo = geo

    def get_ip(self):
        "check the external ip"
        result = 0
        try:
            headers = {'Content-type': 'application/json'}
            req = requests.get(
                self.ip_url,
                headers=headers,
            )
            result = req.text
        except ConnectionError, error:
            print error
            sys.exit(1)
        return result

    @staticmethod
    def get_geolocation(ipaddress):
        "check latitude and longitude of the ip"
        result = {'lat': 0, ' lon': 0}
        try:
            match = geolite2.lookup(ipaddress)
            result['lat'] = float(match.location[0])
            result['lon'] = float(match.location[1])
        except ValueError as error:
            print error
            sys.exit(1)
        return result

    def get_weather(self):
        "request weather based on the location"
        geolocation = self.geo
        # check config key
        if not self.forecast_api_key:
            sys.exit('You have to provide a Forecast.io API key')
        forecast_url = '%s/%s/%s,%s/%s' % (
            self.forecast_url,
            self.forecast_api_key,
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
            print error
            sys.exit(1)

    def output(self, weather, data_type):
        "format and output the weather"
        table = []
        # city name
        city = str(weather['timezone']).replace('_', ' ')
        # hourly limit
        if len(weather['hourly']['data']) > 24:
            hourly = weather['hourly']['data'][0:24]
        else:
            hourly = weather['hourly']['data']
        # current weather
        if data_type == 'now':
            print ''
            print '%s now' % city
            table.append(['summary', 'temp', 'term', 'humidity'])
            table.append([weather['currently']['summary'],
                          self.format_temp(
                              weather['currently']['temperature']),
                          self.format_temp(
                              weather['currently']['apparentTemperature']),
                          self.format_percent(weather['currently']['humidity'])])

        # next 24 hours
        if data_type == 'hourly':
            print ''
            print '%s forecast next %s hours' % (city, len(hourly))
            table.append(['day', 'summary', 'temp', 'term', 'humidity'])
            for data in hourly:
                table.append([self.format_timestamp(data['time'], 'hour'),
                              data['summary'],
                              self.format_temp(data['temperature']),
                              self.format_temp(data['apparentTemperature']),
                              self.format_percent(data['humidity'])])

        # next few days
        if data_type == 'forecast':
            print ''
            print '%s forecast next %s days' % (city, len(weather['daily']['data']))
            table.append(['day', 'summary', 'min', 'max', 'humidity', 'rain'])
            for data in weather['daily']['data']:
                table.append([self.format_timestamp(data['time']),
                              data['summary'],
                              self.format_temp(data['temperatureMin']),
                              self.format_temp(data['temperatureMax']),
                              self.format_percent(data['humidity']),
                              self.format_percent(data['precipProbability'])])
        print to_text(table, header=False, corners='+', hor='-', ver='|',
                      formats=['', '', '>', '>', '>', '>'])

    @staticmethod
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

    @staticmethod
    def format_temp(temp):
        "format temperature"
        return str(temp) + ' C'

    @staticmethod
    def format_percent(num):
        "format humidity"
        return str(int(float(num) * 100)) + '%'


def load_config():
    "load configuration"
    script_path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_path, 'weather.conf')
    # check if file exists
    if not os.path.isfile(filename):
        sys.exit(
            'Error: you have to create the config file, run weather-cli --setup')
    # load configuration
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


def setup_config():
    "help setup the config file"
    script_path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_path, 'weather.conf')
    # read the input
    print 'required parameters'
    api_key = raw_input('Enter the forecast.io api key:')
    print 'optional parameters'
    lat = raw_input('Enter the latitude: ')
    lon = raw_input('Enter the longitude: ')
    # write configuration
    print 'generating config file...'
    fconfig = open(filename, 'w')
    fconfig.write("[forecast]\n")
    fconfig.write("key = %s\n" % api_key)
    fconfig.write("latitude = %s\n" % lat)
    fconfig.write("longitude = %s\n" % lon)
    fconfig.close()
    sys.exit('setup complete')


@click.command()
@click.option('--weather', type=str, default='now', help='Get weather: now, hourly, forecast')
@click.option('--setup', default=False, is_flag=True, help='Run setup')
def cli(weather, setup):
    "Weather from the command line"
    whtr = Weather()
    # check if we have to setup the config file
    if setup:
        setup_config()
    # load configuration
    config = load_config()
    # check if we have a lat and long defined on the config
    if config['geolocation']['lat'] == '' or config['geolocation']['lon'] == '':
        ip_address = whtr.get_ip()
        geo = whtr.get_geolocation(ip_address)
    else:
        geo = config['geolocation']
    # display weather
    whtr.api_key(config['forecast'])
    whtr.geolocation(geo)
    whtr.magic(weather)


if __name__ == '__main__':
    cli()
