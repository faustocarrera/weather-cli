# Weather cli
Weather from the command line, so cool!

## Installation

```
pip install weather-cli
```

## Configuration

```
weather-cli --setup
```

If you installed directly without using virtualenv, you have to use sudo to set it up.

You will need a pirate-weather.apiable.io API key, register [here](https://pirate-weather.apiable.io/products/weather-data/) to obtain it. You have 10,000 API calls per month for free, enough to check the weather a couple of times a day.

You could add the latitude and logitude of the city you want to check the weather, just go to [travelmath.com](http://www.travelmath.com/) and search the city.  

If you leave both numbers empty, the script will try to guess your location based on your public IP.

## Usage

```
weather-cli [OPTION] [FORMAT]
```

|Option          | Description                   |
|----------------|-------------------------------|
|-n, --now       | Get current weather           |
|-h, --hourly    | Get the next 24 hours weather |
|-f, --forecast  | Get the next days weather     |
|--about         | About weather-cli             |
|--info          | Check current configuration   |
|--setup         | Run setup                     |
|--format [json] | Output format                 |
|--help          | Show this message and exit.   |

## Data sources

* [pirate-weather.apiable.io](https://pirate-weather.apiable.io/)
* [GeoLite2 City MaxMin DB](http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz)


## Dependencies

* [requests](http://docs.python-requests.org/en/latest/) >= 2.4
* [geocoder](https://github.com/DenisCarriere/geocoder) >= 1.5
* [tabletext](https://github.com/Thibauth/tabletext) >= 0.1

## Try it without installing

```
$ git clone git@github.com:faustocarrera/weather-cli.git
$ virtualenv env -p python2.7
$ source env/bin/activate
$ pip install -r requirements.txt
$ python weather/weather.py --setup
$ python weather/weather.py [OPTIONS] [FORMAT]
$ profit
```

## License

MIT

## Version history

**ver 1.0.1**

add fix to Weather class import  
add fix to raw_input error  

**ver 1.0.0**

add python3 support

**ver 0.2.3**

Fix weather api url

**ver 0.2.1**  

Replace python-geoip for geocoder library for a better geolocation   
Enhace the setup process to be more descriptive  
Add city name to config file  

**ver 0.1.12**  

add output data as json

**ver 0.1.11**  

small fixes  
add new short options -n -h -f  
add about  
add config info  
check error on setup 

**ver 0.1.10**  

first beta version

**ver 0.1.0**  

first alpha version
