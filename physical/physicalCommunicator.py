import paho.mqtt.client as mqtt

import json
import time

from simulation import environment
import simulation
import school
import plotter

envir = environment()


# MQTT
def on_mqtt_connect(client, userdata, flags, rc):
    client.subscribe('smart_classroom/physical/#')
    print("Connected to MQTT Broker")


def on_log(client, userdata, level, buff):
    # print(buff)
    blea = False


def on_mqtt_disconnect(client, userdata, rc):
    print("Disconnected from MQTT Broker")


def on_mqtt_message(client, userdata, msg):
    # print(msg.topic)
    payload = json.loads(msg.payload.decode('UTF-8'))
    # print(msg.payload)
    if msg.topic == "smart_classroom/physical/actuators":
        # Expected: {'actuator': "window", 'status': 0}
        if envir.manual <= 0:
            set_actuator(payload)
    elif msg.topic == "smart_classroom/physical/lesson":
        # Expected: {'subject': "Fenster", 'teacher': "Null"}
        # print(payload)
        set_lessons(payload)
    elif msg.topic == "smart_classroom/physical/manual":
        # Guarantees that manual changes aren't overwritten for 1h
        envir.set_manual(1)
        set_actuator(payload)
    else:
        print("not implemented topic" + msg.topic + " " + str(msg.payload))


def set_actuator(msg):
    """
    Changes the actuator status
    :param msg: The mqtt message which holds the actuator and the status which have to be set.
                The message has the form { "actuator": actuator, "status": status}
    """
    actuator = msg['actuator']
    value = msg['status']
    # print("Actuator: " + actuator + "\nValue: " + str(value) + "\nType: " + str(type(value)))
    envir.set_planning(2)
    if actuator == 'window':
        # Value is either 0 (closed) or 1 (open)
        envir.set_windows(value)
    elif actuator == 'ac':
        # Value is either 0 (off) or 1 (on)
        envir.set_air_cond(value)
    elif actuator == 'radiators':
        # Value is either 0 (off) or 1 (on)
        envir.set_radiators(value)
    elif actuator == 'shutters':
        # Value is between 0 and 1
        envir.change_shutters(value)
    elif actuator == 'light':
        # Value is between 0 and 500
        envir.set_lamps(value)
    elif actuator == 'humidifier':
        envir.set_humidifier(value)


def set_lessons(msg):
    """
    Changes the values of a lesson
    :param msg: The mqtt message which holds the lesson/subject and the new teacher for this subject.
                The message has the form {"subject": subject, "teacher": teacher, "slot": slot}.
                The slot is of no importance for this setter.
    """
    subject = msg['subject']
    teacher = msg['teacher']
    school.SUBJECT_DICT[subject].set_active_teacher(teacher)


def publish_data(client, data):
    """
    Publishes the sensordata to the backend
    :param client: The mqtt client with which the message is published
    :param data: The data has the form {"light_in": light_in, "light_out": light_out, "light_board": light_board,
                "temp_in": temp_in, "temp_out": temp_out, "humidity_in": humidity_in, "humidity_out": humidity_out}
    """
    # Publish data to backend
    client.publish("smart_classroom/backend/sensordata", json.dumps(data), qos=2)


client = mqtt.Client()
client.on_connect = on_mqtt_connect
client.on_disconnect = on_mqtt_disconnect
client.on_message = on_mqtt_message
client.on_log = on_log
client.username_pw_set("user", "pw")
client.connect("hostname", 1234, 56)

# subscribe to physical - contains actuator commands


client.loop_start()
# The endless mqtt loop
# while True:
timeList = []
tempOutList = []
tempInList = []
lightOutList = []
lightInList = []

plöt = plotter.plot()
for slot in range(1, 26):
    subject = school.slot_to_subject(slot)
    if subject != "":
        msg = {'subject': subject, 'teacher': school.SUBJECT_DICT[subject].teacher, 'slot': str(slot)}
        client.publish("smart_classroom/backend/lesson", json.dumps(msg), qos=2)
for day in range(112):
    print(day)
    envir.update()
    # Creates arrays of data to send
    sensor_data = simulation.get_sensor_data(envir)
    subject_data = school.get_subject_data(envir.get_today_slots())
    teacher_data = school.get_teacher_data()
    # Data has format time,sensor data,subject data,teacher data
    data = [(1577836800 + envir.time * int(24 / envir.day_length * 60) * 60), sensor_data, subject_data,
            teacher_data]
    publish_data(client, data)
    plöt.update(envir)
    time.sleep(1)
    #if day % 7 == 6:
    #    for slot in range(1, 26):
    #        subject = school.slot_to_subject(slot)
    #        msg = {'subject': subject, 'teacher': school.SUBJECT_DICT[subject].teacher, 'slot': str(slot)}
    #        client.publish("smart_classroom/backend/lesson", json.dumps(msg), qos=2)
    for daytime in range(95):
        if daytime / envir.day_length *24 > 20:
            for slot in range(1, 26):
                subject = school.slot_to_subject(slot)
                if subject != "":
                    msg = {'subject': subject, 'teacher': school.SUBJECT_DICT[subject].teacher, 'slot': str(slot)}
                    client.publish("smart_classroom/backend/lesson", json.dumps(msg), qos=2)
        envir.update()
        sensor_data = [(1577836800 + envir.time * int(24 / envir.day_length * 60) * 60),
                       simulation.get_sensor_data(envir)]
        publish_data(client, sensor_data)
        plöt.update(envir)
        time.sleep(1)

plöt.save_plots(envir)
