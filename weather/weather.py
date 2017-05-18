#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Weather cli - Weather from the command line
Basically the script checks your ip, geolocate the ip and
checks the weather based on that information, so cool!
"""

import os
import sys
import requests
from requests.exceptions import ConnectionError
import geocoder
import json
import datetime
from tabletext import to_text
import click

try:
    import ConfigParser as configparser
except:
    import configparser

__version__ = '1.0.0'


class Weather(object):

    "The weather class"

    ip_url = 'http://ipecho.net/plain'
    forecast_url = 'https://api.darksky.net/forecast'
    forecast_api_key = None
    geo = None

    def __init__(self):
        pass

    def magic(self, data_type, output):
        "check for weather"
        weather_data = self.get_weather()
        weather_result = self.output(
            self.geo['location'], weather_data, data_type)
        # print(result)
        if output == 'json':
            print(json.dumps(weather_result))
        else:
            print('')
            print(weather_result['header'])
            print(to_text(
                weather_result['table'],
                header=False,
                corners='+',
                hor='-',
                ver='|',
                formats=['', '', '>', '>', '>', '>']
            ))

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
        except ConnectionError as error:
            print(error)
            sys.exit(1)
        return result

    @staticmethod
    def get_geolocation(ipaddress):
        "check latitude and longitude of the ip"
        result = {'city': None, 'lat': 0, ' lon': 0}
        try:
            # force disable insecure request warning
            requests.packages.urllib3.disable_warnings()
            match = geocoder.ip(ipaddress)
            result['location'] = '%s, %s' % (match.city, match.country)
            result['lat'] = float(match.lat)
            result['lon'] = float(match.lng)
        except ValueError as error:
            print(error)
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
        except ConnectionError as error:
            print(error)
            sys.exit(1)

    def output(self, location, weather, data_type):
        "format and output the weather"
        header = ''
        table = []
        # hourly limit
        if len(weather['hourly']['data']) > 24:
            hourly = weather['hourly']['data'][0:24]
        else:
            hourly = weather['hourly']['data']
        # current weather
        if data_type == 'now':
            header = 'Weather in %s now' % location
            table.append(['summary', 'temp', 'term', 'humidity'])
            table.append([weather['currently']['summary'],
                          self.format_temp(
                              weather['currently']['temperature']),
                          self.format_temp(
                              weather['currently']['apparentTemperature']),
                          self.format_percent(weather['currently']['humidity'])])

        # next 24 hours
        if data_type == 'hourly':
            header = '%s forecast next %s hours' % (location, len(hourly))
            table.append(['day', 'summary', 'temp', 'term', 'humidity'])
            for data in hourly:
                table.append([self.format_timestamp(data['time'], 'hour'),
                              data['summary'],
                              self.format_temp(data['temperature']),
                              self.format_temp(data['apparentTemperature']),
                              self.format_percent(data['humidity'])])

        # next few days
        if data_type == 'forecast':
            header = '%s forecast next %s days' % (
                location, len(weather['daily']['data']))
            table.append(['day', 'summary', 'min', 'max', 'humidity', 'rain'])
            for data in weather['daily']['data']:
                table.append([self.format_timestamp(data['time']),
                              data['summary'],
                              self.format_temp(data['temperatureMin']),
                              self.format_temp(data['temperatureMax']),
                              self.format_percent(data['humidity']),
                              self.format_percent(data['precipProbability'])])
        return {'header': header, 'table': table}

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
        sys.exit('Error: you have to create the config file, run weather-cli --setup')
    # load configuration
    config_parser = configparser.RawConfigParser()
    config_parser.read(filename)
    # check configuration
    try:
        version = config_parser.get('weather', 'version')
        if version != __version__:
            reconfig(version, filename)
            config_parser.read(filename)
    except configparser.NoSectionError:
        reconfig('0.0.0', filename)
        config_parser.read(filename)
    # config
    config = {
        'weather': {
            'version': config_parser.get('weather', 'version'),
        },
        'forecast': {
            'key': config_parser.get('forecast', 'key'),
        },
        'geolocation': {
            'location': config_parser.get('geolocation', 'location'),
            'lat': config_parser.get('geolocation', 'latitude'),
            'lon': config_parser.get('geolocation', 'longitude'),
        }
    }
    return config


def reconfig(version, filename):
    print('updating configuration...')
    config_parser = configparser.RawConfigParser()
    config_parser.read(filename)
    if version == '0.0.0':
        key = config_parser.get('forecast', 'key')
        lat = config_parser.get('forecast', 'latitude')
        lon = config_parser.get('forecast', 'longitude')
        location = None
        if lat and lon:
            # force disable insecure request warning
            requests.packages.urllib3.disable_warnings()
            geo = geocoder.google([lat, lon], method='reverse')
            location = '%s, %s' % (geo.city, geo.country)

    fconfig = open(filename, 'w')
    fconfig.write("[weather]\n")
    fconfig.write("version = %s\n" % __version__)
    fconfig.write("[forecast]\n")
    fconfig.write("key = %s\n" % key)
    fconfig.write("[geolocation]\n")
    fconfig.write("location = %s\n" % location)
    fconfig.write("latitude = %s\n" % lat)
    fconfig.write("longitude = %s\n" % lon)
    fconfig.close()
    print('done!')
    sys.exit()


def setup_config():
    "help setup the config file"
    script_path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_path, 'weather.conf')
    # required parameters
    print('')
    api_key = raw_input('Enter your forecast.io api key (required):')
    if not api_key:
        print('Sorry, the api key is required')
        print('get your api key from https://developer.forecast.io/')
        sys.exit(1)
    # optional parameters
    print('Warning:')
    print('The script will try to geolocate your IP.')
    print('If you fill the latitude and longitude, you avoid the IP geolocation.')
    print('Use it if you want a more acurated result, use a different location,')
    print('or just avoid the IP geolocation.')
    print('Check your latitude and longitude from http://www.travelmath.com/')
    print('')
    lat = raw_input('Enter the latitude (optional): ')
    lon = raw_input('Enter the longitude (optional): ')
    # get the city name
    location = None
    if lat and lon:
        # force disable insecure request warning
        requests.packages.urllib3.disable_warnings()
        geo = geocoder.google([lat, lon], method='reverse')
        location = '%s, %s' % (geo.city, geo.country)
    # write configuration
    print('generating config file...')
    try:
        fconfig = open(filename, 'w')
        fconfig.write("[weather]\n")
        fconfig.write("version = %s\n" % __version__)
        fconfig.write("[forecast]\n")
        fconfig.write("key = %s\n" % api_key)
        fconfig.write("[geolocation]\n")
        fconfig.write("location = %s\n" % location)
        fconfig.write("latitude = %s\n" % lat)
        fconfig.write("longitude = %s\n" % lon)
        fconfig.close()
        print('setup complete')
        sys.exit(0)
    except IOError:
        print('Use virtualenv or setup as root')
        sys.exit(1)


def about_self():
    "About weather-cli"
    abt = """
    weather-cli
    Weather from the command line
    Version: %s
    Author: Fausto Carrera <fausto.carrera@gmx.com>
    """ % __version__
    return abt


def print_config(config):
    "Current configuration"
    print('')
    print('Current configuration')
    print('version:   %s' % config['weather']['version'])
    print('api key:   %s' % config['forecast']['key'])
    print('location:  %s' % config['geolocation']['location'])
    print('latitude:  %s' % config['geolocation']['lat'])
    print('longitude: %s' % config['geolocation']['lon'])
    print('')


@click.command()
@click.option('--now', '-n', 'weather', flag_value='now', default=True, help='Get current weather')
@click.option('--hourly', '-h', 'weather', flag_value='hourly', help='Get the next 24 hours weather')
@click.option('--forecast', '-f', 'weather', flag_value='forecast', help='Get the next days weather')
@click.option('--about', 'about', default=False, is_flag=True, help='About weather-cli')
@click.option('--info', 'info', default=False, is_flag=True, help='Check current configuration')
@click.option('--setup', 'setup', default=False, is_flag=True, help='Run setup')
@click.option('--output', 'output', type=click.Choice(['json']), help='Output format')
def cli(weather, about, info, setup, output):
    "Weather from the command line"
    # setup weather
    wthr = Weather()
    # check if about
    if about:
        print(about_self())
        sys.exit(0)
    # check if we have to setup the config file
    if setup:
        setup_config()
    # load configuration
    config = load_config()
    # info
    if info:
        print_config(config)
        sys.exit(0)
    # check if we have a lat and long defined on the config
    if config['geolocation']['lat'] == '' or config['geolocation']['lon'] == '':
        ip_address = wthr.get_ip()
        geo = wthr.get_geolocation(ip_address)
    else:
        geo = config['geolocation']
    # display weather
    wthr.api_key(config['forecast'])
    wthr.geolocation(geo)
    wthr.magic(weather, output)


if __name__ == '__main__':
    cli()
