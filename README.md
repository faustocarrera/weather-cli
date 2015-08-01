# Weather cli
Weather from the command line

## How this works?
Basically the script checks your ip, geolocate the ip and checks the weather based on that information, so cool!

## Data sources

* [Forecast.io](https://developer.forecast.io/)
* [GeoLite2 City MaxMin DB](http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz)


## Requirements

* [requests](http://docs.python-requests.org/en/latest/) >= 2.4
* [python-geoip](https://pythonhosted.org/python-geoip/) >= 2.2
* [python-geoip-geolite2](https://pypi.python.org/pypi/python-geoip-geolite2) >= 2015.303
* [tabletext](https://github.com/Thibauth/tabletext) >= 0.1

Install requirements

```python
pip install -r requirements
```

You gonna need a Forecast.io API key, register [here](https://developer.forecast.io/) to obtain it. You have 999 API calls per day for free, enough to check the weather a couple of times a day.

## Configuration

Just create the config/wheather.conf file and add your Forecast.io API key and you are ready.  

You could add the latitude and logitude of the city you want to check the weather, just found the data on [travelmath.com](http://www.travelmath.com/)  

If you leave both numbers empty, the script will try to check your location based on your IP.

```python
[forecast]
key = your_forecast_io_api_key
latitude = 55.7522222
longitude = 37.6155556
```

## Try it

* git clone git@github.com:faustocarrera/weather-cli.git
* update the config/wheather.conf file with your Forecast.io API key
* virtualenv env
* source env/bin/activate
* pip install -r requirements
* python weather.py
* profit

## Usage

```python
python weather.py --weather [OPTION]
```

now: default action for current weather  
hourly: weather for the next 12 hours  
forecast: forecast for the next 8 days  

## Todo

* ~~add option for just current weather~~
* ~~add option for next 12 hours forecast~~
* ~~add option for next 8 days forecast~~
* ~~set now as default weather option~~
* ~~add option to include my own latitude and longitude to config file~~
* ~~convert dates to days names~~
* add autoconfiguration
* add to pipy for easy setup

