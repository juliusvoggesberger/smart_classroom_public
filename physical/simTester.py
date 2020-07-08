import numpy

import matplotlib.pyplot as plt
import school
import plotter
from simulation import environment
import simulation
import planning

def set_actuator(envir, msg):
    actuator = msg['actuator']
    value = msg['status']
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

def set_lessons(envir, msg):
    subject = msg['subject']
    teacher = msg['teacher']
    school.SUBJECT_DICT[subject].set_active_teacher(teacher)








plöt = plotter.plot()
envir = environment()
envir.set_planning(0)
temperature_list = []
for day in range(112):
    envir.update()
    temperature_list.append(envir.return_teacher_temperature())
    plöt.update(envir)
    for daytime in range(95):
        envir.update()
        temperature_list.append(envir.return_teacher_temperature())
        plöt.update(envir)
plöt.reset()



envir = environment()
envir.set_planning(1)
for day in range(112):
    envir.update()
    plöt.update(envir)
    for daytime in range(95):
        envir.update()
        plöt.update(envir)
plöt.reset()



plan = planning.Planner()

envir = environment()
envir.set_planning(2)
for day in range(112):
    envir.update()
    actuator_planning = plan.sensor_planning((1577836800 + envir.time * int(24 / envir.day_length * 60) * 60), simulation.get_sensor_data(envir))
    for item in actuator_planning:
        set_actuator(envir, item)
    teacher_planning = plan.teacher_planning(school.get_subject_data(envir.get_today_slots()), school.get_teacher_data())
    for slot in teacher_planning:
        # if changes
        if teacher_planning[slot][1]:
            msg = {'subject': teacher_planning[slot][0], 'teacher': teacher_planning[slot][2], 'slot': str(slot)}
            set_lessons(envir, msg)
    plöt.update(envir)
    for daytime in range(95):
        envir.update()
        actuator_planning = plan.sensor_planning((1577836800 + envir.time * int(24 / envir.day_length * 60) * 60), simulation.get_sensor_data(envir))
        for item in actuator_planning:
            set_actuator(envir, item)
        plöt.update(envir)
plöt.save_plots(envir)