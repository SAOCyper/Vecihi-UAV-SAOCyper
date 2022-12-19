# cs.???? = currentstate, any variable on the status tab in the planner can be used.
# Script = options are 
# Script.Sleep(ms)
# Script.ChangeParam(name,value)
# Script.GetParam(name)
# Script.ChangeMode(mode) - same as displayed in mode setup screen 'AUTO'
# Script.WaitFor(string,timeout)
# Script.SendRC(channel,pwm,sendnow)
# 

print('Start Script')
for chan in range(1,9):
    Script.SendRC(chan,1500,False)
Script.SendRC(3,Script.GetParam('RC3_MIN'),True)

#######ROLL########

####LEFT######
Script.SendRC(8,1700,True) # Manual mode
Script.SendRC(1,2000,True) # roll
while cs.roll > -45: # top hald 0 - 180
    Script.Sleep(5)
while cs.roll < -45: # -180 - -45
    Script.Sleep(5)

########RECOVER#########
Script.SendRC(8,1500,True) # stabalise
Script.SendRC(1,1500,True) # level roll
Script.Sleep(2000) # 2 sec to stabalise

#####RIGHT#####
Script.SendRC(8,1700,True) # Manual mode
Script.SendRC(1,1000,True) # roll
while cs.roll > -45: # top half 0 - 180
    Script.Sleep(5)
while cs.roll < -45: # -180 - -45
    Script.Sleep(5)

########RECOVER########
Script.SendRC(8,1500,True) # stabalise
Script.SendRC(1,1500,True) # level roll
Script.Sleep(2000) # 2 sec to stabalise


######LOOP#########
Script.SendRC(8,1700,True) # Manual mode
Script.SendRC(2,1600,True) # Slight down for airspeed
Script.Sleep(500)

#runup should be based on airspeed
#while cs.groundspeed < 20:
#	Script.Sleep(5)

Script.SendRC(3,2000,True) #Full Throttle
Script.SendRC(2,1000,True) # Pull back on elevator for Loop
while cs.pitch > -45: # top hald 0 - 180
    Script.Sleep(5)
while cs.pitch < -45: # -180 - -45
    Script.Sleep(5)

#######RECOVER#######
Script.SendRC(8,1500,True) # stabalise
Script.SendRC(2,1500,True) # level pitch
Script.Sleep(2000) # 2 sec to stabalise


######INVERTED######
#Script.SendRC(8,1700,True) #Manual Mode
#while cs.roll != 180:
#	Script.SendRC(1,1000,True)
#Script.SendRC(1,1500,True) #Even Ailerons upside down
#Script.SendRC(2,1550,True) #Slight down elevator to hold alt

#######RECOVER#######
#Script.SendRC(8,1500,True) # stabalise
#Script.SendRC(2,1500,True) # level pitch
#Script.Sleep(2000) # 2 sec to stabalise
