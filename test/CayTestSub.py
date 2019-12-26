#!/usr/bin/env python
import cayenne.client
import logging, toml, os

# Cayenne authentication info. This should be obtained from the Cayenne Dashboard.
# MQTT_USERNAME  = "MQTT_USERNAME"
# MQTT_PASSWORD  = "MQTT_PASSWORD"
# MQTT_CLIENT_ID = "MQTT_CLIENT_ID"

ConfFile = '/CicadacomPi3~f9ac.txt'
HomeDir =       os.environ['HOME']
ConfPathFile = HomeDir+ConfFile
# Read the Cayenne configuration stuff into a dictionary
ConfigDict = toml.load(ConfPathFile)
CayenneParam = ConfigDict.get('cayenne')
print (CayenneParam)

MQTT_USERNAME  = CayenneParam.get('CayUsername')
MQTT_PASSWORD  = CayenneParam.get('CayPassword')
MQTT_CLIENT_ID = CayenneParam.get('CayClientID')

# The callback for when a message is received from Cayenne.
def on_message(message):
    print("message received: " + str(message))
    # If there is an error processing the message return an error string, otherwise return nothing.

client = cayenne.client.CayenneMQTTClient()
client.on_message = on_message
# client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, loglevel=logging.INFO )
# For a secure connection use port 8883 when calling client.begin:
# client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, port=8883, loglevel=logging.INFO)
client.loop_forever()

