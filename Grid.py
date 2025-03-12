import math

class Grid:
    class Point:
            def __init__(self, x, y):
                """Initialize a point with x and y coordinates.""" 
                #mode represents the drive mode that we go to once a point is reached
                #0 for line 1 for Nav
                self.x = x
                self.y = y
            
            def distance_to(self, other):
                """Return the Euclidean distance to another Point."""
                return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

            def update_pos(self, dx, dy):
                """Calculate the points new position to another point."""
                self.x = self.x + dx
                self.y = self.y + dy
            
            def __repr__(self):
                return f"Point({self.x}, {self.y})"
    
    def __init__(self):
        """Initialize an bounded grid"""
        """bounds are the edges of the track: should be 
        a tuple (xmin, xmax, ymin, ymax) in millimeters"""
        """CPS is a list of Points representing the critical points"""
        self.grid_bo= (-127, 1700, -127, 1700)
        #start, CP0:self.Point(140, 857), CP1: self.Point(343, 857), CP2:  self.Point(0, 1465), 
        # 5s1:self.Point(305, 1518), CP3: self.Point(686, 1365), 
        # CP4, int, CP5, wall: self.Point(200, 0) ,5s2, after_cup,finish
        self.CPS = [self.Point(140, 857), self.Point(343, 857), self.Point(0, 1465), 
                    self.Point(500, 1600),  self.Point(686, 1365), self.Point(610, 750), 
                    self.Point(650, 150), self.Point(470, 150), self.Point(254, 378), 
                    self.Point(-15, 230), self.Point(0,0)]
                   #[CPO, CP1, CP2, 5s1, CP3, CP4, INT, CP5, 5s2, after_cup, finish]
                   #[0,    1,   2,   3,   4,   5,   6,    7,  8,  ,   9,        10]
    def set_CP(self, value: Point):
        """Set a value at a specific (x, y) coordinate."""
        self.CPS.append(value)

    def get_CP(self, idx):
        """Get the value at a specific (x, y) coordinate. Return default if not set."""
        return self.CPS[idx]