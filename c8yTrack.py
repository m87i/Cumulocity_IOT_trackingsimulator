import paho.mqtt.client as mqtt
import time, random, sys, json

receivedMessages = []

#simulated temperature measurements list
temperatures = ["22","25","26","28","30"]
#simulated humidity measurements list
humidities = ["50", "55","60, ""57"]

def on_message(client, userdata, message):
    print("Received Message: "+ str(message.payload))

def simulateTrack(trackfile):
    with open (trackfile) as f:
        trackdata = json.load(f)
#loop trough geojson structure
    for feature in trackdata["features"]:
        #lopp through coordinates
        for points in feature['geometry']['coordinates']:
            #generate MQTT standard message c8y_Temperature Measurement
            TemperatureMessage = '211, {temperature}'.format(temperature=temperatures[0])
            print('sending Temperature:' + temperatures[0])
            publish("s/us", TemperatureMessage)
            #generate MQTT customized message c8y_HumidityMeasurement Measurement
            HumidityMessage = '200, c8y_HumidityMeasurement, h, {humidity},%RH'.format(humidity=humidities[0])
            print('sending Humidity:' + humidities[0])
            publish("s/us", HumidityMessage)
            #generate MQTT position as location update (402)
            gpsPosition = '402,{latitude},{longitude},,'.format(latitude=points[1], longitude=points[0])
            print("Sending Position: "+ gpsPosition)
            #publish gps location update
            publish("s/us", gpsPosition)
            #shuffle temperature
            random.shuffle (temperatures)

            random.shuffle (humidities)
            #wait randomized betwen 2 and 5 sec
            time.sleep(random.randint(2, 5))

def publish (topic, message, waitForAck = False):
    mid = client.publish(topic, message, 2)[1]
    if (waitForAck):
        while mid not in receivedMessages:
            time.sleep(0.25)

def on_publish(client, userdata, mid):
    receivedMessages.append(mid)

def register_device (name):
    # Child device creation (101): 100, myDevice, myType
    publish("s/us", "100," + name + ", c8y_MQTTDevice")
    # Configure Hardware (110): 110, serialNumber ,model, revision
    publish("s/us","110, SN123456789, model1,0.8")
    # Set required availability (117): 117, Required Interval (min)
    publish("s/us","117,3")


if __name__ == "__main__":
    #open configuration JSON file
    with open('config.json') as json_file:
        config = json.load(json_file)
    #create MQTT client
    client = mqtt.Client(client_id="TrackingSimulator")
#set client authentication
client.username_pw_set(config["tenant-id"]+"/"+config["user-id"], config["pwd"])
#register message handlers
client.on_message = on_message
client.on_publish = on_publish
#connect to c8y tenant with MQTT    
client.connect("mqtt.us.cumulocity.com", 1883)
#subscribe to error topic
client.subscribe("s/e")
#loop client to receive error messages
client.loop_start()
#register device in Cumulocity
register_device("Tracking Simulator")
#start tracking simulation with downloaded geo-json-file from geojson.io
simulateTrack(config["trackfile"])
#stop looping
client.loop_stop()
#close client connection
client.disconnect()
