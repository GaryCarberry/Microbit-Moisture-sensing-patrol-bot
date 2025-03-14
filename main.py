from microbit import *
from KitronikMOVEMotor import MOVEMotor
import music # imports the sound and buzzer library
import time #imports concept of time delays for the code
import radio#imports library that allows radio communication between two microbits
import log  #allows the microbit to log environmentla data over time
log.set_labels('temperature','sound','distance',timestamp=log.SECONDS)#set the headers for the csv file i will be reading from


# Initialize motors and line-following sensors
buggy=MOVEMotor()#creates the movemotor objecct from the kitronik movemotor class
left_sensor = pin2  # Left sensor connected to pin 2
right_sensor = pin1  # Right sensor connected to pin 1
trigger=pin13# echo pin was found at pin 13, these dont have to be initialised but it helps make the code easier to read
echo=pin14
# Threshold values for detecting the line (calibrate these)
BLACK_THRESHOLD = 200  # Sensor reading for the line (which is black)
WHITE_THRESHOLD = 700  # Sensor reading for the background (which is white)
MIDPOINT = (BLACK_THRESHOLD + WHITE_THRESHOLD) // 2
light=display.read_light_level()#light is assigned to the current light level for comparison
# Set up the radio
radio.config(group=1)  # Ensure both devices use the same group
radio.on()#radio is turned on and available for communication

def get_distance(timeout_ms=50):#added a timeout to prevent infinite passing
    """Measure distance using the ultrasonic sensor with a timeout."""
    trigger.write_digital(0)
    time.sleep_us(2)
    trigger.write_digital(1)
    time.sleep_us(10)
    trigger.write_digital(0)
    
    # Start waiting for echo signal with a timeout
    start_wait = time.ticks_ms()
    while echo.read_digital() == 0:
        if time.ticks_diff(time.ticks_ms(), start_wait) > timeout_ms:
            print("Timeout waiting for echo signal to start")
            return float('inf')  # Return an infinite distance if timeout occurs
    
    start_time = time.ticks_us()
    
    # Wait for the echo signal to go low with a timeout
    start_wait = time.ticks_ms()
    while echo.read_digital() == 1:
        if time.ticks_diff(time.ticks_ms(), start_wait) > timeout_ms:
            print("Timeout waiting for echo signal to stop")
            return float('inf')  # Return an infinite distance if timeout occurs
    
    end_time = time.ticks_us()
    duration = time.ticks_diff(end_time, start_time)
    distance = (duration / 2) / 29.1  # Calculate distance in cm
    return distance

    
@run_every(s=15)
def log_data():
    
    sound=microphone.sound_level()#initialised here so its easier for the microbit to log it 
    log.add({
      'temperature': temperature(),#uses the following sensore to upload to the MY_DATA file in the microbit
      'sound': sound,
      'distance':get_distance()
    })
    
# Function to read the sensor values
def read_sensors():
    left = left_sensor.read_analog()
    right = right_sensor.read_analog()
    return left, right

def transition_led_and_buzzer():
    # Define color tuples for red, orange, and green
    red = (255, 0, 0)
    orange = (255, 165, 0)
    green = (0, 255, 0)

    off = (0, 0, 0)
    # Define buzzer tones (using music notes for better compatibility)
    red_tone = 'c'  # Low tone for red (C note)
    orange_tone = 'd'  # Medium tone for orange (D note)
    green_tone = 'e'  # High tone for green (E note)

    # Set LEDs to red and play low tone
    buggy.setLEDs(red)  # Set LEDs to red
    buggy.showLEDs()    # Update LED display
    pin0.write_digital(1)  # Turn on buzzer
    music.play(red_tone, wait=True, pin=pin0)  # Play red tone (C note)
    pin0.write_digital(0)  # Turn off buzzer
    sleep(1000)         # Keep red for 1 second

    # Set LEDs to orange and play medium tone
    buggy.setLEDs(orange)  # Set LEDs to orange
    buggy.showLEDs()       # Update LED display
    pin0.write_digital(1)  # Turn on buzzer
    music.play(orange_tone, wait=True, pin=pin0)  # Play orange tone (D note)
    pin0.write_digital(0)  # Turn off buzzer
    sleep(1000)            # Keep orange for 1 second

    # Set LEDs to green and play high tone
    buggy.setLEDs(green)   # Set LEDs to green
    buggy.showLEDs()       # Update LED display
    pin0.write_digital(1)  # Turn on buzzer
    music.play(green_tone, wait=True, pin=pin0)  # Play green tone (E note)
    pin0.write_digital(0)  # Turn off buzzer
    sleep(1000)            # Keep green for 1 second
    buggy.setLEDs(off)
    buggy.showLEDs()
# Line-following routine
def line_follow():
    SPEED = 80  # Base motor speed
    ADJUST = 60  # Adjustment factor for proportional control

    while True:
        
        left, right = read_sensors()
      
        
        
        #constantly checks the distance to be prepared to act on the distance should it go below 8.5cm
        distance=get_distance()
        if distance<=8.5:
            work_out()
            take_moisture()  
        # Case 1: Both sensors on the line (straight path)
        if left < MIDPOINT and right < MIDPOINT:
            buggy.motorOn("l", "f", SPEED)
            buggy.motorOn("r", "f", SPEED)

        # Case 2: Off to the left (right sensor on the line)
        elif left > MIDPOINT and right < MIDPOINT:
            buggy.motorOn("l", "f", SPEED - ADJUST)
            buggy.motorOn("r", "f", SPEED + ADJUST)

        # Case 3: Off to the right (left sensor on the line)
        elif right > MIDPOINT and left < MIDPOINT:
            buggy.motorOn("l", "f", SPEED + ADJUST)
            buggy.motorOn("r", "f", SPEED - ADJUST)

        # Case 4: Lost the line, need to search for it
        else:
            buggy.motorOff("l")
            buggy.motorOff("r")
            if not search_for_line():
                print("Handing over to radio control...")
                radio_recovery()

        sleep(50)
        
# Attempt to find the line independently
def search_for_line():
    light_level = display.read_light_level()
 
    
    
    if light_level < 50:
        SEARCH_SPEED = 70  # Slower search speed in low light
    else:
        SEARCH_SPEED = 90  # Faster search speed in normal light

    ATTEMPT_DURATION = 0.8  # Time for each attempt (seconds)

  
    
    # First attempt: Spin left
    print("Attempting to find line: Left")
    buggy.motorOn("l", "r", SEARCH_SPEED)
    buggy.motorOn("r", "f", SEARCH_SPEED)
    start_time = running_time()
    while running_time() - start_time < ATTEMPT_DURATION * 1000:
        left, right = read_sensors()
        if left < MIDPOINT or right < MIDPOINT:#if it finds a line itll return to its regular line following
            print("Line found during left search.")
            buggy.motorOff("l")
            buggy.motorOff("r")
            return True

    # Second attempt: Spin right
    print("Attempting to find line: Right")
    buggy.motorOn("l", "f", SEARCH_SPEED)
    buggy.motorOn("r", "r", SEARCH_SPEED)
    start_time = running_time()
    while running_time() - start_time < ATTEMPT_DURATION * 1000:
        left, right = read_sensors()
        if left < MIDPOINT or right < MIDPOINT:
            print("Line found during right search.")
            buggy.motorOff("l")
            buggy.motorOff("r")
            return True

    # If both attempts fail
    print("Failed to find line independently.")
    buggy.motorOff("l")
    buggy.motorOff("r")
    return False
    #radio.recovery
# Radio recovery mechanism
def radio_recovery():
    print("Waiting for radio signal...")
    while True:
        message = radio.receive()
        if message == "A":  # Turn left to search for the line
            print("Turning left (radio control)...")
            buggy.motorOn("l", "r", 50)
            buggy.motorOn("r", "f", 50)
            sleep(200)  # Adjust timing as needed
        elif message == "B":  # Turn right to search for the line
            print("Turning right (radio control)...")
            buggy.motorOn("l", "f", 50)
            buggy.motorOn("r", "r", 50)
            sleep(200)  # Adjust timing as needed

        # Check sensors to see if the line has been found
        left, right = read_sensors()
        if left < MIDPOINT or right < MIDPOINT:
            print("Line found! Resuming...")
            buggy.motorOff("l")
            buggy.motorOff("r")
            return  # Exit radio recovery and resume line-following

# Movement functions
def move_forward(duration=0.2):
    buggy.motorOn("l", "f", 80)
    buggy.motorOn("r", "f", 80)
    time.sleep(duration)
    buggy.motorOff("l")
    buggy.motorOff("r")
#the idea of this function is to turn based on where the shortest distance is within the array
def turn_left(angle=10):#this and the turn right function have a default angle of 10, this will change based on the tangentmaking function
    turn_time = angle / 90  # Adjusted based on motor calibration
    buggy.motorOn("l", "r", 50)
    buggy.motorOn("r", "f", 50)
    time.sleep(turn_time)
    buggy.motorOff("l")
    buggy.motorOff("r")

def turn_right(angle=10):
    turn_time = angle / 90  # Adjust based on motor calibration
    buggy.motorOn("l", "f", 50)
    buggy.motorOn("r", "r", 50)
    time.sleep(turn_time)
    buggy.motorOff("l")
    buggy.motorOff("r")

def take_moisture():
    #reverse function to take mositure and to return to its original place
    buggy.motorOn("l", "r", 54)#difference in left motor speed is to account for the threading on the two motors
    buggy.motorOn("r", "r", 50)
    time.sleep(1)  # Adjust timing for precise 90° turn
    buggy.motorOff("l")
    buggy.motorOff("r")

def turn_180():
    # turns 180 degrees after trial and error
    buggy.motorOn("l", "f", 85.5)
    buggy.motorOn("r", "r", 85.5)
    time.sleep(0.75)  # Adjusted timing for precise 180° turn
    buggy.motorOff("l")
    buggy.motorOff("r")

def find_corners():
    distances_left = []#creates an array for when the buggy turns left to find the corner
    distances_right = []#creates an array for when the buggy turns right to find the corner

    # Find left corner
    for _ in range(18):  # Adjust steps for finer turns
        turn_left(10)  # Turn incrementally
        distance = get_distance()#takes distance bit by bit to add to the array
        distances_left.append(distance)#adds it to the end of the array
        if len(distances_left) > 1 and distance > distances_left[-2] + 5:  # if theres a Significant increase the cfunction will break and the array is set
            break

    # same logic in the right corner finder
    for _ in range(18):  # Adjust steps for finer turns
        turn_right(10)  # Turn incrementally
        distance = get_distance()
        distances_right.append(distance)
        if len(distances_right) > 1 and distance > distances_right[-2] + 5:  # Significant increase
            break

    # Combine and find smallest distance
    all_distances = distances_left + distances_right
    smallest_distance = min(all_distances)
    index_of_min = all_distances.index(smallest_distance)

    # Determine direction to orient
    if index_of_min < len(distances_left):
        direction = "left"
        angle_to_turn = index_of_min * 10  # Angle proportional to index
    else:
        direction = "right"
        angle_to_turn = (index_of_min - len(distances_left)) * 10

    return direction, angle_to_turn

def work_out():#this is the actuating function f the tangent maker
    distance = get_distance()# when within the distance an obstacle is detected
    print(distance)
    if distance <= 10:  # Obstacle detected
        direction, angle = find_corners()#begins to find the corners 

        # Turn towards the shortest length in an effort to  be perpandicular to the obstacle
        if direction == "left":
            turn_left(angle)
        elif direction == "right":
            turn_right(angle)

        turn_180()
# Main loop
while True:
    # Check for loud noise
    
    msg=radio.receive()
    if microphone.current_event()==SoundEvent.LOUD:#actuvates based on sound
        print("Loud noise detected. Beginning patrol")
        transition_led_and_buzzer()  
        line_follow() 
    
       
    
    sleep(100)
