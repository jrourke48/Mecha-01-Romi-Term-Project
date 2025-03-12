from Grid import Grid
import math
#from time import ticks_us, ticks_diff

class Nav:
    class Line:
        def __init__(self, p1, p2):
            """Initialize a line with two Point objects."""
            self.p1 = p1
            self.p2 = p2
        #updates the line 
        def update_startline(self, p1):
            """Update the start of line to reflect the current position and keeps 
            the next point the same."""
            self.p1 = p1
        def update_whole(self, p1, p2):
            """Updates both the start and end to reflect a new target."""
            self.p1 = p1
            self.p2 = p2

        def get_dist(self):
            """Return the length of the line."""
            return self.p1.distance_to(self.p2)

        def get_heading(self):
            """Return the heading angle (in degrees) with respect to the x-axis."""
            dx = self.p2.x - self.p1.x
            dy = self.p2.y - self.p1.y
            return (math.degrees(math.atan2(dy, dx)) - 90) % 360
        


        def __repr__(self):
            return f"Line({self.p1}, {self.p2})"
        
    def __init__(self, Grid):
        self.pos = Grid.Point(0,0) #romi absolute position
        self.Grid = Grid
        self.y = 0
        self.mode = 2
        self.prevrencoder = 0 #previous rencoder postition
        self.prevlencoder = 0 #previous lencoder position
        self.Xc = 0 #current chassis position
        self.yaw = 0 #current heading
        self.omegac = 0 #current yaw rate
        self.dt = 0    # amount of time btwn last two updates
        self.prev_time = 0 #previous time
        self.t = 0  #current time
        self.nextpoint = Grid.CPS[0] #next point to hit
        self.distance = 0 #initial distance to next checkpoint
        self.curheading = 0
        self.target = self.Line(self.pos, self.nextpoint) #target line

    
    def new_target(self, idx):
        #idx represents which CP is your new target
        """Update the target to the next critical point. Return 1 if finished, otherwise 0."""
        self.pos = self.nextpoint
        self.nextpoint = self.Grid.get_CP(idx)  # Get the next point
        self.target.update_whole(self.pos, self.nextpoint)  # Update the line
        self.curheading= self.target.get_heading()
        self.distance = self.target.get_dist()
        self.Xc = 0
    
    #check if we have reached the target
    def check_target(self):
        #res represents the proximity needed to return true
        if self.Xc >= self.distance:
            self.mode = 2 #change to pivot mode
            return True
        else:
            return False
    
    #update the heading
    def update_yaw(self, yaw):
        #print(yaw)
        self.yaw = self.y-yaw
        if self.yaw < 0:
            self.yaw += 360
        

    #update all parameters
    def update_all(self, yaw, rconv, encoderr, encoderl):
        #if self.t == 0:
            #self.prev_time = ticks_us()
            #self.dt = ticks_diff(ticks_us, self.prev_time)
            #self.t += self.dt
        #else:
            #update romi position
            self.Xc += rconv / 2 * ((encoderr.get_position()-self.prevrencoder) + (encoderl.get_position()-self.prevlencoder))
            self.prevrencoder = encoderr.get_position()
            self.prevlencoder = encoderl.get_position()
            #now = ticks_us() #determine the delta time
            #self.dt = ticks_diff(now, self.prev_time)
            #self.prev_time = now
            #self.t += self.dt #update current time
            self.update_yaw(yaw) #update current yaw
            #update the romi position
            #self.pos.update_pos(-self.Xc * math.sin(math.radians(self.curheading)),
                #self.Xc * math.cos(math.radians(self.curheading)))
           

    #method to get heading error
    def get_error(self):
        return self.target.get_heading()- self.yaw
    
    #checks how close it has gotten to the next point in percentage
    def pdis_next(self):
        return abs(self.target.get_dist()/self.distance)
    
    #determine error in pivot driving mode
    def pivot(self, yaw, encoderr, encoderl):
        self.update_yaw(yaw) #update the romi yaw
        #print(self.yaw)
        e = self.get_error() #get the error from desired heading
        if abs(e) < 4:
            self.mode = 3
            self.curheading = self.yaw
            self.prevrencoder = encoderr.get_position()
            self.prevlencoder = encoderl.get_position()
        return e

    #determine error in straight driving mode
    def straight(self, yaw, yaw_rate, rconv, encoderr, encoderl):
        self.update_all(yaw, rconv, encoderr, encoderl) #update position
        return yaw_rate #return yaw_rate as error