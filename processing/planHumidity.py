import numpy as np


class HumidityPlanner:

    def __init__(self):
        self.y_goal = self.load("../processing/y_goal.txt")  # goal temperature last year
        self.upper_bound = 45
        self.lower_bound = 35

    def check_humidity(self, humidity, time):
        """checks if the humidity is in a given interval"""
        threshold = -2
        env_time = int((time - 1577836800) / 60 / (int(24 / 96 * 60)))
        next_relevant_time = (env_time + 1) % (len(self.y_goal))
        time_diff = 1
        # finds the next relevant slot
        while self.y_goal[next_relevant_time] == 0:
            next_relevant_time = (next_relevant_time + 1) % (len(self.y_goal))
            time_diff += 1
        difference = (humidity - ((self.upper_bound + self.lower_bound) / 2))/time_diff
        if difference > threshold:
            return 0
        else:
            return 1

    def load(self, file):
        """loads float np array from file"""
        text_file = open(file, "r")
        output = text_file.read().split(',')
        converted_output = np.array(output).astype(np.float)
        text_file.close()
        return converted_output


