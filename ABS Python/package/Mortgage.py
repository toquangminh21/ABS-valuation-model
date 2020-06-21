'''
Mortgage Mixin class to provide mortgage-specific functionality, from Level 4
'''

# When you run this class program you get a ModuleNotFoundError, but your main program still works well. WTF?
from package.Loan import Loan
from package.FixedVariableLoans import FixedRateLoan, VariableRateLoan
from package.Asset import Asset
import logging

# Mixins do not inherit, b/c of diamond problem
class MortgageMixin(object):
    # Because the mixin will be inherited FIRST, we MUST have an __init__ function to ensure that the
    # later base class Loan __init__ gets called as well. Else, nothing gets called
    def __init__(self, term, rate, face, house=None):
        self._category = 'Mortgage Loan'
        # Exception handling. Raise an exception to notify the user and handle it
        if isinstance(house, House):
            self._house = house
        else:
            logging.error('User inputs {house} which is of type "{type}". The Mortgage expects a House-derived object'.format(house=house, type=type(house).__name__))
            raise TypeError('Mortgage must have a House asset. Please create a new Mortgage object.')
        super(MortgageMixin, self).__init__(term, rate, face, house)

    # Method to determine the premium of the monthly PMI
    # Must be mixed with a Loan, or else it will throw error
    'NOTE: PMI should only be EARLY at the beginning. Once principal gets paid down LATER, PMI is removed'
    def PMI(self, period):
        # Use the (EXPECTED) Loan base class balanceFormula() method to calculate outstanding balance at period t
        balance_at_period_t = super(MortgageMixin, self).balanceFormula(period)
        # Calculate LTV: outstanding balance at period t divided by the asset's, NOT loan's, initial value
        LTV = balance_at_period_t/self._house._value
        if LTV > 0.8:
            # Then the PMI = 0.75% of the outstanding balance at period t
            # Divide by 12 to get the monthly PMI
            'NOTE: PMI is paid on the LOAN BALANCE, not the ASSET. As loan gets paid down insurance should also go down'
            return 0.0075 * balance_at_period_t / 12
        # If LTV ratio < 80% asset's initial value, PMI is 0
        else:
            return 0

    # Overriding method to calculate monthly payment to adjust for PMI
    # Base method must still be implemented, because we're just CUSTOMIZING
    def monthlyPayment(self, period):
        # Get the regular, non-PMI payment from the (EXPECTED) Loan base class
        regularPayment = super(MortgageMixin, self).monthlyPayment()

        # Then, return the sum of the payment and PMI
        return regularPayment + self.PMI(period)

    def principalDueFormula(self, period):
        # Stuck here for a bit. First approach: I CUSTOMIZE the principalDueFormula DIRECTLY
        # But then, that method calls self.monthlyPayment(), and it's the MortgageMixin's rather than the Loan's
        # So it requires an argument for period, which I passed in, because the Loan's parameter is just a dummy
        return super(MortgageMixin, self).principalDueFormula(period)

        # interestDue = super(MortgageMixin, self).interestDueFormula(period)
        # Second approach: So I call interestDue to find the interestDue instead
        # return self.monthlyPayment(period) - interestDue
        # Third approach: I can also define self._regularPayment in the __init__ function and then reuse later.

# Create this class for testing purposes on inheritance. No __init__ on purpose.
class MortgageLoan(MortgageMixin, Loan):
    pass

'''
Exercise 2.2.6 and 2.2.7
'''

# __init__ to get self.category for __repr__ display
class House(Asset):
    def __init__(self, value, depreciation):
        super(House, self).__init__(value, depreciation)
        self._category = 'House'


class PrimaryHome(House):
    # Same comments as above: default annual depreciation rate is 3%. User must enter a value. Pass in to Asset
    def __init__(self, value, depreciation=0.03):
        super(PrimaryHome, self).__init__(value, depreciation)
        self._category = 'Primary Home'

    def yearlyDepreciation(self):
        return self.depreciation


class VacationHome(House):
    # Same comments as above. Lower rate because vacation home it is often vacant
    def __init__(self, value, depreciation=0.01):
        super(VacationHome, self).__init__(value, depreciation)
        self._category = 'Vacation Home'

    def yearlyDepreciation(self):
        return self.depreciation
