import serial
from time import time, sleep
from copy import deepcopy

# 
CMD_START_TRANSMISSION = b'G'
CMD_END_TRANSMISSION = b'X'
CMD_LED_ON = b'I'
CMD_LED_OFF = b'O'

# SERIAL_START_TRANSMISSION = 'S'
SERIAL_END_TRANSMISSION = 'E\r\n'

filename = "arduino_buffer.txt"
SLEEP_ON_WRITE = True
SLEEP_ON_READ = False

MAX_SIZE = 16
SLEEP_TIME_AFTER_CMD = .01
SLEEP_TIME_BETWEEN_REQUESTS = .05  # .01

NUMBER_OF_VARIABLES = 8
SLIDER_RANGE = 150

DEFAULT = -10
sensors = [1000] * NUMBER_OF_VARIABLES  # save last inputs
max_vals = [1] * NUMBER_OF_VARIABLES
chosen_i = DEFAULT  # save last peak
UPPER_LIMIT = 40
LOWER_LIMIT = 50
circle_mode = False
wait_high = False
wait_low = False
cover_count = 0
num_rounds = 0
prev = 'c'
last_call = DEFAULT
STATIC = 0
COVER = 1
RIGHT_TURN = 2
LEFT_TURN = 3
COVER_OFF = 4
GO_BACK = 5
UNDERSCORE = 10

ser = serial.Serial('COM4', 9600)
# ser = serial.Serial('/dev/tty.usbmodem1411', 9600)  # left usb port
# ser = serial.Serial('/dev/tty.usbmodem1421', 9600)  # right usb port
sleep(3)
ser.flushInput()
sensor_data = [0] * NUMBER_OF_VARIABLES


def serial_input(start_transmission):
    if start_transmission:
        ser.reset_input_buffer()
        ser.write(CMD_START_TRANSMISSION)

    else:
        ser.write(CMD_END_TRANSMISSION)

    if SLEEP_ON_WRITE:
        sleep(SLEEP_TIME_AFTER_CMD)


def led_status(led_on):
    if led_on:
        ser.write(CMD_LED_ON)
    else:
        ser.write(CMD_LED_OFF)

    # if SLEEP_ON_WRITE:
    #     sleep(SLEEP_TIME_AFTER_CMD)


def get_serial_line():
    line = ser.readline().decode('ascii')
    if SLEEP_ON_READ:
        sleep(SLEEP_TIME_AFTER_CMD)
    return line


def get_serial_data():
    data = [0] * MAX_SIZE

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

    if len(new_data) == NUMBER_OF_VARIABLES:
        global sensor_data
        sensor_data = new_data

        return new_data

    else:
        pass
        # print("wrong number of variables (" + str(new_data.size) + ")")


# Plot parts from:
# https://gist.github.com/brandoncurtis/33a67d9d402973face8d
#
def main(output_file):
    while True:

        try:
            new_sensor_data = update_sensor_data()

        except ValueError as exception:
            print(exception)
            break

        except OverflowError as exception:
            print(exception)
            break

        # print(sensor_data)
        # print("writing data")
        # np.savetxt(output_file, sensor_data.reshape(1, sensor_data.size), fmt="%d", delimiter=",")

        file = open(output_file, "w+")
        gesture = read_gestures()
        normalized = [0] * NUMBER_OF_VARIABLES
        for i in range(NUMBER_OF_VARIABLES):
            normalized[i] = sensor_data[i] / max_vals[i] * SLIDER_RANGE
            normalized[i] = int(normalized[i])
            if normalized[i] < UNDERSCORE:
                normalized[i] = UNDERSCORE

        file.write(str(gesture) + "\n")
        str_data = ",".join(map(str, normalized))
        file.write(str_data)
        file.close()

        if gesture == COVER:
            led_status(False)
        elif gesture == COVER_OFF:
            led_status(True)

        sleep(SLEEP_TIME_BETWEEN_REQUESTS)

    ser.close()


def read_gestures():
    global chosen_i, circle_mode, wait_high, wait_low, num_rounds, prev, \
        max_vals, cover_count, last_call
    sensor_list = sensor_data
    high_count = 0
    low_count = 0
    cur_i = DEFAULT
    cur_value = 0

    for i in range(NUMBER_OF_VARIABLES):
        if sensor_list[i] > max_vals[i]:  # set max value of each sensor
            max_vals[i] = sensor_list[i]
        # count how many sensors have a big difference between last call
        # and this one
        if (sensor_list[i] - sensors[i]) >= UPPER_LIMIT:
            high_count += 1
            # remember the most dominant sensor
            if cur_value < sensor_list[i]:
                cur_value = sensor_list[i]
                cur_i = i
        if (sensors[i] - sensor_list[i]) >= LOWER_LIMIT:
            low_count += 1
        sensors[i] = sensor_list[i]
    if wait_low:
        if low_count >= 4:
            wait_low = False
            cover_count += 1
            if cover_count == 2:
                cover_count = 0
                print("COVER_OFF")
                return COVER_OFF
            else:
                wait_high = True
            return DEFAULT
    elif wait_high:
        if high_count >= 6:
            wait_high = False
            wait_low = True
            return DEFAULT

    if high_count == 1:
        circle_mode = True
        if chosen_i == DEFAULT:
            chosen_i = cur_i
        elif 0 < (cur_i - chosen_i) % (NUMBER_OF_VARIABLES - 1) <= 3:
            chosen_i = cur_i
            if prev != 'r':
                prev = 'r'
            print("RIGHT_TURN")
            last_call = RIGHT_TURN
            return RIGHT_TURN
        elif 0 < (chosen_i - cur_i) % (NUMBER_OF_VARIABLES - 1) <= 3:
            chosen_i = cur_i
            if prev != 'l':
                prev = 'l'
            print("LEFT_TURN")
            last_call = LEFT_TURN
            return LEFT_TURN
        return last_call

    if circle_mode:
        num_rounds += 1
        if num_rounds == 15:
            num_rounds = 0
            prev = 'c'
            chosen_i = DEFAULT
            circle_mode = False
        return last_call

    if (not circle_mode) and (not wait_high) and (not wait_low):
        if high_count >= 5:
            wait_low = True
            print("COVER")
            last_call = COVER
            return COVER
        elif high_count == 0:
            print("STATIC")
            last_call = STATIC
            return STATIC
    return DEFAULT


if __name__ == "__main__":
    # buffer = open(filename, "w+")
    main(filename)
    # buffer.close()
    # serial_input(True)
    # print(get_serial_line())
