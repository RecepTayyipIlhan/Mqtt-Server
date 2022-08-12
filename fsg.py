import random
import time
from paho.mqtt import client as mqtt_client
import pika
import os
import sys
import logging
import paho.mqtt.client as mqtt
import json
import csv
import random
from datetime import datetime
from init_fiireabse import service_firebase
from google.cloud.firestore import GeoPoint



USER =  'ardunio-uno-app@ttn'
PASSWORD = 'NNSXS.RULA2PAQCD2NARHWVHQRGM4FPBLBAK44EPXUFKA.NH6SOLAJGPISXTFGDEJJ2NBURFVS6GNFAQLBH5CZGLTTDWEAOTPA'
PUBLIC_TLS_ADDRESS = "eu1.cloud.thethings.network"
PUBLIC_TLS_ADDRESS_PORT = 8883
DEVICE_ID = "70B3D57ED0044718"
ALL_DEVICES = True
QOS = 0

DEBUG = False


def get_value_from_json_object(obj, key):
    try:
        return obj[key]
    except KeyError:
        return '-'


def stop(client):
    client.disconnect()
    print("\nExit")
    sys.exit(0)


# Write uplink to tab file
def save_to_file(some_json):
    end_device_ids = some_json["end_device_ids"]
    device_id = end_device_ids["device_id"]
    application_id = end_device_ids["application_ids"]["application_id"]
    received_at = some_json["received_at"]

    if 'uplink_message' in some_json:
        uplink_message = some_json["uplink_message"]
        f_port = get_value_from_json_object(uplink_message, "f_port")

        # check if f_port is found
        if f_port != '-':
            f_cnt = get_value_from_json_object(uplink_message, "f_cnt")
            frm_payload = uplink_message["frm_payload"]
            # If decoded_payload is a json object or a string "-" it will be converted to string
            decoded_payload = str(get_value_from_json_object(uplink_message, "decoded_payload"))
            rssi = get_value_from_json_object(uplink_message["rx_metadata"][0], "rssi")
            snr = get_value_from_json_object(uplink_message["rx_metadata"][0], "snr")
            data_rate_index = get_value_from_json_object(uplink_message["settings"], "data_rate_index")
            consumed_airtime = get_value_from_json_object(uplink_message, "consumed_airtime")

            # Daily log of uplinks
            now = datetime.now()
            path_n_file = now.strftime("%Y%m%d") + ".txt"
            #print(path_n_file)
            if not os.path.isfile(path_n_file):
                with open(path_n_file, 'a', newline='') as tabFile:
                    fw = csv.writer(tabFile, dialect='excel-tab')
                    fw.writerow(["received_at", "application_id", "device_id", "f_port", "f_cnt", "rssi", "snr",
                                 "data_rate_index", "consumed_airtime", "frm_payload", "decoded_payload"])

            with open(path_n_file, 'a', newline='') as tabFile:
                fw = csv.writer(tabFile, dialect='excel-tab')
                fw.writerow([received_at, application_id, device_id, f_port, f_cnt, rssi, snr,
                             data_rate_index, consumed_airtime, frm_payload, decoded_payload])
                dict_loc=(decoded_payload[1:-1])

                print(type(dict_loc))
                dict_loc = dict_loc[dict_loc.find(':')+3:-1]
                if dict_loc != "1":
                    dict_loc=dict_loc[:-4]
                    print(dict_loc)
                    print("x")
                    data = dict_loc.split(",")
                    user_id = data[0]
                    message_id = data[1]
                    lat = data[2]
                    lon = data[3]

                    lat = float(lat)
                    lon = float(lon)


                    location= GeoPoint(lat, lon)
                    print(dict_loc)
                    #print('loc :'+loc)
                    id = random.randint(10000,99999)
                    obj=service_firebase(user_id,message_id,location,str(id))

                    obj.init_firebase()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("\nConnected successfully to MQTT broker")
    else:
        print("\nFailed to connect, return code = " + str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, message):
    print("\nMessage received on topic '" + message.topic + "' with QoS = " + str(message.qos))

    parsed_json = json.loads(message.payload)

    if DEBUG:
        print("Payload (Collapsed): " + str(message.payload))
        print("Payload (Expanded): \n" + json.dumps(parsed_json, indent=4))

    save_to_file(parsed_json)


# mid = message ID
# It is an integer that is a unique message identifier assigned by the client.
# If you use QoS levels 1 or 2 then the client loop will use the mid to identify messages that have not been sent.
def on_subscribe(client, userdata, mid, granted_qos):
    print("\nSubscribed with message id (mid) = " + str(mid) + " and QoS = " + str(granted_qos))


def on_disconnect(client, userdata, rc):
    print("\nDisconnected with result code = " + str(rc))


def on_log(client, userdata, level, buf):
    print("\nLog: " + buf)
    logging_level = client.LOGGING_LEVEL[level]
    logging.log(logging_level, buf)


# Generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'

print("Create new mqtt client instance")
mqttc = mqtt.Client(client_id)

print("Assign callback functions")
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message
mqttc.on_disconnect = on_disconnect
# mqttc.on_log = on_log  # Logging for debugging OK, waste

# Setup authentication from settings above
mqttc.username_pw_set(USER, PASSWORD)

# IMPORTANT - this enables the encryption of messages
mqttc.tls_set()  # default certification authority of the system

# mqttc.tls_set(ca_certs="mqtt-ca.pem") # Use this if you get security errors
# It loads the TTI security certificate. Download it from their website from this page: 
# https://www.thethingsnetwork.org/docs/applications/mqtt/api/index.html
# This is normally required if you are running the script on Windows

print("Connecting to broker: " + PUBLIC_TLS_ADDRESS + ":" + str(PUBLIC_TLS_ADDRESS_PORT))
mqttc.connect(PUBLIC_TLS_ADDRESS, PUBLIC_TLS_ADDRESS_PORT, 60)


if ALL_DEVICES:
    print("Subscribe to all topics (#) with QoS = " + str(QOS))
    mqttc.subscribe("#", QOS)
elif len(DEVICE_ID) != 0:
    topic = "v3/" + USER + "/devices/" + DEVICE_ID + "/up"
    print("Subscribe to topic " + topic + " with QoS = " + str(QOS))
    mqttc.subscribe(topic, QOS)
else:
    print("Can not subscribe to any topic")
    stop(mqttc)


print("And run forever")
try:
    run = True
    while run:
        mqttc.loop(10)  # seconds timeout / blocking time
        print(".", end="", flush=True)  # feedback to the user that something is actually happening
except KeyboardInterrupt:
    stop(mqttc)