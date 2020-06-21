'''
Minh To
Thursday 5/29/2020
Exercises 6.1.3: Player and Game classes for Monte Carlo simulation
'''

import random, logging
logging.getLogger().setLevel(logging.INFO)

class Player(object):
    # No need for __init__

    # Method for Player to choose a random door from the initial list.
    def initialChoice(self, initialList):

        # Store it in an instance attribute for reference later in the strategy() method
        self.initialDoor = random.choice(initialList)

        # Return the initially chosen door
        return self.initialDoor

    # The Game class will whittle the newList down to only 2 doors now

    # Method to stay or switch, given the new list
    def strategy(self, strategy, newList):
        # If the player strategy is to switch
        if strategy == 'switch':
            # Then loop through the new list, which should only have 2 doors: initialDoor and montyDoor
            for door in newList:
                # ... and choose the montyDoor
                if door != self.initialDoor: return door

        # Else if strategy is to stay, stick with the initialDoor
        else:
            return self.initialDoor

    'NOTE: The 2 above classes must sandwich some code in the Game class'
