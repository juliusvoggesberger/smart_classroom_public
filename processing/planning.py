import planRoomTemperatureGradient
import planTeacherIndirectCSP
import planHumidity
import planLight

import school


class Planner:
    def __init__(self):
        self.temperature_planner = planRoomTemperatureGradient.TemperaturePlanner()
        self.humidity_planner = planHumidity.HumidityPlanner()
        self.teacher_dict = school.TEACHER_DICT  # ALL TEACHER
        self.subject_dict = school.SUBJECT_DICT

    def teacher_planning(self, data_subject, data_teacher):
        """organizes teachers for the whole day according to the csp/classical planning problem"""
        ret_dict = {}
        for slot in data_subject:
            li = planTeacherIndirectCSP.solve_csp(slot, data_teacher)
            ret_dict.update({slot: li})
        return ret_dict

    def sensor_planning(self, time, data):
        """runs planning on the sensordata and returns recommended values for the actuators"""
        light = data['light_in']
        light_board = data['light_board']
        room_humidity = data['humidity_in']
        outside_humidity = data['humidity_out']
        room_temp = data['temp_in']
        outside_temp = data['temp_out']
        ac = 0
        radiators = 0
        hum = 0
        windows = 0
        if (room_temp < 19 < outside_temp or room_temp > 23 > outside_temp):
            if (room_humidity < 30 < outside_humidity or room_humidity > 50 > outside_humidity):
                windows = 1
        lamp, shut = planLight.check_light(light, light_board)
        if self.temperature_planner.check_temperature(room_temp, time) == 1:
            radiators = 1
        elif self.temperature_planner.check_temperature(room_temp, time) == -1:
            ac = 1
        if ac == 0:
            hum = self.humidity_planner.check_humidity(room_humidity, time)
        return [{'actuator': "window", 'status': windows}, {"actuator": 'shutters', "status": shut}, {"actuator": 'light', "status": lamp},
                {"actuator": 'humidifier', "status": hum}, {"actuator": 'radiators', "status": radiators},
                {"actuator": 'ac', "status": ac}]
