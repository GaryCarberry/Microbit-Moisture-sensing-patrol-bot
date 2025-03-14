from microbit import *
import radio
import speech
import random
import music
#A controller that receives data from the movemotor during its patrol, this will be captured and when reconnected via USB 
#the user will be able to view their information using the CSV capture code to view the information, at certain times online
#with thingspeak
# Configure the radio
radio.config(group=1)  # Ensure the same group as the robot
radio.on()

# Button mapping
LEFT_COMMAND = "A"  # Command to stop the robot
RIGHT_COMMAND = "B"  # Example command to turn (optional)

def Lose():#For when the microbit loses its game of rock paper scissors
        display.show(Image.SAD)#sad image for feeedback
        speech.say("Oh I lost",speed=90)#uses the speech to say that it lost
        sleep(1000)#waits one second
        music.play(music.FUNERAL)
        
def Win():#For when the microbit wins its game of rock paper scissors
    
    display.show(Image.SILLY)
    speech.say("HAHA I Win",speed=90)
    sleep(1000)
    music.play(music.ENTERTAINER)
   
def Draw():#For when the microbit draws its game of rock paper scissors
    display.show(Image.SURPRISED)
    speech.say("Oh a draw")
    sleep(1000)
    speech.say("Boooooooring",speed=90)
    music.play(music.WAWAWAWAA)
    
def rps():#basic rock paper scissors function used as a sidefeature to play while waiting for data to be collected, 
    speech.say("Rock",pitch=70,speed=40,mouth=128,throat=128)#controls how the robot delivers the message
    display.show(Image('03330:'#emulates the leds on the front of the microbit
                       '05330:'
                       '03430:'
                       '05430:'
                       '03330:'
                      ))
    sleep(1000)#delays until the next part
    display.clear()#clears the display for the microbit led
    speech.say("Paper",pitch=70,speed=40,mouth=128,throat=128)
    display.show(Image('33330:'
                       '03230:'
                       '03330:'
                       '03230:'
                       '03333:'
                      ))
    sleep(1000)
    display.clear()
    speech.say("Scissors",pitch=70,speed=40,mouth=128,throat=128)
    display.show(Image('30033:'
                       '03033:'
                       '00300:'
                       '03033:'
                       '30033:'
                      ))
    sleep(1000)
    display.clear()
    answer= random.randint(1,3)# the option it chooses is 1,2 or 3 is later assign numbers to the 3 outcomes so it can decide what its picked
    sleep(2000)
    if answer==1:
        speech.say('Scissors')
        display.show(Image('30033:'
                           '03033:'
                           '00300:'
                           '03033:'
                           '30033:'
                          ))
        if button_a.is_pressed():#button a being rock so the microbit loses
            sleep(1000)
            Lose()
        elif button_b.is_pressed():#button b being paper so the microbit wins
            sleep(1000)
            Win()
        elif pin_logo.is_touched():#logo is scissors so its a draw
            sleep(1000)
            Draw()
    if answer==2:
        speech.say('Rock')
        display.show(Image('03330:'
                           '05330:'
                           '03430:'
                           '05430:'
                           '03330:'
                          ))
        if button_a.is_pressed():
            sleep(1000)
            Draw()
        elif button_b.is_pressed():
            sleep(1000)
            Lose()
        if pin_logo.is_touched():
            sleep(1000)
            Win()
    if answer==3:
        speech.say("Paper")
        display.show(Image('33330:'
                           '03230:'
                           '03330:'
                           '03230:'
                           '03333:'
                          ))
        sleep(2000)
        if button_a.is_pressed():
            sleep(1000)
            Win()
        elif button_b.is_pressed():
            sleep(1000)
            Draw()
        elif pin_logo.is_touched():
            sleep(1000)
            Lose()
a="Rock"
b="Paper"
c="Scissors"
        
    


# Main loop
while True:
    # Send "A" when button A is pressed,
    #these a and b commands are for the possibility of the microbit getting stuck while on patrol
    if button_a.is_pressed():
        radio.send(LEFT_COMMAND)
        display.show("A")  # Visual feedback
        sleep(500)  # Debounce to avoid multiple rapid sends
    
    # (Optional) Send "B" when button B is pressed
    if button_b.is_pressed():
        radio.send(RIGHT_COMMAND)
        display.show("B")  # Visual feedback
        sleep(500)  # Debounce to avoid multiple rapid sends
    if accelerometer.was_gesture('shake'):# when shaken it plays rock paper scissors
        rps()
        sleep(1000)
 
    # Clears the display when no buttons are pressed
    if not (button_a.is_pressed() or button_b.is_pressed()):
        display.clear()
