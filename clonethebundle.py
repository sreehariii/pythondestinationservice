import wget
import json
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import os
from cfenv import AppEnv
import requests
import base64




app = Flask(__name__)


############### Step 1: Read the environment variables ###############

env = AppEnv()
uaa_service = env.get_service(name='cf-admincockpit-xsuaa')
dest_service = env.get_service(name='cf-admincockpit-destination')
#sUaaCredentials = dest_service.credentials["clientid"] + ':' + dest_service.credentials["clientsecret"]

sUaaCredentials = base64.b64encode("{}:{}".format(dest_service.credentials["clientid"] , dest_service.credentials["clientsecret"]).encode())
sDestinationName = 'sapglobaltrustlist'


#### Step 2: Request a JWT token to access the destination service ###

headers = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Basic {}".format(sUaaCredentials.decode('utf-8'))} 
form = [('client_id', dest_service.credentials["clientid"] ), ('grant_type', 'client_credentials')]
r = requests.post(uaa_service.credentials["url"] + '/oauth/token', data=form, headers=headers)


####### Step 3: Search your destination in the destination service #######

token = r.json()["access_token"]
headers= { 'Authorization': 'Bearer ' + token }
r = requests.get(dest_service.credentials["uri"] + '/destination-configuration/v1/destinations/'+sDestinationName, headers=headers)

############### Step 4: Access the destination securely ###############


destination = r.json()
print(destination)
token = destination["authTokens"][0]

githubUrl = destination["destinationConfiguration"]["URL"]
githubUsername = destination["destinationConfiguration"]["User"]
githubPassword = destination["destinationConfiguration"]["Password"]

print(githubPassword, githubPassword, githubUrl)

cf_port = os.getenv("PORT")
if __name__ == '__main__':
	if cf_port is None:
		app.run(host='0.0.0.0', port=5000, debug=True)
	else:
		app.run(host='0.0.0.0', port=int(cf_port), debug=True)
