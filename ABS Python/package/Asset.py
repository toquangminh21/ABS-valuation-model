'''
Asset class from Level 5
'''

import logging


class Asset(object):
    # Initialization method; depreciation is in ANNUAL terms
    def __init__(self, value, depreciation=0):
        # If value is not a positive int or float, we log and raise TypeError
        if not isinstance(value, (int, float)) or value < 0:
            logging.error(
                'User inputs {value} which is of type "{type}". The parameter value expects a positive float or int'.format(
                    value=value, type=type(value).__name__))
            raise TypeError('value must be a positive float/integer. Please create a new Asset object.')
        else:
            self._value = value

        # If depreciation is not a float in the range of (0, 1), we log and raise TypeError
        if not isinstance(depreciation, (int, float)) or not 0 <= depreciation <= 1 :
            logging.error(
                'User inputs {depreciation} which is of type "{type}". The parameter depreciation expects a positive float or int'.format(
                    depreciation=depreciation, type=type(depreciation).__name__))
            raise TypeError('depreciation must be a positive float/integer. Please create a new Asset object.')
        else:
            self._depreciation = depreciation
    # Formatting purpose. See comments in base class Loan __repr__ function
    def __repr__(self):
        # Form: Asset: Value-Annual depreciation rate
        # Ex: PrimaryHome: 250000-0.03
        return '{className}: {value}-{depreciation}'.format(className=type(self).__name__, value=self._value, depreciation=self._depreciation)

    # Getters and setters for the member data
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, ivalue):
        self.value = ivalue

    @property
    def depreciation(self):
        return self._depreciation
    @depreciation.setter
    def depreciation(self, idepreciation):
        self.depreciation = idepreciation

    # Method to calculate monthly depreciation rate
    def monthlyDepreciation(self):
        return self.depreciation/12

    def currentValue(self, t):
        # The current value of a given asset at period t = initial value * total depreciation at time t
        # We implement this in code
        totalDepreciation = (1 - self.monthlyDepreciation()) ** t
        return self.value * totalDepreciation