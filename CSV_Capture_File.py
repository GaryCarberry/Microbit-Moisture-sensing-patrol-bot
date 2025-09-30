import csv#allows reading of csv
import time
import requests#allows the coe to make HTTP requests
import random


with open ('microbit(4).csv',mode='r')as file:
    csvFile=csv.reader(file)
    for lines in csvFile:
        timest=lines[0]
        temp=lines[1] 
        dist=lines[3]
        sound=lines[2]
        moisture=random.randint(1,100)
        msg=("https://api.thingspeak.com/update?api_key=GQVT0LGOT5K9LKRA&
        field1={},#modfies each field in thingspeak to showcase data received from the microbit
        &field2={},
        &field3={},
        &field4={},
        &field5={}".format(timest,temp,dist,sound,moisture))
        print(msg)
        api_url=msg
        response=requests.get(api_url)
        print(lines)
        time.sleep(20)

