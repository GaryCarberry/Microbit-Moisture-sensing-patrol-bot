from microbit import *
from KitronikMOVEMotor import MOVEMotor
import music       # sound & buzzer
import time        # delays & ticks
import radio       # micro:bit radio
import log         # CSV environmental logging

# Set up radio group
radio.config(group=1)
radio.on()

class DataLogger:
    def __init__(self, bot):
        log.set_labels('temperature', 'sound', 'distance', timestamp=log.SECONDS)
        self.bot = bot

    @run_every(s=15)
    def log_data(self):
        sound_level = microphone.sound_level()
        self.bot.sensors.log.add({
            'temperature': temperature(),
            'sound': sound_level,
            'distance': self.bot.sensors.get_distance()
        })


class Sensors:
    BLACK_THRESHOLD = 200
    WHITE_THRESHOLD = 700
    MIDPOINT = (BLACK_THRESHOLD + WHITE_THRESHOLD) // 2

    def __init__(self):
        self.left_pin = pin2
        self.right_pin = pin1
        self.trigger = pin13
        self.echo = pin14

    def read_line(self):
        left = self.left_pin.read_analog()
        right = self.right_pin.read_analog()
        return left, right

    def get_distance(self, timeout_ms=50):
        # trigger pulse
        self.trigger.write_digital(0)
        sleep_us(2)
        self.trigger.write_digital(1)
        sleep_us(10)
        self.trigger.write_digital(0)

        start = time.ticks_ms()
        while self.echo.read_digital() == 0:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                return float('inf')

        t_start = time.ticks_us()
        start = time.ticks_ms()
        while self.echo.read_digital() == 1:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                return float('inf')

        duration = time.ticks_diff(time.ticks_us(), t_start)
        return (duration / 2) / 29.1  # cm


class Actuators:
    def __init__(self):
        self.buggy = MOVEMotor()
        self.buzzer = pin0

    def transition_led_and_buzzer(self):
        palette = [
            ((255, 0, 0), 'c'),
            ((255, 165, 0), 'd'),
            ((0, 255, 0), 'e')
        ]
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

    def turn_left(self, angle=90, speed=50):
        t = angle / 90
        self.buggy.motorOn('l','r', speed)
        self.buggy.motorOn('r','f', speed)
        sleep(t * 1000)
        self.stop()

    def turn_right(self, angle=90, speed=50):
        t = angle / 90
        self.buggy.motorOn('l','f', speed)
        self.buggy.motorOn('r','r', speed)
        sleep(t * 1000)
        self.stop()

    def turn_180(self):
        self.turn_left(180, speed=85)

    def take_moisture(self):
        # reverse ~90°
        self.buggy.motorOn('l','r',54)
        self.buggy.motorOn('r','r',50)
        sleep(1000)
        self.stop()


class Navigator:
    def __init__(self, sensors, actuators):
        self.s = sensors
        self.a = actuators

    def search_for_line(self):
        light = display.read_light_level()
        speed = 70 if light < 50 else 90
        duration = 0.8 * 1000

        # spin left
        self.a.buggy.motorOn('l','r', speed)
        self.a.buggy.motorOn('r','f', speed)
        start = running_time()
        while running_time() - start < duration:
            l, r = self.s.read_line()
            if l < self.s.MIDPOINT or r < self.s.MIDPOINT:
                self.a.stop()
                return True

        # spin right
        self.a.buggy.motorOn('l','f', speed)
        self.a.buggy.motorOn('r','r', speed)
        start = running_time()
        while running_time() - start < duration:
            l, r = self.s.read_line()
            if l < self.s.MIDPOINT or r < self.s.MIDPOINT:
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
        for _ in range(18):
            self.a.turn_left(10)
            d = self.s.get_distance()
            left_d.append(d)
            if len(left_d)>1 and d > left_d[-2] + 5:
                break

        # right scan
        for _ in range(18):
            self.a.turn_right(10)
            d = self.s.get_distance()
            right_d.append(d)
            if len(right_d)>1 and d > right_d[-2] + 5:
                break

        all_d = left_d + right_d
        i = all_d.index(min(all_d))
        if i < len(left_d):
            return 'left', i*10
        return 'right', (i-len(left_d))*10

    def work_out(self):
        distance = self.s.get_distance()
        if distance <= 10:
            dir_, ang = self.find_corners()
            if dir_ == 'left':
                self.a.turn_left(ang)
            else:
                self.a.turn_right(ang)
            self.a.turn_180()

    def line_follow(self):
        Speed, Adjustment = 80, 60
        while True:
            l, r = self.s.read_line()
            d = self.s.get_distance()
            if d <= 8.5:
                self.work_out()
                self.a.take_moisture()
            if l < self.s.MIDPOINT and r < self.s.MIDPOINT:
                self.a.move_forward(S)
            elif l > self.s.MIDPOINT:
                self.a.buggy.motorOn('l','f', Speed-Adjustment)
                self.a.buggy.motorOn('r','f', Speed+Adjustment)
            elif r > self.s.MIDPOINT:
                self.a.buggy.motorOn('l','f', Speed+Adjustment)
                self.a.buggy.motorOn('r','f', Speed-Adjustment)
            else:
                self.a.stop()
                if not self.search_for_line():
                    self.radio_recovery()
            sleep(50)


class PatrolBot:
    def __init__(self):
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