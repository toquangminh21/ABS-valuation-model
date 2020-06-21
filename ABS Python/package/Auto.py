'''
Auto classes from level 3
'''

# When you run this class program you get a ModuleNotFoundError, but your main program still works well. WTF?

from package.Asset import Asset
from package.Loan import Loan
from package.FixedVariableLoans import FixedRateLoan, VariableRateLoan
import logging

# Similar to MortgageMixin, we create a Mixin for Auto


class AutoMixin(object):
    # Similar to a Mortgage, nothing specific to an Auto that needs to be initialized.
    # But we still call __init__ to make sure that the __init__ in the EXPECTED base class gets called
    # Expected base class: Loan. Loan has 3 parameters => Supply 3 parameters
    def __init__(self, term, rate, face, car=None):
        self._category = 'Auto Loan'
        # Exception handling. Raise an exception to notify the user and handle it
        if isinstance(car, Car):
            self._car = car
        else:
            logging.error('User inputs {car} which is of type "{type}". The AutoLoan expects a Car-derived object'.format(car=car, type=type(car).__name__))
            raise TypeError('AutoLoan must have a Car asset. Please create new.')
        super(AutoMixin, self).__init__(term, rate, face, car)


# No __init__ necessary, so that AutoMixin __init__ is called
# Will need 3 parameters to create a FixedAutoLoan object: ter, rate, face
class FixedAutoLoan(AutoMixin, FixedRateLoan):
    pass

# Car class derives from the base Asset class
# No __init__ so base Asset class automatically called
# Takes 1 parameter: value
class Car(Asset):
    pass


class Civic(Car):
    # The default annual depreciation of a Civic is 5% b/c it's a budget car. Only parameter user needs is value
    # User can change depreciation rate depending on their model, giving it flexibility
    def __init__(self, value, depreciation=0.05):
        # Call __init__ of the super class, which is Car, which calls Asset b/c Car doesn't have an __init__
        # Pass in the parameters
        super(Civic, self).__init__(value, depreciation)
        self._category = 'Civic'

    def yearlyDepreciation(self):
        return self.depreciation


class Lamborghini(Car):
    # Same comments as above. Annual depreciation rate for a Lamborghini is 10% b/c it's luxury
    def __init__(self, value, depreciation=0.1):
        super(Lamborghini, self).__init__(value, depreciation)
        self._category = 'Lamborghini'

    def yearlyDepreciation(self):
        return self.depreciation


class Lexus(Car):
    # Same comments as above. Annual depreciation rate for a Lamborghini is 8% b/c it's luxury
    def __init__(self, value, depreciation=0.08):
        super(Lexus, self).__init__(value, depreciation)
        self._category = 'Lexus'

    def yearlyDepreciation(self):
        return self.depreciation
