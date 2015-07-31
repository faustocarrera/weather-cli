# Weather cli
Weather from the command line

## How this works?
Basically the script checks your ip, geolocate the ip and checks the weather based on that information, so cool!

## Data sources

[Forecast.io](https://developer.forecast.io/)   
[GeoLite2 Free download](https://dev.maxmind.com/geoip/geoip2/geolite2/)  
[GeoLite2 City MaxMin DB](http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz)


## Requirements

* [requests](http://docs.python-requests.org/en/latest/) >= 2.4
* [maxminddb](https://github.com/maxmind/libmaxminddb) >= 1.1
* [geoip2](https://pypi.python.org/pypi/geoip2) >= 2.2
* [tabletext](https://github.com/Thibauth/tabletext) >= 0.1

Install requirements  

```python
pip install -r requirements.txt
```

You gonna need a Forecast.io API key, register [here](https://developer.forecast.io/) to obtain it

## Configuration

Just update the config/wheather.conf file with your Forecast.io API key and you are ready.

## Try it

* git clone git@github.com:faustocarrera/weather-cli.git
* update the config/wheather.conf file with your Forecast.io API key
* virtualenv env
* source env/bin/activate
* pip install -r requirements.txt
* python weather.py
* profit

## Todo

* add option for just current weather
* add option for next 12 hours forecast
* add option for next days forecast
