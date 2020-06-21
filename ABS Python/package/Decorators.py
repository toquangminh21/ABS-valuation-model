'''
Decorator functions from 5.2.1 and 5.2.2
'''

import time
from functools import wraps

'5.2.1: Timer'

##### Decorator Timer function
def Timer(function):
    # Protect wrapped function string representation
    @wraps(function)
    # wrapped function to be timed. Take variable-length parameters so it can work with any generic function
    def timedFunction(*args, **kwargs):
        start = time.time()
        # Invoke the function that was passed-in, aka the one that will be decorated, and pass in arguments
        res = function(*args, **kwargs)
        end = time.time()
        difference = end - start
        print('Function {0}: {1} seconds'.format(function, difference))

        return res

    return timedFunction

'5.2.2: Memoization'

# Empty cache dictionary for appending purposes
dictionary = {}

# Decorator memoization function
def memoize(function):
    @wraps(function)
    def memoizedFunction(*args, **kwargs):
        # Variable to store the key of the cache dictionary in a tuple
        parameterTuple = (args, tuple(kwargs.values()))
        # If the passed-in arguments tuple is not a key in the dictionary
        if parameterTuple not in dictionary.keys():
            # Then run the process-intensive function, and store that value in a newly created key in the dictionary
            dictionary[parameterTuple] = function(*args, **kwargs)
        # Return the value corresponding with the tuple of arguments
        return dictionary[parameterTuple]

    return memoizedFunction

    # Dictionary keys will consist of tuples of 2 sub-tuples: 1st is positional *args and 2nd is **kwargs
    # Dictionary values will consist of integers
    # print(dictionary)

    # Regular functions for Test 2 in 5.2.2
def searchExt(treeStructure, extension=''):
    for (pathStr, subdirsList, filesList) in treeStructure:
        # Loop through the FILES LIST and only YIELD the ones with a .py extension
        for files in filesList:
            if files.endswith(extension): yield '{path}\\{files}'.format(path=pathStr, files=files)