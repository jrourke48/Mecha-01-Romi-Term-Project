from time import ticks_diff, ticks_us

def motortask_fun(shares):
    run, encoder, motor, eff= shares
    S0_w = 0 # names for each state
    S1_r = 1
    state = 0  #state variable
    Kp = 0.2
    Ki = 0.15
    Kd = 0.1
    omega = 1374.25 #ticks/us to eff %
    phi = 2.12 #ticks/us to eff %
    esum = 0
    eprev = 0
    while True:
        #state machine
        if state == S0_w:
            state = S0_wait(run, eff, motor)
        elif state == S1_r:
            state = S1_run(run, encoder, motor, eff, Kp, Ki, Kd, omega, phi, esum, eprev)
        else: 
            raise ValueError('Invalid state')
        yield state

#wait to run state
def S0_wait(run, eff, motor):
    if run.get() == 1: #check if the motor effort is being changed
        motor.enable() #enable the motors
        motor.set_eff(eff.get())
        return 1
    else:
        return 0

#motor run state
def S1_run(run, encoder, motor, eff, Kp, Ki, Kd, omega, phi, esum, eprev):
    if run.get() == 0: #check if the motor is supposed to stop
        motor.disable() #stop the motor
        return 0
    motor.set_eff(control_loop(eff, encoder, Kp, Ki, Kd, omega, phi, esum, eprev)) #update the eff by running the pid control loop
    return 1

#helper function for pid control loop
def control_loop(eff, encoder, Kp, Ki, Kd, omega, phi, esum, eprev):
    Vref = eff.get() #get the reference velocity
    encoder.update()
    Vact = omega*encoder.get_velocity() - phi
    e = Vref - Vact
    # Proportional control
    Ak = Kp*e
    # Integral control
    esum += e #riemman sum of error
    esum = max(min(esum, 10), -10)  # Prevent windup
    Ai = 0.05*Ki*esum #constant time step and Ki
    # Derivative control
    Ad = Kd*(e - eprev)/0.05  #constant time step and Kd
    eprev = e
    # Sum the control actions
    return Ak+Ad+Ai

