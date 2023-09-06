#Libraries
import pyrebase
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo
import RPi.GPIO as GPIO
import time

#setting API firebase
config = {
  "apiKey": "AIzaSyBIxLGjEx5RJyiYgcCsWrj2leXziEUJEHQ",
  "authDomain": "cobarelay-b71bf.firebaseapp.com",
  "databaseURL": "https://cobarelay-b71bf-default-rtdb.firebaseio.com",
  "projectId": "cobarelay-b71bf",
  "storageBucket": "cobarelay-b71bf.appspot.com",
  "messagingSenderId": "318516627224",
  "appId": "1:318516627224:web:4e92bb0d831c8e25cac06d",
  "measurementId": "G-0WMLKJSNSH"
};
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
database = firebase.database()

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

factory = PiGPIOFactory()
servo_org=Servo(24, pin_factory=factory)
servo_anorg=Servo(21, pin_factory=factory)

#set GPIO Pins
GPIO_SEN=22
GPIO_TRIGGER = 18
GPIO_ECHO = 23

GPIO_TRIGGER2 = 16
GPIO_ECHO2 = 20

GPIO_TRIGGER3 = 17
GPIO_ECHO3 = 27
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_TRIGGER2, GPIO.OUT)
GPIO.setup(GPIO_ECHO2, GPIO.IN)
GPIO.setup(GPIO_TRIGGER3, GPIO.OUT)
GPIO.setup(GPIO_ECHO3, GPIO.IN)
GPIO.setup(GPIO_SEN, GPIO.IN)
 
def jarak(trig,echo):
    # set Trigger to HIGH
    GPIO.output(trig, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(trig, False)
 
    StartTime = time.time()
    StopTime = time.time()
     
    # save StartTime
    while GPIO.input(echo) == 0:
        StartTime = time.time()
    # save time of arrival
    while GPIO.input(echo) == 1:
        StopTime = time.time()

# time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

database.child("SDB")
data = {"org":1,"anorg":1  }
database.set(data)
#tutup     
servo_org.max()
servo_anorg.min()
 
if __name__ == '__main__':
    try:
        while True:
            dist = jarak(GPIO_TRIGGER,GPIO_ECHO)
            dist2= jarak(GPIO_TRIGGER2,GPIO_ECHO2)
            dist3= jarak(GPIO_TRIGGER3,GPIO_ECHO3)
            #konversi volume
            if dist>50:
                dist=50
            if dist2>50:
                dist2=50
            
            vol_org= int((dist/50)*100)
            vol_anorg=int((dist2/50)*100)
            dt_org=100-vol_org
            dt_anorg=100-vol_anorg
            database.child("SDB").update({"org": dt_org})
            database.child("SDB").update({"anorg": dt_anorg})
                
            organik=GPIO.input(GPIO_SEN)
            
            print ("Measured org = %.1f cm" % dist)
            print ("Measured anorg = %.1f cm" % dist2)
            print ("Measured objek = %.1f cm" % dist3)
            time.sleep(0.3)
            print(organik)
            if dist3<10:
                for i in range(4):
                    organik=organik=GPIO.input(GPIO_SEN)
                    time.sleep(0.3)
                if organik==0:
                    servo_org.min()
                else:
                    servo_anorg.max()
                time.sleep(5)
                servo_org.max()
                servo_anorg.min()
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()


