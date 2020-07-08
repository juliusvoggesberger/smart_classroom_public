import numpy

import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as matpdf
import school
import json
from simulation import environment
import simulation


class plot:
    def __init__(self):
        self.time_list = []
        self.temp_out_list = []
        self.temp_in_list_dict = dict({0: [], 1: [], 2: []})
        self.humidity_out_list = []
        self.humidity_in_list_dict = dict({0: [], 1: [], 2: []})
        self.light_out_list = []
        self.light_in_list_dict = dict({0: [], 1: [], 2: []})
        self.light_board_list_dict = dict({0: [], 1: [], 2: []})

        self.temp_dif_list_dict = dict({0: [], 1: [], 2: []})
        self.humid_in_dif_list_dict = dict({0: [], 1: [], 2: []})
        self.light_in_dif_list_dict = dict({0: [], 1: [], 2: []})
        self.light_board_dif_list_dict = dict({0: [], 1: [], 2: []})
        self.replacement_error_list_dict = dict({0: [], 1: [], 2: []})
        self.radiator_use_time_dict = dict({0: [], 1: [], 2: []})
        self.ac_use_time_dict = dict({0: [], 1: [], 2: []})
        self.humidifier_use_time_dict = dict({0: [], 1: [], 2: []})

        self.planning = -1

    def reset(self):
        self.time_list = []
        self.temp_out_list = []
        self.humidity_out_list = []
        self.light_out_list = []

    def update(self, envir):
        self.time_list.append(envir.time)
        self.temp_out_list.append(envir.temp_out)
        self.temp_in_list_dict[envir.planning].append(envir.temp_in)
        self.light_out_list.append(envir.light_out)
        self.light_in_list_dict[envir.planning].append(envir.light_in)
        self.light_board_list_dict[envir.planning].append(envir.light_board)
        self.humidity_in_list_dict[envir.planning].append(envir.humidity_in)
        self.humidity_out_list.append(envir.humidity_out)

        temp_dif, humid_in_dif, light_in_dif, light_board_dif, replacement_error = envir.error()
        self.temp_dif_list_dict[envir.planning].append(temp_dif)
        self.humid_in_dif_list_dict[envir.planning].append(humid_in_dif)
        self.light_in_dif_list_dict[envir.planning].append(light_in_dif)
        self.light_board_dif_list_dict[envir.planning].append(light_board_dif)
        self.replacement_error_list_dict[envir.planning].append(replacement_error)
        if len(self.radiator_use_time_dict[envir.planning]) != 0:
            self.radiator_use_time_dict[envir.planning].append(
                self.radiator_use_time_dict[envir.planning][-1] + envir.radiators)
            self.ac_use_time_dict[envir.planning].append(self.ac_use_time_dict[envir.planning][-1] + envir.air_cond)
            self.humidifier_use_time_dict[envir.planning].append(
                self.humidifier_use_time_dict[envir.planning][-1] + envir.humidifier)
        else:
            self.radiator_use_time_dict[envir.planning].append(0)
            self.ac_use_time_dict[envir.planning].append(0)
            self.humidifier_use_time_dict[envir.planning].append(0)

    def save_plots(self, envir):
        pdf = matpdf.PdfPages("Planning.pdf")
        plt.figure(figsize=[20, 24])

        plt.subplot(321)
        plt.plot(self.time_list, self.temp_out_list)
        plt.legend("Temperature outside")
        plt.title("Temperature outside")
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")
        plt.ylabel("Temperature in C°")

        plt.ylim(-10, 50)

        plt.subplot(322)
        plt.plot(self.time_list, self.temp_in_list_dict[0])
        plt.plot(self.time_list, self.temp_in_list_dict[1])
        plt.plot(self.time_list, self.temp_in_list_dict[2])
        plt.legend(["No planning", "Simple planning", "Our planning"])
        plt.title("Temperature inside")
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")
        plt.ylabel("Temperature in C°")
        plt.ylim(-10, 50)

        plt.subplot(323)
        plt.plot(self.time_list, self.humidity_out_list)
        plt.title("Humidity outside")
        plt.ylim(0, 100)
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")
        plt.ylabel("relative air humidity in %")

        plt.subplot(324)
        plt.plot(self.time_list, self.humidity_in_list_dict[0])
        plt.plot(self.time_list, self.humidity_in_list_dict[1])
        plt.plot(self.time_list, self.humidity_in_list_dict[2])
        plt.legend(["No planning", "Simple planning", "Our planning"])
        plt.title("Humidity inside")
        plt.ylabel("Relative air humidity")
        plt.ylim(0, 50)
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")

        plt.subplot(325)
        plt.plot(self.time_list, self.light_out_list)
        plt.title("Light outside")
        plt.ylim(0, 20000)
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")
        plt.ylabel("Light level in Lux")

        plt.subplot(326)
        plt.plot(self.time_list, self.light_in_list_dict[0])
        plt.plot(self.time_list, self.light_in_list_dict[1])
        plt.plot(self.time_list, self.light_in_list_dict[2])
        plt.legend(["No planning", "Simple planning", "Our planning"])

        plt.title("Light inside")
        plt.ylim(0, 20000)
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")
        plt.ylabel("Light level in Lux")

        pdf.savefig()
        plt.figure(figsize=[30, 24])
        plt.subplot(321)
        days = range(envir.season_length * 4)
        avg_dict = [[], [], []]
        for day in days:
            avg_dict[0].append(0)
            avg_dict[1].append(0)
            avg_dict[2].append(0)
            counter0 = 0
            counter1 = 0
            counter2 = 0
            for unit in range(day * envir.day_length, day * envir.day_length + envir.day_length):
                if self.temp_dif_list_dict[0][unit] != 0:
                    avg_dict[0][day] += self.temp_dif_list_dict[0][unit]
                    counter0 += 1
                if self.temp_dif_list_dict[1][unit] != 0:
                    avg_dict[1][day] += self.temp_dif_list_dict[1][unit]
                    counter1 += 1
                if self.temp_dif_list_dict[2][unit] != 0:
                    avg_dict[2][day] += self.temp_dif_list_dict[2][unit]
                    counter2 += 1
            avg_dict[0][day] = avg_dict[0][day] / max(counter0, 1)
            avg_dict[1][day] = avg_dict[1][day] / max(counter1, 1)
            avg_dict[2][day] = avg_dict[2][day] / max(counter2, 1)
        plt.bar([float(num) - 0.15 for num in days], avg_dict[0], width=0.2)
        plt.bar([float(num) + 0.1 for num in days], avg_dict[1], width=0.2)
        plt.bar([float(num) + 0.35 for num in days], avg_dict[2], width=0.2)
        plt.legend(["No planning", "Simple planning", "Our planning"])
        plt.title("Temperature difference")
        plt.ylim(-9, 4)
        plt.xticks(numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")

        plt.subplot(322)
        plt.plot(self.time_list, self.humid_in_dif_list_dict[0])
        plt.plot(self.time_list, self.humid_in_dif_list_dict[1])
        plt.plot(self.time_list, self.humid_in_dif_list_dict[2])
        plt.legend(["No planning", "Simple planning", "Our planning"])
        plt.title("humidity difference")
        plt.ylim(-40, 40)
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")

        plt.subplot(323)
        plt.plot(self.time_list, self.light_in_dif_list_dict[0])
        plt.plot(self.time_list, self.light_in_dif_list_dict[1])
        plt.plot(self.time_list, self.light_in_dif_list_dict[2])
        plt.legend(["No planning", "Simple planning", "Our planning"])
        plt.title("light difference")
        plt.ylim(-1000, 1000)
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")

        plt.subplot(324)
        plt.plot(self.time_list, self.light_board_dif_list_dict[0])
        plt.plot(self.time_list, self.light_board_dif_list_dict[1])
        plt.plot(self.time_list, self.light_board_dif_list_dict[2])
        plt.legend(["No planning", "Simple planning", "Our planning"])
        plt.title("Boardlight difference")
        plt.ylim(-1000, 1000)
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")

        plt.subplot(325)
        array = numpy.array(self.replacement_error_list_dict[0])
        print(numpy.count_nonzero(array == 0))
        plt.bar([-0.15, 1 - 0.15, 2 - 0.15, 3 - 0.15],
                [numpy.count_nonzero(array == 0) // 6, numpy.count_nonzero(array == 1) // 6,
                 numpy.count_nonzero(array == 2) // 6,
                 numpy.count_nonzero(array == 3) // 6],
                width=0.3)
        array = numpy.array(self.replacement_error_list_dict[2])
        plt.bar([0.15, 1 + 0.15, 2 + 0.15, 3 + 0.15],
                [numpy.count_nonzero(array == 0) // 6, numpy.count_nonzero(array == 1) // 6,
                 numpy.count_nonzero(array == 2) // 6,
                 numpy.count_nonzero(array == 3) // 6],
                width=0.3)
        plt.legend(["No planning", "Our planning"])
        plt.title("Teacher replacement Error")
        plt.xticks([0,1,2,3],["normal teacher", "Affine replacement", "not affine replacement", "No replacement"])
        plt.xlim(-0.5, 3.5)
        #plt.xlabel("Replacements")
        plt.ylabel("Amount of lessons")
        pdf.savefig()

        plt.figure(figsize=[20, 24])
        plt.subplot(311)
        plt.plot(self.time_list, self.radiator_use_time_dict[0])
        plt.plot(self.time_list, self.radiator_use_time_dict[1])
        plt.plot(self.time_list, self.radiator_use_time_dict[2])
        plt.legend(["No planning", "Simple planning", "Our planning"])
        plt.title("Radiator use time")
        plt.ylim(0, 3000)
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")
        plt.ylabel("Time in minutes")

        plt.subplot(312)
        plt.plot(self.time_list, self.ac_use_time_dict[0])
        plt.plot(self.time_list, self.ac_use_time_dict[1])
        plt.plot(self.time_list, self.ac_use_time_dict[2])
        plt.legend(["No planning", "Simple planning", "Our planning"])
        plt.title("AC use time")
        plt.ylim(0, 3000)
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")
        plt.ylabel("Time in minutes")

        plt.subplot(313)
        plt.plot(self.time_list, self.humidifier_use_time_dict[0])
        plt.plot(self.time_list, self.humidifier_use_time_dict[1])
        plt.plot(self.time_list, self.humidifier_use_time_dict[2])
        plt.legend(["No planning", "Simple planning", "Our planning"])
        plt.title("humidifier use time")
        plt.ylim(0, 3000)
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")
        plt.ylabel("Time in minutes")
        pdf.savefig()
        pdf.close()

        plt.figure(figsize=[12, 6])
        plt.bar([float(num) - 0.15 for num in days], avg_dict[0], width=0.2)
        plt.bar([float(num) + 0.1 for num in days], avg_dict[1], width=0.2)
        plt.bar([float(num) + 0.35 for num in days], avg_dict[2], width=0.2)
        plt.legend(["No planning", "Simple planning", "Our planning"])
        plt.ylim(-9, 4)
        plt.xticks(numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlim(1, 112)
        plt.xlabel("Day")
        plt.ylabel("Temperature difference in C°")
        plt.savefig("temp_diff.svg")

        plt.figure(figsize=[20, 24])
        plt.rcParams.update({"font.size": 18})
        plt.subplot(311)
        plt.plot(self.time_list, [num / 4 for num in self.radiator_use_time_dict[0]])
        plt.plot(self.time_list, [num / 4 for num in self.radiator_use_time_dict[1]])
        plt.plot(self.time_list, [num / 4 for num in self.radiator_use_time_dict[2]])
        plt.legend(["No planning", "Simple planning", "Our planning"])
        plt.title("Radiator use time")
        plt.xlim(0, envir.season_length * envir.day_length * 4)
        plt.ylim(0, 1600 / 4)
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")
        plt.ylabel("Time in hours")

        plt.subplot(312)
        plt.plot(self.time_list, [num / 4 for num in self.ac_use_time_dict[0]])
        plt.plot(self.time_list, [num / 4 for num in self.ac_use_time_dict[1]])
        plt.plot(self.time_list, [num / 4 for num in self.ac_use_time_dict[2]])
        plt.legend(["No planning", "Simple planning", "Our planning"])
        plt.title("AC use time")
        plt.xlim(0, envir.season_length * envir.day_length * 4)
        plt.ylim(0, 1600 / 4)
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")
        plt.ylabel("Time in hours")

        plt.subplot(313)
        plt.plot(self.time_list, [num / 4 for num in self.humidifier_use_time_dict[0]])
        plt.plot(self.time_list, [num / 4 for num in self.humidifier_use_time_dict[1]])
        plt.plot(self.time_list, [num / 4 for num in self.humidifier_use_time_dict[2]])
        plt.legend(["No planning", "Simple planning", "Our planning"])
        plt.title("Humidifier use time")
        plt.xlim(0, envir.season_length * envir.day_length * 4)
        plt.ylim(0, 1600 / 4)
        plt.xticks(envir.day_length * numpy.arange(1, 17) * 7, (numpy.arange(1, 17)) * 7)
        plt.xlabel("Day")
        plt.ylabel("Time in hours")
        plt.tight_layout(pad=6.0)
        plt.savefig("Use_time.svg")

        plt.figure(figsize=[12, 12])
        array = numpy.array(self.replacement_error_list_dict[0])
        print(numpy.count_nonzero(array == 0))
        plt.bar([-0.15, 1 - 0.15, 2 - 0.15, 3 - 0.15],
                [numpy.count_nonzero(array == 0) // 6, numpy.count_nonzero(array == 1) // 6,
                 numpy.count_nonzero(array == 2) // 6,
                 numpy.count_nonzero(array == 3) // 6],
                width=0.3)
        array = numpy.array(self.replacement_error_list_dict[2])
        plt.bar([0.15, 1 + 0.15, 2 + 0.15, 3 + 0.15],
                [numpy.count_nonzero(array == 0) // 6, numpy.count_nonzero(array == 1) // 6,
                 numpy.count_nonzero(array == 2) // 6,
                 numpy.count_nonzero(array == 3) // 6],
                width=0.3)
        plt.legend(["No planning", "Our planning"])
        plt.title("Teacher replacement Error")
        plt.xticks([0, 1, 2, 3], ["normal teacher", "Affine replacement", "not affine replacement", "No replacement"])
        plt.xlim(-0.5, 3.5)
        # plt.xlabel("Replacements")
        plt.ylabel("Amount of lessons")
        plt.savefig("TeacherReplacement.svg")