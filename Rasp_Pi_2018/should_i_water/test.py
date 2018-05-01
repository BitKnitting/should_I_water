import certifi
import json
import urllib3


import pdb;pdb.set_trace()
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
url = "https://api.darksky.net/forecast/d3fbc403cc28523a125c3c5ab8e43ded/47.649093,-122.199153"
request = http.request('GET',url)
stuff = json.loads(request.data.decode('utf8'))
summary_string = stuff['hourly']['summary']
# From https://darksky.net/dev/docs
# clear-day, clear-night, rain, snow, sleet, wind, fog, cloudy,
# partly-cloudy-day, or partly-cloudy-night
icon_string = stuff['daily']['icon']
request.release_con()
