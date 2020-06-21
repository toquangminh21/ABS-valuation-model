'''
Game class for Monte Carlo simulation from Level 6
'''

import random, logging, time
from Player import Player
from Decorators import Timer, memoize

# Seed the random functions using the current time to ensure randomness
random.seed(time.time)

class Game(object):
    def __init__(self, player=Player):
        self.player = player


    @Timer
    # Method to play the game, first argument is the number of simulations
    # 1st parameter strategy must be either "stay" or "switch"
    def playGame(self, strategy, initialList, simulations):

        # Initialize win and loss counters
        winCounter = 0
        lossCounter = 0

        # Loop through the game n simulations
        for i in range(simulations):

            # Firstly, assign the prize to one of the 3 doors with uniform probability
            prizeDoor = random.choice(initialList)

            # Secondly, have the game\'s player choose a random door in the initialList and store in the initialDoor var
            initialDoor = self.player.initialChoice(initialList)

            # Filter out the initial doors, and store in remainingDoors
            remainingDoors = [door for door in initialList if door != initialDoor]

            # Loop through the remainingDoors and remove ALL the non-prize goat doors.
            montyDoor = [door for door in remainingDoors if door == prizeDoor]

            # if montyDoor has 1 element left, that must be the prizeDoor
            # if montyDoor is blank, that means the initialDoor must be the prizeDoor
            if montyDoor == []:
                # Then we just assign a random door from the remainingDoors list to montyDoor
                montyDoor.append(random.choice(remainingDoors))

            # Create a newList that contains the initialDoor and the montyDoor
            newList = [initialDoor, montyDoor[0]]

            # Debug codes
            # print('Initial list in iteration #{0}: {1}'.format(i+1, initialList))
            # print('Prize door in iteration #{0}: {1}'.format(i+1, prizeDoor))
            # print('Initial door in iteration #{0}: {1}'.format(i+1, initialDoor))
            # print('Remaining doors in iteration #{0}: {1}'.format(i+1, remainingDoors))
            # print('Monty door in iteration #{0}: {1}\n'.format(i+1, montyDoor))

            'Somehow this code gives double the probability for increasing list sizes. ' \
            'Ex: 10 doors: stay = 10%, switch = 20%. Very interesting.'
            # Loop through the remainingDoors and remove the non-selected, non-prize goat doors
            # for door in remainingDoors:
            #     if door != prizeDoor:
            #         # Remove the goat doors
            #         remainingDoors.remove(door)
            #         # Repeat until there is only 1 door left in the list
            #         if len(remainingDoors) == 1: break
            # newList now contains the initialDoor and prize door

            'Continued from line 45'
            # Query the player\'s finalDoor depending on his strategy

            # Will evaluate to initialDoor if strategy == "stay"
            # Will evaluate to montyDoor in the newList if strategy == "switch"
            finalDoor = self.player.strategy(strategy, newList)

            # If the finalDoor is the same as the prizeDoor, player wins and winCounter increments by 1
            if finalDoor == prizeDoor:
                winCounter += 1

            # Else, player loses and lossCounter increments by 1
            else:
                lossCounter += 1

        # After all the simulations are completed, we output the results
        print('Number of wins: {0}'.format(winCounter))
        print('Number of losses: {0}'.format(lossCounter))
        # and calculate the probability of success for the chosen strategy: # wins / # simulations
        print('Probability of success with "{0}" strategy: {1}'.format(strategy, winCounter/simulations))