import random
import math
import numpy

import school


# time in [0,yearLength*dayLength] one unit is 24/dayLength hours, dayLength Units are a day, dayLength*yearLength a year.
# First season is spring. Summerest day on Day 1.5*seasonLength and winterest on day 3.5*seasonLength


class environment:

    def __init__(self):
        random.seed(1234)
        self.time = -1

        # Year parameters
        self.season_length = 28
        self.year_length = self.season_length * 4
        self.day_length = 96
        # Thermal conduction coefficient, usually not constant, but simplified in the simulation
        self.dif = 24 / self.day_length

        self.hottest_average_temp = 30.0
        self.coldest_average_temp = 0.0
        # Temperature change over the year is simulated linearly
        self.temperature_derivative = (self.hottest_average_temp - self.coldest_average_temp) / (self.year_length / 2)
        # Halved from actual value because it's inside not outside
        self.summer_sun_strength = 50000.0
        self.winter_sun_strength = 5000.0
        # light change over the year is simulated linearly
        self.light_derivative = (self.summer_sun_strength - self.winter_sun_strength) / (self.year_length / 2)

        # Actuators
        self.planning = 0
        self.manual = 0
        self.windows = 0
        self.shutters = 0.2
        self.air_cond = 0
        self.air_cond_temp = 18
        self.humidifier = 0
        self.radiators = 0
        self.radiator_temp = 24
        self.lamps = 0
        self.goal_temperature = 20

        # Weather
        self.temp_avg = 0
        self.clouds = 0
        self.temp_out = 0
        self.humidity_out = 0
        # LightSensors
        self.light_in = 0
        self.light_out = 0
        self.light_board = 0
        # Airqualitysensors
        self.temp_in = 20
        self.humidity_in = 40

        # Room values
        self.attendance = False
        self.attending_teacher = ""
        self.current_subject = ""

    def update(self):
        """Advances the simulation one timestep."""
        random.seed(1234 + 10 * self.time)
        self.time += 1
        day = (self.time % (self.day_length * self.year_length)) // self.day_length
        daytime = self.time % self.day_length
        # Day length from 1 (winter solstice) to 6 (summer solstice)
        summerSolsticeDistance = min(abs(day - 1.5 * self.season_length),
                                     1.5 * self.season_length + (self.year_length - day))
        sunny_length = 6 - 5 * summerSolsticeDistance / (self.year_length / 2)
        self.day_initialization()
        # Checks if there is an attended lesson
        self.current_subject = school.slot_to_subject(time_to_slot(self, self.time))
        self.attendance = False
        self.attending_teacher = ""
        if self.current_subject != "":
            if school.SUBJECT_DICT[self.current_subject].active_teacher != "":
                self.attendance = True
                self.attending_teacher = school.SUBJECT_DICT[self.current_subject].active_teacher
        # Sets actuators
        if self.manual <= 0:
            # No planning
            if self.planning == 0:
                self.teacher_action()
            # Simple planning
            elif self.planning == 1:
                self.simple_planning()
        else:
            self.manual -= 1
        # The next line is just a bell function around 12 (meaning brightest at 12) multiplied with both sun strength
        #         # and cloudiness
        self.light_out = math.exp(-(((daytime / self.day_length * 24 - 12) * 2) ** 2.0 / (sunny_length * 20.0))) * (
                self.summer_sun_strength - self.light_derivative * summerSolsticeDistance) * (
                                 28 ** (- self.clouds / 4.0))
        self.temp_out = self.temp_avg + (sunny_length * 1.25) ** 1.25 * math.exp(
            -(((daytime / self.day_length * 24 - 12) * 2) ** 2.0 / (sunny_length * 20.0))) - 5
        # Thermal conduction with "leaky windows"
        self.humidity_out = (self.clouds - 1) / 9 * 100
        self.humidity_in = self.humidity_in + self.dif * (self.humidity_out - self.humidity_in) * self.windows - \
                           self.radiators * self.dif * max(self.radiator_temp - self.temp_in, 0) / 2 + \
                           max(self.air_cond, self.humidifier) * self.dif * (40 - self.humidity_in) / 5
        self.humidity_in = max(self.humidity_in, 0)
        self.temp_in = self.temp_in + self.dif * (self.temp_out - self.temp_in) * (self.windows * 0.9 + 0.1) + \
                       self.air_cond * self.dif * min(self.air_cond_temp - self.temp_in, 0) + \
                       self.radiators * self.dif * max(self.radiator_temp - self.temp_in, 0)
        self.light_in = self.light_out * (28 ** (- self.shutters / .4)) + self.lamps
        self.light_board = (self.light_out * (28 ** (- self.shutters / .4))) ** 0.82

    def day_initialization(self):
        """If the environment daytime is 00:00, update daily environment parameters."""
        random.seed(1234 + 10 * self.time)
        day = (self.time % (self.day_length * self.year_length)) // self.day_length
        season = day // self.season_length
        summerSolsticeDistance = min(abs(day - 1.5 * self.season_length),
                                     1.5 * self.season_length + (self.year_length - day))
        dayLength = 6 - 5 * summerSolsticeDistance / (self.year_length / 2)
        if (self.time % self.day_length) == 0:
            # daily setup for average temperature, cloudiness and teacher sickness
            for teacher in school.TEACHER_DICT:
                school.TEACHER_DICT[teacher].set_sick()
                if school.TEACHER_DICT[teacher].sick:
                    for subject in school.TEACHER_DICT[teacher].subjects_taken:
                        school.SUBJECT_DICT[subject].set_active_teacher("")
                else:
                    for subject in school.TEACHER_DICT[teacher].subjects_taken:
                        school.SUBJECT_DICT[subject].set_active_teacher(teacher)
            self.temp_avg = self.hottest_average_temp - self.temperature_derivative * summerSolsticeDistance + random.uniform(
                -5.0, 5.0)

            if season < 1:
                # Spring has random weather "April, April..."
                self.clouds = random.randint(1, 10)
            elif season < 2:
                # Summer is either very sunny or very cloudy
                self.clouds = numpy.random.choice(numpy.arange(1, 11),
                                                  p=[0.4, 0.2, 0.1, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.18])
            elif season < 3:
                # Autumn is very cloudy
                self.clouds = math.ceil(random.triangular(0, 10, 8))
            elif season < 4:
                # Winter is cloudy
                self.clouds = math.ceil(random.triangular(0, 10, 5))

    def teacher_action(self):
        """Teachers turn on the radiators/AC when they are there and need it. They're turned off after the lesson."""
        if self.attending_teacher != "":
            self.goal_temperature = school.TEACHER_DICT[self.attending_teacher].ideal_temperature
            if self.temp_in > self.goal_temperature + 1:
                self.air_cond = 1
                self.radiators = 0
            elif self.temp_in < self.goal_temperature - 1:
                self.radiators = 1
                self.air_cond = 0
            else:
                self.air_cond = 0
                self.radiators = 0
            self.lamps = 500
            self.shutters = 0.2
        # Turn off all things + reset goal_temperature to default
        else:
            self.air_cond = 0
            self.radiators = 0
            self.goal_temperature = 20
            self.lamps = 0
            self.shutters = 0

    def simple_planning(self):
        """Simple planning that balances temperature around 21 and humidity around 40%.
           It's active between 06:00 (2h before the first slot at 8) and 17:15(When lessons end)."""
        daytime = self.time % self.day_length
        if 6 / (24 / self.day_length) < daytime < 17.25 / (24 / self.day_length):
            self.goal_temperature = 21
            if self.temp_in > self.goal_temperature + 1:
                self.air_cond = 1
                self.radiators = 0
            elif self.temp_in < self.goal_temperature - 1:
                self.radiators = 1
                self.air_cond = 0
            else:
                self.air_cond = 0
                self.radiators = 0
            if self.humidity_in < 30:
                self.humidifier = 1
            else:
                self.humidifier = 0
        else:
            self.air_cond = 0
            self.radiators = 0
            self.humidifier = 0

    def get_today_slots(self):
        """Returns the slots that might have a lesson."""
        weekday = (self.time % (7 * self.day_length)) // (self.day_length)
        if 0 <= weekday <= 4:
            return list(range(weekday * 5 + 1, weekday * 5 + 6))
        return []

    def set_windows(self, value):
        """0/1 for windows"""
        self.windows = value

    def set_air_cond(self, value):
        """0/1 for air conditioning"""
        self.air_cond = value

    def set_humidifier(self, value):
        """0/1 for humidifier"""
        self.humidifier = value

    def set_radiators(self, value):
        """Boolean for radiatiors"""
        self.radiators = value

    def change_shutters(self, value):
        """percentage from 0-1"""
        self.shutters = max(0, min(1, self.shutters + value))
        self.light_in = self.light_out * (self.season_length ** (- self.shutters / .4)) + self.lamps
        self.light_board = (self.light_out * (self.season_length ** (- self.shutters / .4))) ** (0.82)

    def set_lamps(self, value):
        """Boolean for lamps"""
        self.lamps = value
        self.light_in = self.light_out * (self.season_length ** (- self.shutters / .4)) + self.lamps

    def set_manual(self, value):
        """Blocks the actuators from automatic changes for value hours"""
        self.manual = self.day_length / 24 * value

    def set_goal_temperature(self, value):
        """Integer for temperature"""
        self.goalTemperature = value

    def set_planning(self, value):
        """ int for planning, 0 = no planning, 1 = simple planning, 2 = smart planning"""
        self.planning = value

    def error(self):
        """Returns temperature difference, humidity difference, Inner light difference, Board light difference, teacher replacement error"""
        if self.current_subject == "":
            teacher_replacement_error = -1
        else:
            # If no teacher is found: Error = 3
            if self.attending_teacher == "":
                teacher_replacement_error = 3
            elif school.SUBJECT_DICT[self.current_subject].teacher == self.attending_teacher:
                teacher_replacement_error = 0
            elif self.current_subject in school.TEACHER_DICT[self.attending_teacher].subjects:
                teacher_replacement_error = 1
            else:
                teacher_replacement_error = 2
        if self.attendance:
            return self.temp_in - school.TEACHER_DICT[
                self.attending_teacher].ideal_temperature, self.humidity_in - 40, self.light_in - 750, self.light_board - 250, teacher_replacement_error
        else:
            return 0, 0, 0, 0, teacher_replacement_error

    def return_teacher_temperature(self):
        if self.current_subject != "":
            return school.TEACHER_DICT[school.SUBJECT_DICT[self.current_subject].teacher].ideal_temperature
        else:
            return 0


def slot_to_time(envir, slot):
    """transforms lectureslots to startingtime"""
    if (0 < slot < 26):
        if ((slot - 1) % 5 < 3):
            return 8 * 60 / (24 * 60 / envir.dayLength) + ((slot - 1) % 5) * 1.75 / (24 / envir.dayLength)
        else:
            return 14 * 60 / (24 * 60 / envir.dayLength) + ((slot - 1) % 5 - 3) * 1.75 / (24 / envir.dayLength)
    else:
        print("non valid timeslot")


def time_to_slot(envir, time):
    day = (time % (7 * envir.day_length)) // envir.day_length
    day_time = (time % envir.day_length) * (24 / envir.day_length)
    if (day < 5):
        slot = (day % 5) * 5
        if (8 <= day_time < 9.5):
            slot += 1
        elif (9.75 <= day_time < 11.25):
            slot += 2
        elif (11.5 <= day_time < 13):
            slot += 3
        elif (14 <= day_time < 15.5):
            slot += 4
        elif (15.75 <= day_time < 17.25):
            slot += 5
        else:
            slot = 0
    else:
        slot = 0
    return slot


def get_sensor_data(environment):
    return {"light_in": environment.light_in - environment.lamps, "light_out": environment.light_out,
            "light_board": environment.light_board,
            "temp_in": environment.temp_in, "temp_out": environment.temp_out, "humidity_in": environment.humidity_in,
            "humidity_out": environment.humidity_out}
