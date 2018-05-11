#!/bin/bash
clear
echo "Set environment variables"
export OUTLOOK_USERNAME='thor_johnson@msn.com'
export OUTLOOK_PASSWORD='sarahchance'
export CLIENT_SECRET_FILE='/home/pi/myLadybugHelper/env_variables/client_secret.json'
export GMAIL_STORAGE='/home/pi/myLadybugHelper/env_variables/gmail.storage'
export DATABASE_FILE='/home/pi/myLadybugHelper/databases/garden_readings.db'
export WEATHER_URL='https://api.darksky.net/forecast/d3fbc403cc28523a125c3c5ab8e43ded/47.649093,-122.199153'
export WEATHER_PNG=/home/pi/myLadybugHelper/weather_images/daily_weather.png
export LOGFILE='/home/pi/myLadybugHelper/should_i_water/should_i_water.log'
echo "Done setting environment variables"
