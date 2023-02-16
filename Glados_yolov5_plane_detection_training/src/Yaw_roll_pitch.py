if self.rc_overrides:## To go to left
           self.rc_roll -= 50
           if self.rc_roll < self.rc_roll_min:
              self.rc_roll=self.rc_roll_min
           if self.rc_roll > self.rc_roll_max:
              self.rc_roll=self.rc_roll_max
           self.vehicle.channels.overrides[1] = self.rc_roll
        else:
           plane.set_airspeed(22)
           plane.set_rc_channel(1,1300)
           
        return True       
        if self.rc_overrides:## To go to right
           self.rc_roll += 50
           if self.rc_roll < self.rc_roll_min:
              self.rc_roll=self.rc_roll_min
           if self.rc_roll > self.rc_roll_max:
              self.rc_roll=self.rc_roll_max
           self.vehicle.channels.overrides[1] = self.rc_roll
        else:
           plane.set_airspeed(22)
           plane.set_rc_channel(1,1700)
           
        return True   

        if self.rc_overrides:#go to left while ascending
           self.rc_pitch -= 50
           if self.rc_pitch < self.rc_pitch_min:
              self.rc_pitch=self.rc_pitch_min
           if self.rc_pitch > self.rc_pitch_max:
              self.rc_pitch=self.rc_pitch_max 
           self.rc_roll -= 50
           if self.rc_roll < self.rc_roll_min:
              self.rc_roll=self.rc_roll_min
           if self.rc_roll > self.rc_roll_max:
              self.rc_roll=self.rc_roll_max
           self.vehicle.channels.overrides[2] = self.rc_pitch
           self.vehicle.channels.overrides[1] = self.rc_roll
        else:
           plane.set_airspeed(22)
           plane.set_rc_channel(1,1700)
           t1 = threading.Thread(target=self.send_ned_velocity, args=(vel_x,vel_y,vel_z,duration,))
           t1.daemon = True
           t1.start()
        return True
        if self.rc_overrides:#go to right while ascending
           self.rc_pitch -= 50
           if self.rc_pitch < self.rc_pitch_min:
              self.rc_pitch=self.rc_pitch_min
           if self.rc_pitch > self.rc_pitch_max:
              self.rc_pitch=self.rc_pitch_max 
           self.rc_roll += 50
           if self.rc_roll < self.rc_roll_min:
              self.rc_roll=self.rc_roll_min
           if self.rc_roll > self.rc_roll_max:
              self.rc_roll=self.rc_roll_max
           self.vehicle.channels.overrides[2] = self.rc_pitch
           self.vehicle.channels.overrides[1] = self.rc_roll
        else:
           plane.set_airspeed(22)
           #plane.set_rc_channel(1,1700)
           t1 = threading.Thread(target=self.send_ned_velocity, args=(vel_x,vel_y,vel_z,duration,))
           t1.daemon = True
           t1.start()
        return True

        if self.rc_overrides:#go to left while descending
           self.rc_pitch -= 50
           if self.rc_pitch < self.rc_pitch_min:
              self.rc_pitch=self.rc_pitch_min
           if self.rc_pitch > self.rc_pitch_max:
              self.rc_pitch=self.rc_pitch_max 
           self.rc_roll += 50
           if self.rc_roll < self.rc_roll_min:
              self.rc_roll=self.rc_roll_min
           if self.rc_roll > self.rc_roll_max:
              self.rc_roll=self.rc_roll_max
           self.vehicle.channels.overrides[2] = self.rc_pitch
           self.vehicle.channels.overrides[1] = self.rc_roll
        else:
           plane.set_airspeed(22)
           #plane.set_rc_channel(1,1700)
           t1 = threading.Thread(target=self.send_ned_velocity, args=(vel_x,vel_y,vel_z,duration,))
           t1.daemon = True
           t1.start()
        return True
        
        if self.rc_overrides:#go to right while descending
           self.rc_pitch += 50
           if self.rc_pitch < self.rc_pitch_min:
              self.rc_pitch=self.rc_pitch_min
           if self.rc_pitch > self.rc_pitch_max:
              self.rc_pitch=self.rc_pitch_max 
           self.rc_roll += 50
           if self.rc_roll < self.rc_roll_min:
              self.rc_roll=self.rc_roll_min
           if self.rc_roll > self.rc_roll_max:
              self.rc_roll=self.rc_roll_max
           self.vehicle.channels.overrides[2] = self.rc_pitch
           self.vehicle.channels.overrides[1] = self.rc_roll
        else:
           vel=self.DefaultVelocity/math.sqrt(2)
           vel_x=-vel
           vel_y=vel
           vel_z=0
           duration=1
           t1 = threading.Thread(target=self.send_ned_velocity, args=(vel_x,vel_y,vel_z,duration,))
           t1.daemon = True
           t1.start()
        return True
        #self.vehicle.channels.overrides[4] = self.rc_yaw