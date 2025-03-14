# Microbit-Moisture-sensing-patrol-bot
This project utilizes the BBC micro:bit to create a patrol bot capable of sensing soil moisture levels. The bot uses a fitted line follow sensor as well as an ultrasonic distance sensor to interact with its environment, providing valuable data for applications such as plant care and agricultural monitoring.

Results of sensor can be found on https://thingspeak.mathworks.com/channels/2764298/private_show

Features
Soil Moisture Detection: Utilizes a soil moisture sensor to detect the moisture level in the soil.
Patrolling Capability: Incorporates infrared sensors to enable the bot to patrol a designated area.
Data Logging: Records moisture levels over time for analysis, creating a csv file to be uploaded remotely or through the controller.
Components
2 BBC micro:bit v2s: Acts as the brains of the bot and logs date to its storage, v2 needed for logging feature
Soil Moisture Sensor: Detects the moisture content in the soil.
Line follow sensor: Uses contrast in colour beneath the microbit to follow a patrol line
Ultrasonic Sensor: Sends out a pulse and measures response time to gauge distance(code was made to implemnt this feature)
Servo Motors: Provide mobility to the bot as well as powering the moisture sensor 

Setup and Installation
Assemble the Hardware:
Connect the soil moisture sensor to the micro:bit and mount it facing south of the robot
Attach the ultrasonic sensors for finding the .
Mount the micro:bit and sensors onto the chassis.

Programming the micro:bit:
Implement the MOVEMOTOR class
Use the provided Python scripts (main.py, transmot_thing.py, ) to program each micro:bit respectively
Ensure all dependencies are installed and the scripts are correctly uploaded to the micro:bit.

Purpose Of Each File
Main.py:
  The brains of the sensing bot, it utilises various different  functions to carry out its data collecting
  Data is logged throughout runtime for the user i.e temperature, sound, moisture
  The line_follow function makes the robot zigzag along the line, the zigzagging ensures the robot stays on track without driving straight off the patrol,
  it constantly measures the black and white contrast and aims to stay within a threshold i have set earlier in the code 
  
  An ultrasound function is created to utilise its distance sensing, furthermore the find_corners() function rapidly uses the pulses from left to right
  when there is a spike in distances during the array i.e [1,2,3,2,1,39] the bot will know its passed the corner of the object and begin checking the left corner. The microbit uses this information to make sure it turns perfectly 180 degrees away from the object and reverses in to collect moisture data
![image](https://github.com/user-attachments/assets/79ea5053-9ca4-4075-9906-5aff93928d67)

CSV_capture_file.py:
A program that uses the captured csv file to upload the data to thingspeak, 
The code builds an array through each row of the csv and uploads it to thingspeaks field using a wrtite API key

![image](https://github.com/user-attachments/assets/691f81fa-33c6-4de6-bd11-fcd8b073cb7a)


Transmot_thing.py
The second microbit uses this code to assist the motor if it gets stuck by pressing a or b, right or left to get it back on track.
It also has a rock paper scissors mini game to pass time while robot patrols.

Calibration:

Test the bot's movement and sensor responses before deployment.
The bot may need its wheel motors adjusted to prevent drift on straights.
Usage
Starting the Bot:

Power on the micro:bit to initiate the patrol sequence.
The bot will navigate the patrol line and monitor soil moisture levels of openings in plant pots.
Data Logging:
Moisture readings are recorded and can be analyzed later by viewing it in DATA folder after connecting the transmit controller.
The bots data can be uploaded to thingspeak, a branch of MATLAB to view the data online

Contributing
Contributions are welcome. Please fork the repository and submit a pull request with your enhancements or bug fixes.
