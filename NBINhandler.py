class Inputhandler:
    def __init__(self, nb_input):
        self.nb_input = nb_input
        self.active_prompt = None  # Current active prompt
        self.curinput = False  # Ensures input is processed before adding a new prompt

    def add_prompt(self, message, min_val=None, max_val=None, shares=None):
        #Adds a prompt if none is currently active.
        if not self.curinput:  # Prevent duplicate prompts
            self.active_prompt = (message, min_val, max_val, shares)
            self.curinput = True  # Now waiting for user input
            print(message)

    def check(self):
        #Checks for user input and processes it if available.
        if not self.curinput:
            return False
        if self.nb_input.any():
            user_input = self.nb_input.get().strip()

            # Case 1: No validation needed (press enter to continue)
            if self.active_prompt[1] is None and self.active_prompt[2] is None:
                self.active_prompt = None  # Reset prompt
                self.curinput = False
                return True  

            # Case 2: Validate input within min/max bounds
            try:
                value = int(user_input)
                if self.active_prompt[1] <= value <= self.active_prompt[2]:
                    # Store input in shared variables if needed
                    if self.active_prompt[3]:
                        for share in self.active_prompt[3]:
                            share.put(value)
                    self.active_prompt = None  # Reset prompt
                    self.curinput = False
                    return True  
                else:
                    print(f"\nInvalid input. Enter a value between {self.active_prompt[1]} and {self.active_prompt[2]}.")
            except ValueError:
                print("\nInvalid input. Please enter an integer.")

        return False  # No valid input yet

