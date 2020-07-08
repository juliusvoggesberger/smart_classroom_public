import numpy as np


class TemperaturePlanner:
    """plans the temperature according to the data from the previous year"""

    def __init__(self):
        self.y_goal = self.load("../processing/y_goal.txt")  # goal temperature last year

    def check_temperature(self, room_temp, time):
        env_time = int((time - 1577836800)/60/(int(24 / 96 * 60)))
        threshold = 1
        time_diff = 1
        # for cyclic year
        next_relevant_time = (env_time + 1) % (len(self.y_goal))
        # finds the next relevant slot
        while self.y_goal[next_relevant_time] == 0:
            next_relevant_time = (next_relevant_time + 1) % (len(self.y_goal))
            time_diff += 1
        difference = (self.y_goal[next_relevant_time] - room_temp) / time_diff
        if difference > threshold:
            # heater
            return 1
        elif difference < - threshold:
            # ac
            return -1
        return 0

    @staticmethod
    def load(file):
        """loads float np array from file"""
        text_file = open(file, "r")
        output = text_file.read().split(',')
        converted_output = np.array(output).astype(np.float)
        text_file.close()
        return converted_output

