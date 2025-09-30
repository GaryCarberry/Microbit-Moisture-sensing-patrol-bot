from microbit import *
from KitronikMOVEMotor import MOVEMotor
import music       # sound & buzzer
import time        # delays & ticks
import radio       # micro:bit radio
import log         # CSV environmental logging

# Set up radio group
radio.config(group=1)
radio.on()

class DataLogger:#Logs data concurrently in the microbit  every 15 seconds
    def __init__(self, bot):
        log.set_labels('temperature', 'sound', 'distance', timestamp=log.SECONDS)

    @run_every(s=15)#Built-in function tor run every15 seconds
    def log_data():
        sound_level = microphone.sound_level()#reads sound level at that moment
        log.add({
            'temperature': temperature(),
            'sound': sound_level,
            'distance': self.bot.sensors.get_distance()
        })


class Sensors:
    BLACK_THRESHOLD = 200#Thresholds to create a reltaionship between black and white for the sensor
    WHITE_THRESHOLD = 700
    MIDPOINT = (BLACK_THRESHOLD + WHITE_THRESHOLD) // 2

    def __init__(self):
        self.left_pin = pin2# initialisng sensor pins These two are for the line follow and are colour sensors
        self.right_pin = pin1
        self.trigger = pin13#Pins for ultrasonic sensor
        self.echo = pin14

    def read_line(self):
        left = self.left_pin.read_analog()#reading analog values to understand the orientation of the pins
        right = self.right_pin.read_analog()
        return left, right

    def get_distance(self, timeout_ms=50):
        # trigger pulse
        self.trigger.write_digital(0)#Begins an ultrasonic burst
        sleep_us(2)
        self.trigger.write_digital(1)
        sleep_us(10)
        self.trigger.write_digital(0)

        start = time.ticks_ms()
        while self.echo.read_digital() == 0:#Timeout if the signal doesnt come back
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                return float('inf')

        t_start = time.ticks_us()#when the echo signal begins
        start = time.ticks_ms()#when its reset to a new window
        while self.echo.read_digital() == 1:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:#if an echo is received continue to receive distance
                return float('inf')

        duration = time.ticks_diff(time.ticks_us(), t_start)#duration is the full round trip of the echo pulse and must be halved
        return (duration / 2) / 29.1  # cm


class Actuators:
    def __init__(self):
        self.buggy = MOVEMotor()#creates movemotor object defined in microbit ide
        self.buzzer = pin0

    def transition_led_and_buzzer(self):
        palette = [
            ((255, 0, 0), 'c'),
            ((255, 165, 0), 'd'),
            ((0, 255, 0), 'e')
        ]#list of colours in the built-inRGBs
        for color, tone in palette:
            self.buggy.setLEDs(color)
            self.buggy.showLEDs()
            self.buzzer.write_digital(1)
            music.play(tone, wait=True, pin=self.buzzer)
            self.buzzer.write_digital(0)
            sleep(1000)
        self.buggy.setLEDs((0,0,0))
        self.buggy.showLEDs()

    def move_forward(self, speed=80, duration=None):
        self.buggy.motorOn('l','f', speed)
        self.buggy.motorOn('r','f', speed)
        if duration:
            sleep(duration)
            self.stop()

    def stop(self):
        self.buggy.motorOff('l')
        self.buggy.motorOff('r')

    def turn_left(self, angle=90, speed=50):#Bit of trial and error coding her
        t = angle / 90# 90 degree turn occurs at speed 50 for 1 second as found through testing
        self.buggy.motorOn('l','r', speed)
        self.buggy.motorOn('r','f', speed)
        sleep(t * 1000)
        self.stop()

    def turn_right(self, angle=90, speed=50):#vice versa of turn_left
        t = angle / 90
        self.buggy.motorOn('l','f', speed)
        self.buggy.motorOn('r','r', speed)
        sleep(t * 1000)
        self.stop()

    def turn_180(self):
        self.turn_left(180, speed=85)

    def take_moisture(self):
        # creates a perfect 180 degree turn
        self.buggy.motorOn('l','r',54)
        self.buggy.motorOn('r','r',50)
        sleep(1000)
        self.stop()


class Navigator:
    def __init__(self, sensors, actuators):
        self.s = sensors
        self.a = actuators

    def search_for_line(self):
        light = display.read_light_level()# save power at nightime
        speed = 70 if light < 50 else 90
        duration = 800#timeout

        # spin left
        self.a.buggy.motorOn('l','r', speed)
        self.a.buggy.motorOn('r','f', speed)
        start = running_time()#since program began
        while running_time() - start < duration:#runs until running time exceeds timeour
            l, r = self.s.read_line()#left and right values of the respective sensor
            if l < self.s.MIDPOINT or r < self.s.MIDPOINT:
                self.a.stop()
                return True

        # spin right
        self.a.buggy.motorOn('l','f', speed)
        self.a.buggy.motorOn('r','r', speed)
        start = running_time()
        while running_time() - start < duration:
            l, r = self.s.read_line()
            if l < self.s.MIDPOINT or r < self.s.MIDPOINT:#stops when back on the line
                self.a.stop()
                return True

        self.a.stop()
        return False

    def radio_recovery(self):
        while True:
            msg = radio.receive()
            if msg == 'A':
                self.a.turn_left(10)
            elif msg == 'B':
                self.a.turn_right(10)
            l, r = self.s.read_line()
            if l < self.s.MIDPOINT or r < self.s.MIDPOINT:
                return

    def find_corners(self):
        left_d, right_d = [], []
        # left scan
        for _ in range(18):#moves left to find distance
            self.a.turn_left(10)
            d = self.s.get_distance()
            left_d.append(d)
            if len(left_d)>1 and d > left_d[-2] + 5:#Evaluates if there's a large drop off when it comes to distance checking
                break

        # right scan
        for _ in range(18):
            self.a.turn_right(10)
            d = self.s.get_distance()
            right_d.append(d)
            if len(right_d)>1 and d > right_d[-2] + 5:
                break

        all_d = left_d + right_d#combines lists
        i = all_d.index(min(all_d))#stores index of the smallest distance in the co,bined list
        if i < len(left_d):#if its in the left index move left to find the previous distance dpeendent on array position
            return 'left', i*10
        return 'right', (i-len(left_d))*10

    def work_out(self):
        distance = self.s.get_distance()
        if distance <= 10:
            dir_, ang = self.find_corners()#calls the direction and angle of the find_corners logic
            if dir_ == 'left':
                self.a.turn_left(ang)
            else:
                self.a.turn_right(ang)
            self.a.turn_180()

    def line_follow(self):#Code that brings the whole program together
        Speed, Adjustment = 80, 60
        while True:
            left, right = self.s.read_line()#reads the line constantly
            distance = self.s.get_distance()gets distance
            if distance <= 8.5:
                self.work_out()
                self.a.take_moisture()
            if left < self.s.MIDPOINT and r < self.s.MIDPOINT:
                self.a.move_forward(S)
            elif left > self.s.MIDPOINT:
                self.a.buggy.motorOn('l','f', Speed-Adjustment)
                self.a.buggy.motorOn('r','f', Speed+Adjustment)
            elif right > self.s.MIDPOINT:
                self.a.buggy.motorOn('l','f', Speed+Adjustment)
                self.a.buggy.motorOn('r','f', Speed-Adjustment)
            else:
                self.a.stop()
                if not self.search_for_line():
                    self.radio_recovery()
            sleep(50)


class PatrolBot:
    def __init__(self):#makes objects of all the classes 
        self.sensors = Sensors()
        self.actuators = Actuators()
        self.navigator = Navigator(self.sensors, self.actuators)
        self.logger = DataLogger(self)

    def run(self):
        while True:
            if microphone.current_event() == SoundEvent.LOUD:
                print("Loud noise detected. Beginning patrol")
                self.actuators.transition_led_and_buzzer()
                self.navigator.line_follow()
            sleep(100)


# Entry Point
bot = PatrolBot()

bot.run()
