from Nav import Nav
from Grid import Grid

def navtask_fun(shares):
    run, e, mode, bmp, imu, encoderr, encoderl, psat, i = shares
    # Initialize the grid and nav class
    grid = Grid()
    nav = Nav(grid)
    rconv = 0.15272  # Conversion from ticks/us to rad/s and radius

    # State names
    
    S0_w = 0      # State 0
    S1_s = 1      # State 1
    S2_0 = 2      # State 2
    S3_1 = 3      # State 3
    S4_2 = 4      # State 4
    S5_5s1 = 5    # State 5
    S6_3 = 6      # State 6  
    S7_4 = 7      # State 7 
    S8_int = 8    # State 8
    S9_5 = 9      # State 9
    S10_bmp = 10  # State 10
    S11_5s2 = 11  # State 11
    S12_c = 12    # State 12

    state = S0_w  # Initial state

    while True:
        # State Machine
        if state == S0_w:
            state = S0_wait(run, nav, imu, mode)
        elif state == S1_s:
            state = S1_start(nav, imu, mode, psat, i)
        elif state == S2_0:
            state = S2_CP0(nav, imu, mode, e, rconv, encoderr, encoderl)
        elif state == S3_1:
            state = S3_CP1(nav, imu, mode, psat)
        elif state == S4_2:
            state = S4_CP2(nav, imu, mode, e, rconv, encoderr, encoderl)
        elif state == S5_5s1:
            state = S5_5S1(nav, imu, mode, psat)
        elif state == S6_3:
            state = S6_CP3(nav, imu, mode, e, rconv, encoderr, encoderl)
        elif state == S7_4:
            state = S7_CP4(nav, imu, mode, e, rconv, encoderr, encoderl)
        elif state == S8_int:
            state = S8_INT(nav, imu, mode, e, rconv, encoderr, encoderl)
        elif state == S9_5:
            state = S9_CP5(bmp, nav, mode)
        elif state == S10_bmp:
            state = S10_BMP(nav, imu, mode, e, rconv, encoderr, encoderl)
        elif state == S11_5s2:
            state = S11_52s(nav, imu, mode, e, rconv, encoderr, encoderl)
        elif state == S12_c:
            state = S12_aftercup(nav, run, imu, mode, e, rconv, encoderr, encoderl)
        else:
            print(f"Error: Invalid state {state}")
            raise ValueError(f"Invalid state: {state}")
        
        yield state


#The following lines of code are repeated for any point to point motion. 
#this will describe what it is doing line by line.
#if nav.mode == 2:          # check for pivot mode
#This line determines the error from the target line to line heading with respect to the imu heading
#it also updates nav.mode if the error is less than 4 degrees
#        e.put(nav.pivot(imu.get_yaw(),  encoderr, encoderl))
#        if nav.mode == 3:      # checks for drive straight mode
#            nav.Xc = 0         #if we should drive straight it will reset the distance traveled
#            mode.put(3)        # it will also change the mode to drive straight
#    else:                      # drive to int point
#This line determines the error for straight driving which is the current yawrate which should be 0 
#it also updates the current distance traveled in the straight line
#        e.put(nav.straight(imu.get_yaw(),imu.get_yawrate(),rconv, encoderr, encoderl))
#        if nav.check_target():  # this checks if the target has been reached
#            mode.put(X)         # if so it will change to the pivot mode or line mode
#            nav.new_target(7)   # it will also change the target to the next point
#            return X            # move to next state
#    return X                    # return to current state


# S0: Waiting for calibration of line sensors
def S0_wait(run, nav, imu, mode):
    if run.get() == 1:  # Check run to begin navigation
        x = imu.get_yaw()
        nav.y = x
        mode.put(1)
        return 1        # move to state 1
    return 0            # Stay in waiting state

# S1: start to point before the diamond
def S1_start(nav, imu, mode, psat, i):
    if i.get() < 100:       # average first 100 yaw values for heading
           nav.y = (nav.y + imu.get_yaw())/2
           i.put(i.get()+1)
    elif psat.get() > 0.23: # sense the beginning of the diamond
        print(nav.y)
        print(imu.get_yaw())
        mode.put(2)
        nav.mode = 2
        nav.new_target(1)
        return 2            # move to state 2
    return 1                # Stay in state 1 if diamond not reached

# S2: Pivot turn to CP1 and drive through diamond
def S2_CP0(nav, imu, mode, e, rconv, encoderr, encoderl):
    if nav.mode == 2:       # check for pivot mode
        e.put(nav.pivot(imu.get_yaw(),  encoderr, encoderl))
        if nav.mode == 3:
            nav.Xc = 0
            mode.put(3)
    else:                  # drive straight to CP1
        e.put(nav.straight(imu.get_yaw(),imu.get_yawrate(),rconv, encoderr, encoderl))
        if nav.check_target():
            mode.put(1)
            nav.new_target(2)
            return 3       # move to state 3
    return 2               # stay in state 2


# S3: Move along line through dash to CP2
def S3_CP1(nav, imu, mode, psat):
    if psat.get() < 0.02:  # check for dashed line
        print("dash")
        nav.new_target(3)
        nav.mode = 1
        return 4
    elif psat.get() > 0.4: # if dash not found, go to CP3
        print("CP3")
        nav.new_target(5)
        x = imu.get_yaw()
        print(x)
        mode.put(2)
        return 6           # move to state 6
    return 3               # stay in state 3

# S4: From CP2 get cup #1 and continue through to point
def S4_CP2(nav, imu, mode, e, rconv, encoderr, encoderl):
    if abs(imu.get_yaw() - nav.y) < 2:  # check for CP2 heading
        print("CP2")
        mode.put(2) 
        nav.mode = 2
    if nav.mode == 2:                   # check for pivot
        e.put(nav.pivot(imu.get_yaw(),  encoderr, encoderl))
        if nav.mode == 3:
            nav.Xc = 0
            mode.put(3)
    elif nav.mode == 3:                # check for driving straight
        e.put(nav.straight(imu.get_yaw(),imu.get_yawrate(),rconv, encoderr, encoderl))
        if nav.check_target():
            print("-5 seconds!")
            mode.put(1)
            nav.new_target(4)
            return 5                   # move to state 5
    return 4                           # stay in state 4

# S5: line follow to CP3
def S5_5S1(nav, imu, mode, psat):
    if psat.get() > 0.4:  # check for CP3
        x = imu.get_yaw()
        print(x)
        nav.new_target(5)
        mode.put(2)
        return 6          # move to state 6
    return 5              # stay in state 5

# S6: from CP3 pivot to drive to CP4
def S6_CP3(nav, imu, mode, e, rconv, encoderr, encoderl):
    if nav.mode == 2:          # check for pivot mode 
        e.put(nav.pivot(imu.get_yaw(),  encoderr, encoderl))
        if nav.mode == 3:      # check for drive straight mode
            print("heading to CP4")
            nav.Xc = 0
            mode.put(3)
    else:                      # drive towards CP4
        e.put(nav.straight(imu.get_yaw(),imu.get_yawrate(),rconv, encoderr, encoderl))
        if nav.check_target(): # check for CP4
            mode.put(2)
            nav.new_target(6)
            return 7           # move to state 7
    return 6                   # stay in state 6
    
# S7: from CP4 drive to int point
def S7_CP4(nav, imu, mode, e, rconv, encoderr, encoderl):
    if nav.mode == 2:          # check for pivot mode
        e.put(nav.pivot(imu.get_yaw(),  encoderr, encoderl))
        if nav.mode == 3:      # check for drive straight mode
            nav.Xc = 0
            mode.put(3)
    else:                      # drive to int point
        e.put(nav.straight(imu.get_yaw(),imu.get_yawrate(),rconv, encoderr, encoderl))
        if nav.check_target(): # check for int point
            mode.put(2)
            nav.new_target(7)
            return 8           # move to state 8
    return 7                   # stay in state 7

# S8: from int point drive to CP5
def S8_INT(nav, imu, mode, e, rconv, encoderr, encoderl):
    if nav.mode == 2:          # check for pivot mode
        e.put(nav.pivot(imu.get_yaw(), encoderr, encoderl))
        if nav.mode == 3:      # check for drive straight mode
            mode.put(3)
    else:                      # drive to CP5
        e.put(nav.straight(imu.get_yaw(), imu.get_yawrate(), rconv, encoderr, encoderl))
        if nav.check_target(): # check for CP5
            mode.put(1)
            nav.nextpoint = Grid.Point(200,0)
            return 9           # move to state 9
    return 8                   # stay in state 8

# S9: from CP5 line follow until bump
def S9_CP5(bmp, nav, mode):
    if bmp.get() == 1:    # check for bump
        print("who put that wall there?")
        mode.put(2)
        nav.new_target(8)
        return 10         # move to state 10
    return 9              # stay in state 9

# S10: after wall move to cup
def S10_BMP(nav, imu, mode, e, rconv, encoderr, encoderl):
    if nav.mode == 2:          # check for pivot mode
        e.put(nav.pivot(imu.get_yaw(), encoderr, encoderl))
        if nav.mode == 3:      # check for drive straight
            mode.put(3)
    else:                      # drive straight to cup
        e.put(nav.straight(imu.get_yaw(), imu.get_yawrate(), rconv, encoderr, encoderl))
        if nav.check_target(): # check for cup position
            mode.put(2)
            nav.new_target(9)
            return 11          # move to state 11
    return 10                  # stay in state 10

# S11: from cup move back to line
def S11_52s(nav, imu, mode, e, rconv, encoderr, encoderl):
    if nav.mode == 2:          # check for pivot
        e.put(nav.pivot(imu.get_yaw(), encoderr, encoderl))
        if nav.mode == 3:      # check for drive straight
            mode.put(3)
    else:                      # drive straight to point on line
        e.put(nav.straight(imu.get_yaw(), imu.get_yawrate(), rconv, encoderr, encoderl))
        if nav.check_target(): # check at line point
            mode.put(2)
            nav.new_target(10)
            return 12          # move to state 12
    return 11                  # stay in state 11

# S12: drive back to start
def S12_aftercup(nav, run, imu, mode, e, rconv, encoderr, encoderl):
    if nav.mode == 2:          # check for pivot
        e.put(nav.pivot(imu.get_yaw(), encoderr, encoderl))
        if nav.mode == 3:      # check for drive straight
            mode.put(3)
    else:
        e.put(nav.straight(imu.get_yaw(), imu.get_yawrate(), rconv, encoderr, encoderl))
        if nav.check_target(): # check at start point
            run.put(0)
            print("completed!")
            return 1           # move to state 1
    return 12                  # stay in state 12
