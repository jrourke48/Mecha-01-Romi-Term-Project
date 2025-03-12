def sensortask_fun(shares):
    run, calibrateb, calibratew, lin_sen_array, centroid, bmp, bmp_array, psat = shares
    S0_cb = 0 # names for each state
    S1_cw = 1
    S2_w = 2
    S3_r = 3 
    state = 0  #state variable
    while True:
        #state machine
        if state == S0_cb:
            state = S0_calibrateb(calibrateb, lin_sen_array)
        elif state == S1_cw:
            state = S1_calibratew(calibratew, lin_sen_array)
        elif state == S2_w:
            state = S2_wait(run)
        elif state == S3_r:
            state = S3_run(run, lin_sen_array, centroid, bmp, bmp_array, psat)
        else: 
            raise ValueError('Invalid state')
        yield state

#calibrate black
def S0_calibrateb(calibrateb, lin_sen_array):
    if calibrateb.get() == 1:
        lin_sen_array.calibrate_black() #print array values
        return 1
    return 0
    
#calibrate white
def S1_calibratew(calibratew, lin_sen_array):
    if calibratew.get() == 1:
        lin_sen_array.calibrate_white() #print array values
        return 2
    return 1 
    
#wait for effort to be input   
def S2_wait(run):
    if run.get() == 1: #check if the data has been collected
        return 3 #move to the print state if so 
    else:
        return 2 #stay in the store state if not

#calculate centroid
def S3_run(run, lin_sens_array, centroid, bmp, bmp_array, psat):
    # print the headers
    if run.get() == 1:
        centroid.put(lin_sens_array.centroid())
        psat.put(lin_sens_array.psat())
        bmp.put(bmp_array.check_bump())          # bmp will be 1 if wall has been hit
        return 3
    else:
        return 2 