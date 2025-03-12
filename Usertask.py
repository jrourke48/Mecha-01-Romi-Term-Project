
def usertask_fun(shares):
    prompt, run, calibrateb, calibratew, L_eff, R_eff, V= shares
    S0_cb = 0 # names for each state
    S1_cw = 1
    S2_w = 2
    S3_r = 3 
    state = 0  #state variable
    while True:
        #state machine
        if state == S0_cb:
            state = S0_calibrateb(prompt, calibrateb)
        elif state == S1_cw:
            state = S1_calibratew(prompt, calibratew)
        elif state == S2_w:
            state = S2_wait(prompt, run, L_eff, R_eff, V)
        elif state == S3_r:
            state = S3_run(prompt, run)
        else: 
            raise ValueError('Invalid state')
        yield state

def S0_calibrateb(prompt, calibrateb):
    #check if we are done calibrating line sensors
    if not prompt.curinput: #check if there is already a prompt
        prompt.add_prompt("Press enter to calibrate black:")
    if prompt.check():
        calibrateb.put(1) #toggle flag to calibrat black
        return 1  # Move to next state when all inputs are collected
    return 0  # Stay in current state

def S1_calibratew(prompt, calibratew):
     #check if we are done calibrating line sensors
    if not prompt.curinput: #check if there is already a prompt
        prompt.add_prompt("Press enter to calibrate white:")
    if prompt.check():
        calibratew.put(1)
        return 2  # Move to next state when all inputs are collected
    return 1  # Stay in current state

#check if we are ready to run
def S2_wait(prompt, run, L_eff, R_eff, V):
    if not prompt.curinput: #check if there is already a prompt
        prompt.add_prompt("Enter motor effort (-50 to 50):", -50, 50, [L_eff, R_eff, V])
    if prompt.check():
        run.put(1) #if valid integer run motor
        return 3
    return 2

#check to stop running
def S3_run(prompt, run):
    if not prompt.curinput: #check if there is already a prompt
        prompt.add_prompt("Press enter to stop:")
    if prompt.check(): #checks for enter
        run.put(0)
        return 2
    return 3


