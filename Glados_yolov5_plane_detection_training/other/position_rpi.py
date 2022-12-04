import RPi.GPIO as GPIO # This library is missing dont try to use
import time
class RaspPiServo:
    def __init__(self):
        self.servoPIN = 17
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.servoPIN, GPIO.OUT)
        self.pwm = GPIO.PWM(self.servoPIN, 50) 
        self.pwm.start(90)
        self.start_point=90
    def left_angle(self,aci):
        x=(10/180)*aci + 1
        duty=x*5
        if aci >= 90:
            return last_duty
        last_duty=duty
        return duty
    def right_angle(self,aci):
        x=(10/180)*aci + 1 
        duty=x*5
        if aci <= 90:
            return last_duty
        last_duty=duty
        return duty   
    def stop(self):
        self.pwm.stop()
    def servo_run(self,command):
        try:
            if command == "Turn left":
                for i in range(90,-1,-5):
                    print ("aci = ",i)
                    duty=self.left_angle(i)
                    self.pwm.ChangeDutyCycle(duty)
                    time.sleep(0.05)
            elif command == "Turn right":
                for i in range(90,181,5):
                    print ("aci = ",i)
                    duty=self.right_angle(i)
                    self.pwm.ChangeDutyCycle(duty)
                    time.sleep(0.05)
            else:
                pass                      
        except KeyboardInterrupt:
            self.pwm.stop()
            GPIO.cleanup()
            print("Program Stopped!")