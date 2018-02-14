
import serial
import numpy as np
from time import time, sleep
from matplotlib import pyplot as plt


CMD_START_TRANSMISSION = b'G'
CMD_END_TRANSMISSION = b'X'

# SERIAL_START_TRANSMISSION = 'S'
SERIAL_END_TRANSMISSION = 'E\r\n'

SLEEP_ON_WRITE = True
SLEEP_ON_READ = False

MAX_SIZE = 16
SLEEP_TIME_AFTER_CMD = .01
SLEEP_TIME_BETWEEN_REQUESTS = .05  # .01

NUMBER_OF_VARIABLES = 8
PLOT_ON = False


ser = serial.Serial('/dev/tty.usbmodem1411', 9600)  # left usb port
# ser = serial.Serial('/dev/tty.usbmodem1421', 9600)  # right usb port
sleep(3)
ser.flushInput()
sensor_data = np.zeros(NUMBER_OF_VARIABLES)


def serial_input(start_transmission):

    if start_transmission:
        ser.reset_input_buffer()
        ser.write(CMD_START_TRANSMISSION)

    else:
        ser.write(CMD_END_TRANSMISSION)

    if SLEEP_ON_WRITE:
        sleep(SLEEP_TIME_AFTER_CMD)


def get_serial_line():
    line = ser.readline().decode('ascii')
    if SLEEP_ON_READ:
        sleep(SLEEP_TIME_AFTER_CMD)
    return line


def get_serial_data():
    data = np.zeros(MAX_SIZE)

    serial_input(True)

    i = 0
    while True:
        line = get_serial_line()

        if line == "\n" or line == "\r\n":
            continue

        if line == SERIAL_END_TRANSMISSION:
            break

        if i == MAX_SIZE:
            serial_input(False)
            raise OverflowError("data overflow: stopping serial")

        try:
            curr_value = int(line)
            data[i] = curr_value
            i += 1

        except ValueError:
            raise ValueError("got non-number value (" + line + ")")

    return data[:i]


def update_sensor_data():

    try:
        new_data = get_serial_data()

    except ValueError as exception:
        raise exception

    except OverflowError as exception:
        raise exception

    if new_data.size == NUMBER_OF_VARIABLES:
        global sensor_data
        sensor_data = new_data

        return new_data

    else:
        pass
        # print("wrong number of variables (" + str(new_data.size) + ")")


# Plot parts from:
# https://gist.github.com/brandoncurtis/33a67d9d402973face8d
#
def main():

    if PLOT_ON:

        # set plot to animated
        plt.ion()
        # plt.interactive(True)

        start_time = time()
        timepoints = []
        ydata = []
        yrange = [-0.1, 5.1]
        view_time = 2  # seconds of data to view at once
        duration = 6  # total seconds to collect data

        fig1 = plt.figure()
        # http://matplotlib.org/users/text_props.html
        fig1.suptitle('live updated data', fontsize='18', fontweight='bold')
        plt.xlabel('time, seconds', fontsize='14', fontstyle='italic')
        plt.ylabel('potential, volts', fontsize='14', fontstyle='italic')
        plt.axes().grid(True)
        line1, = plt.plot(ydata, marker='o', markersize=4, linestyle='none', markerfacecolor='red')
        plt.ylim(yrange)
        plt.xlim([0, view_time])

        # fig1.show()

    run = True

    # collect the data and plot a moving frame
    while not PLOT_ON or run:

        try:
            new_sensor_data = update_sensor_data()

            if PLOT_ON:

                # store the entire dataset for later
                ydata.append(new_sensor_data * 5.0 / 1024)
                timepoints.append(time() - start_time)
                current_time = timepoints[-1]

                # update the plotted data
                line1.set_xdata(timepoints)
                line1.set_ydata(ydata)

                # slide the viewing frame along
                if current_time > view_time:
                    plt.xlim([current_time - view_time, current_time])

                # when time's up, kill the collect+plot loop
                if timepoints[-1] > duration:
                    run = False

                # update the plot
                fig1.canvas.draw()

                # plt.show(block=False)

        except ValueError as exception:
            print(exception)
            break

        except OverflowError as exception:
            print(exception)
            break

        print(sensor_data)
        sleep(SLEEP_TIME_BETWEEN_REQUESTS)

    if PLOT_ON:

        # plt.ioff()

        # plot all of the data you collected
        fig2 = plt.figure()
        # http://matplotlib.org/users/text_props.html
        fig2.suptitle('complete data trace', fontsize='18', fontweight='bold')
        plt.xlabel('time, seconds', fontsize='14', fontstyle='italic')
        plt.ylabel('potential, volts', fontsize='14', fontstyle='italic')
        plt.axes().grid(True)

        plt.plot(timepoints, ydata, marker='o', markersize=4, linestyle='none', markerfacecolor='red')
        plt.ylim(yrange)
        fig2.show()

        plt.show(block=True)

    ser.close()


if __name__ == "__main__":
    main()
    # serial_input(True)
    # print(get_serial_line())
