# From:Sherman Perry <sherman@shermnz.net>
# Based on: https://www.eclipse.org/paho/clients/python/
# Access from: https://cayenne.mydevices.com/shared/5db546374ed44e3f571c50e9

import os, csv, toml, datetime, sys
import paho.mqtt.client as mqtt
# from datetime import datetime

HomeDir =	os.environ['HOME']

# the IOT/LoRaReAd dir contains MQTTUtils.py
MQTTUpath =	os.path.join(HomeDir,'IOT/LoRaReAd')
sys.path.append(MQTTUpath)
from MQTTUtils import Save2CSV

ConfFile =	'/cayenneMQTT.txt'
LocPath = 	os.path.join(HomeDir,'CayMQTT')
CSVPath =	os.path.join(HomeDir,'CSVfiles')
CSV =		'.csv'
CrLf = 		'\r\n'
GeoFile =	'RSSILatLong'

ConfPathFile =	HomeDir+ConfFile

# How often shall we write values to Cayenne? (Seconds + 1)
Interval =      60

# Cayenne authentication info. This should be obtained from the Cayenne Dashboard,
#  and the details should be put into the file listed above.

# Read the Cayenne configuration stuff into a dictionary
ConfigDict = toml.load(ConfPathFile)
CayenneParam = ConfigDict.get('cayenne')
print (CayenneParam)

# Expected config
# [cayenne]
# CayUsername
# CayPassword
# CayClientID
# UniqueID

Subscribe	="v1/{}/things/{}/data/#".format( \
	CayenneParam.get('CayUsername'), \
	CayenneParam.get('CayClientID') )
# The subscribe string we  will send to Cayenne

# Prepare for creating an RSSI, Latitude, Longitude CSV - '22':'RSSI', removed 4 Jan 2020
ChannelMap = {'22':'RSSI','7':'LATwhole','8':'LAT','9':'LONGwhole','10':'LONG'}
LocationKeys = ['TIME', 'RSSI', 'LATwhole', 'LAT', 'LONGwhole', 'LONG']
# LocationKeys = ['RSSI', 'LAT', 'LONG']
Location = {}
# Location = {'TIME': '1'}
for key in ChannelMap:
    Location[ChannelMap[str(key)]] = None

# print(Subscribe)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(Subscribe)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic +"&"+ str(msg.payload))
    if "data" in str(msg.topic):
    # test just in case we get a message that is not data (I wonder what we should do with it?)
# eg msg: v1/6375a470-cff9-11e7-86d0-83752e057225/things/87456840-e0eb-11e9-a38a-d57172a4b4d4/data/2
#       Channel = str(msg.topic)[-2:]
       null,null,null,null,null,Channel = str(msg.topic).split(sep='/')
       null,Data = str(msg.payload).rstrip("'").split(sep='=')
       print("Parsed: ", Channel, Data )
       Save2CSV (CSVPath, CayenneParam.get('CayClientID'), Channel, Data)
       Location[ChannelMap[Channel]] = Data
       CurrentTime = datetime.datetime.now().isoformat()
       print( Location )
       if not any( LocationValues is None for LocationValues in Location.values()):
       # All values have valid content
           # Note when we assembled this tuple
           Location['TIME'] =	CurrentTime
           Location['RSSI'] = 	'0' # Don't currently have a valid RSSI value
           WHOLE = Location['LATwhole']
           Location['LAT'] =     WHOLE[0:len(WHOLE)-1] + Location['LAT'].rstrip('.0')
           WHOLE = Location['LONGwhole']
           Location['LONG'] = 	WHOLE[0:len(WHOLE)-1] + Location['LONG'].rstrip('.0')
           # Add the whole number
           print("Complete! ", Location, CrLf )
           LocOut = os.path.join(LocPath,GeoFile+CSV)
#           print( LocOut )
           if not os.path.isfile(LocOut):
           # There is not currently an output file
               print ("Creating new output file: "+LocOut)
               with open(LocOut, 'w') as LocFile:
                    writer = csv.DictWriter(LocFile, fieldnames=LocationKeys)
                    writer.writeheader()
           with open(LocOut, 'a') as LocFile:
               writer = csv.DictWriter(LocFile, fieldnames=LocationKeys)
               writer.writerow(Location)
           # Reset Location
           Location['LAT'] = None
           Location['LONG'] = None
#           Location = {'TIME': '1'}
#           for key in ChannelMap:
#              Location[ChannelMap[str(key)]] = None

    
#   if msg.topic.endswith("10") or msg.topic.endswith("11") or msg.topic.endswith("22"):
#   print("{0} {1}".format(msg.topic, str(msg.payload)))
#      print(msg.topic +"&"+ str(msg.payload))

client = mqtt.Client(client_id=CayenneParam.get('UniqueID') )
client.username_pw_set(CayenneParam.get('CayUsername'), \
	CayenneParam.get('CayPassword') )
client.on_connect = on_connect
client.on_message = on_message

client.connect("mqtt.mydevices.com", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

