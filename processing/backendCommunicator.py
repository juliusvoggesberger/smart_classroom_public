import paho.mqtt.client as mqtt

import json

import databaseCommunicator as dC

import planning


# MQTT
def on_mqtt_connect(client, userdata, flags, rc):
    client.subscribe('smart_classroom/backend/#')
    print("Connected to MQTT Broker")


def on_log(client, userdata, level, buff):
    print(buff)


def on_mqtt_disconnect(client, userdata, rc):
    print("Disconnected from MQTT Broker")


def on_mqtt_message(client, userdata, msg):
    print("new message")
    payload = json.loads(msg.payload.decode('UTF-8'))
    if msg.topic == "smart_classroom/backend/sensordata":
        send_data_to_database(payload)
        publish_action(client, payload)
    elif msg.topic != "smart_classroom/backend/lesson":
        print("not implemented topic" + msg.topic + " " + str(msg.payload))


def publish_action(client, data):
    """
    Receiving data from the physical layer, decide if an actuator status has to be changed.
    If yes the change will be published to the physical layer.
    Also each day the subjects of the day will be published. If any of the teachers are ill a replacement teacher will
    be searched and if found published to the physical layer and the web application
    :param client: The mqtt client
    :param data: The data which is published to the backend. It can have two forms:
                 Either the list will have a length of 2: [timestamp, sensor data]
                 Or it will have a length of 4: [timestamp, sensor data, subject data, teacher data]
    """
    # sensor planning
    actuator_planning = plan.sensor_planning(data[0], data[1])
    for item in actuator_planning:
        client.publish("smart_classroom/physical/actuators", json.dumps(item), qos=2)
    if len(data) > 2:
        teacher_planning = plan.teacher_planning(data[2], data[3])
        for slot in teacher_planning:
            # if changes
            if teacher_planning[slot][1]:
                msg = {'subject': teacher_planning[slot][0], 'teacher': teacher_planning[slot][2], 'slot': str(slot)}
                client.publish("smart_classroom/physical/lesson", json.dumps(msg), qos=2)
                client.publish("smart_classroom/backend/lesson", json.dumps(msg), qos=2)
                dC.send_data_to_influxdb(
                    {"measurement": "subject data", "tags": {"slot": str(slot), "subject": teacher_planning[slot][0]},
                     "time": data[0] + 1000,
                     "fields": {"teacher": teacher_planning[slot][2]}})


def send_data_to_database(data):
    """
    Receiving data from the physical layer and add it to the database.
    :param data: The data which is published to the backend. It can have two forms:
                 Either the list will have a length of 2: [timestamp, sensor data]
                 Or it will have a length of 4: [timestamp, sensor data, subject data, teacher data]
    """
    for key in data[1]:
        dC.send_data_to_influxdb({"measurement": "sensor data", "tags": {"sensor": key}, "time": data[0],
                                  "fields": {"value": data[1][key]}})
    if len(data) > 2:
        for slot in data[2]:
            dC.send_data_to_influxdb(
                {"measurement": "subject data", "tags": {"slot": str(slot), "subject": data[2][slot][0]}, "time": data[0],
                 "fields": {"teacher": data[2][slot][1]}})
            # Also send the new data to the frontend
            # msg = {'subject': data[2][slot][0], 'teacher': data[2][slot][1], 'slot': str(slot), 'time': data[0]}
            # client.publish("smart_classroom/backend/lesson", json.dumps(msg), qos=2)
        for teacher in data[3]:
            dC.send_data_to_influxdb({"measurement": "teacher data", "tags": {"teacher": teacher}, "time": data[0],
                                      "fields": {"sick": data[3][teacher]}})



plan = planning.Planner()
client = mqtt.Client()
client.username_pw_set("user", "pw")
client.connect("hostname", 1234, 56)
client.on_connect = on_mqtt_connect
client.on_message = on_mqtt_message

# subscribe to backend - contains sensor data
client.subscribe("smart_classroom/backend/#")

# Init database
dC.init_influxdb_database()
dC.get_info()

client.loop_forever()
