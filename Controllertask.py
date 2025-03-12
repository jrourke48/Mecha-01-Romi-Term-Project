def controllertask_fun(shares):
    #unpack the shares: run boolean, line centroid share, motor efforts
    mode, centroid, V, e, L_eff, R_eff = shares
    S0_w = 0 # names for each state
    S1_r = 1
    S2_p = 2
    S3_s = 3
    state = 0  #state variable
    Kp = 4.25
    Ki = 0.07
    Kd = 0.0
    esum = 0 #integral control
    eprev = 0 #derivative control
    while True:
        #state machine
        if state == S0_w:
            state = S0_wait(mode)
        elif state == S1_r:
            state = S1_Lrun(mode, centroid, V, R_eff, 
                           L_eff, Kp, Ki, Kd, esum, eprev)
        elif state == S2_p:
            state = S2_pivot(mode, e, R_eff, L_eff, esum, eprev)
        elif state == S3_s:
            state = S3_straight(mode, e, V, R_eff, L_eff, esum, eprev)
        else: 
            raise ValueError('Invalid state')
        yield state
#wait to run state
def S0_wait(mode):
    if mode.get() == 1: #check if the motor effort is being changed
        return 1
    return 0

def S1_Lrun(mode, centroid, V, R_eff, L_eff, Kp, Ki, Kd, esum, eprev):
    if mode.get() == 0: #check if the motor is supposed to stop
        esum = 0
        eprev = 0
        return 0
    elif mode.get() == 2:
        esum = 0
        eprev = 0
        return 2
    else:
        e = centroid.get()-7
        if e != 0:
            dgamma = control_loop(e, Kp, Ki, Kd, esum, eprev) #perform the pid control
            L_eff.put(round(V.get() + dgamma))
            R_eff.put(round(V.get() - dgamma))
    return 1
    
#method for pivoting
def S2_pivot(mode, e, R_eff, L_eff, esum, eprev):
    if mode.get() == 0: #check if the motor is supposed to stop
        esum = 0
        eprev = 0
        return 0
    elif mode.get() == 3:
        esum = 0
        eprev = 0
        return 3
    else:
        if e.get() > 180:
                A = control_loop(360-e.get(), 0.25, 0.08, 0, esum, eprev)
                L_eff.put(round(A))
                R_eff.put(round(-A))
        else:
                A = control_loop(e.get(), 0.25, 0.08, 0, esum, eprev)
                L_eff.put(round(-A))
                R_eff.put(round(A))
    return 2

#method for determining straight drive error
def S3_straight(mode, e, V, R_eff, L_eff, esum, eprev):
        #idk if this is needed self.update_all(yaw, omegac, r, conv, encoderr, encoderl)
        #return the error which is the difference between the target heading and 
        #the current heading
        if mode.get() == 0: #check if the motor is supposed to stop
            esum = 0
            eprev = 0
            return 0
        elif mode.get() == 1:
            print("back to line")
            esum = 0
            eprev = 0
            return 1
        elif mode.get() == 2:
            esum = 0
            eprev = 0
            return 2
        else:
            A = control_loop(e.get(), 0.045, 0.01, 0, esum, eprev)
            L_eff.put(round(V.get()+A))
            R_eff.put(round(V.get()-A))
        return 3

def S4_arc():
    pass

    
def control_loop(e, Kp, Ki, Kd, esum, eprev):
    # Proportional control
    Ak = Kp*e
    # Integral control
    esum += e #riemman sum of error
    esum = max(min(esum, 30), -30)  # Prevent windup
    Ai = Ki*esum #constant time step and Ki
    # Derivative control
    Ad = Kd*(e - eprev)  #constant time step and Kd
    eprev = e
    # Sum the control actions
    return Ak+Ad+Ai

