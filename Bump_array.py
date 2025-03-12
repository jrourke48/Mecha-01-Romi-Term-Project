
class Bump_array:
    #initialize the bump array
    #bmp_array is a list of IO pins connected to the bump sensors
    def __init__(self, bmp_array):
        self.bmp_array = bmp_array
        self.bump = 0
        
    def check_bump(self) -> bool:
        #Returns 1 if any bump sensor has been triggered
        for pin in self.bmp_array:
            if pin.value() == 0:
                self.bump = 1
                break 
            else:
                self.bump = 0
        return self.bump

    def get_bump(self) -> list[int]:
        #Returns a list of indices where a bump has occurred."""
        return [i for i, pin in enumerate(self.bmp_array) if pin.value()]
    
    def __str__(self):
        return f"Bump_array{self.bmp_array}"
    
   
        
