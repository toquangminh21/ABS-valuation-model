'''
FixedMortgage and VariableMortgage classes
'''

# When you run this class program you get a ModuleNotFoundError, but your main program still works well. WTF?
from Loan.Loan import Loan
from Loan.FixedVariableLoans import FixedRateLoan, VariableRateLoan
from Loan.Mortgage import MortgageMixin

# Don't need to inherit from Loan, because VRL already does. If inherit, VM will get 2 copies of Loan attributes
# Diamond problem: D inherits from B and C, but still get access to A. D->B->C->A


class VariableMortgage(MortgageMixin, VariableRateLoan):
    def __init__(self, term, rateDict, face):
        # Call __init__ for MortgageMixin, which will then call __init__ for rateDict
        # And pass in the appropriate arguments
        super(VariableMortgage, self).__init__(term, rateDict, face)

class FixedMortgage(MortgageMixin, FixedRateLoan):
    # No __init__ on purpose, because nothing to be initialized.
    # No __init__ so that __init__ of MortgageMixin will be called
    # Both MortgageMixin and FRL take 3 parameters => we will have to supply 3 arguments when creating a FM object
    pass

