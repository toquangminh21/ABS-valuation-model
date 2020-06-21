'''
Timer class from level 5
'''

import time, logging
# Make sure that our info-level logging statements get outputted to the screen, replacing print statements
logging.getLogger().setLevel(logging.INFO)

class Timer(object):
    # Warn logging statement to warn the user if time taken exceeds 1 minute
    _warnThreshold = 60

    # Initialize with default parameter timerName, in case user wants to name their timer
    def __init__(self, timerName='timer', unit='seconds'):
        # This attribute is used to later store the last timer result so one can retrieve it
        self.lastTime = None
        # This attribute serves as the toggle for error handling purpose when a person presses on without turning off
        self.on = False
        # This attribute allows the user to get and set the unit
        self.unit = unit
        # This attribute allows the user to rename their timer
        self.timerName = timerName

    # Copy and paste from .start() method, with some changes
    def __enter__(self):
        # Because when we use context manager, we don't need to check if the timer has already been turned on or not
        # We don't even need toggles and if statements - it should run because there is only 1 with statement
        self.start_time = time.time()
        # Return the timer self, so that the with statement stores the timer object in a variable for you to manipulate
        return self

    # Copy and paste from .end() method, with some changes
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        result = self.end_time - self.start_time
        # Display the result with the units chosen, rounded to 5 digits
        if self.unit == 'seconds':
            pass
        if self.unit == 'minutes':
            Timer._warnThreshold /= 60
            result /= 60
        if self.unit == 'hours':
            Timer._warnThreshold /= 3600
            result /= 3600

        # If-else to check if it takes more than 1 minute for the block to execute
        if result <= Timer._warnThreshold:
            logging.info('{timerName}: {result} {unit}'.format(timerName=self.timerName, result=round(result, 5), unit=self.unit))
        else:
            logging.warning('Took more than 1 minute: {timerName}: {result} {unit}'.format(timerName=self.timerName, result=round(result, 5), unit=self.unit))

        # Store the result in the lasttime attribute
        self.lastTime = result



    # Alternative, non-Pythonic way to get/set unit for the timer
    def getUnit(self):
        logging.info('The current unit for "{timerName}" is: {unit}'.format(timerName=self.timerName, unit=self.unit))

    def setUnit(self, unit):
        # Can only set unit to 1 of the 3 options
        if unit in ('seconds', 'minutes', 'hours'):
            self.unit = unit
            logging.info('You have successfully set unit to {unit} for "{timerName}"'.format(unit=unit, timerName=self.timerName))
        # If unit is invalid, logging.info out error message
        else:
            logging.error('ERROR! Invalid unit passed in: "{unit}". Options include: "seconds", "minutes", or "hours".'
                  ' Timer defaulted to seconds.'.format(unit=unit.upper()))

    # Property methods to getter/setter unit of the timer
    # @property
    # def unit(self):
    #     return self.unit
    # @unit.setter
    # def unit(self, input_unit):
    #     # Can only set unit to 1 of the 3 options
    #     if input_unit == 'seconds' or 'minutes' or 'hours':
    #         self.unit = input_unit
    #         logging.info('You have successfully set unit to ', input_unit)
    #     # If unit is invalid, logging.info out error message
    #     else:
    #         logging.info('ERROR! please enter a correct unit. Options include: "seconds", "minutes", or "hours"')