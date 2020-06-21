'''
Abstract Loan class
scroll to bottom for Monte Carlo ABS Loan default methods
'''

from package.Asset import Asset
import logging


class Loan(object):
    def __init__(self, term, rate, face, asset=None):
        # term: MONTHLY periods of the loan, in order to display Waterfall correctly
        # rate: ANNUAL rate
        # face: face value

        # if term is not a positive integer, we log the error and raise an exception
        if not isinstance(term, int) or term < 0:
            logging.error('User inputs {term} which is of type "{type}". The parameter term expects a positive integer'.format(term=term, type=type(term).__name__))
            raise TypeError('Term must be a positive integer. Please create a new Loan object.')
        # else, if term is valid, we save it to an object attribute
        else:
            self._term = term

        # if rate is not a float that is less than or equal to 1, we log the error and raise an exception
        if not isinstance(rate, float) or rate > 1:
            logging.error('User inputs {rate} which is of type "{type}". The parameter rate expects a <= 1 float'.format(
                    rate=rate, type=type(rate).__name__))
            raise TypeError('rate must be a positive integer. Please create a new Loan object.')
        # else, if rate is valid, we save it to an object attribute
        else:
            self._rate = rate

        # if face is not a float or int that is greater than 0, we log the error and raise an exception
        if not isinstance(face, (float, int)) or face < 0:
            logging.error('User inputs {face} which is of type "{type}". The parameter face expects a >= 1 float or int'.format(
                    face=face, type=type(face).__name__))
            raise TypeError('face must be a positive float/integer. Please create a new Loan object.')
        # else, if face is valid, we save it to an object attribute
        else:
            self._face = face


        # if asset is not an Asset-derived object, we log the error and raise an exception
        if not isinstance(asset, Asset):
            logging.error(
                'User inputs {asset} which is of type "{type}". The parameter expects an Asset object'.format(
                    asset=asset, type=type(asset).__name__))
            raise TypeError('asset must be an Asset-derived object. Please create a new Loan object.')
        # else, if asset is valid, we save it to an object attribute
        else:
            self.asset = asset

        self.reset()

##############################################
    # True __init__ function and reset mechanism to period 0 for multiple simulations
    def reset(self):

        # Reset to period 0 where no loan has defaulted
        self.isDefault = False

        # properties attribute is a dictionary that records all the payments of each period.
        # Used to display Waterfall on the Assets side. Initialize with period 0
        self.properties = {0: {'Principal': 0, 'Interest': 0, 'Total': 0, 'Balance': self.balanceFormula(0)}}


    def __repr__(self):
        # Will return the string of the object, which will be invoked when print() or just variable name only
        # Form: NameOfTheClass (term, rate, face). Ex: FixedAutoLoan (30, 0.06, 300000)
        return f'{type(self).__name__}: {self.term * 12}-{self.rate}-{self.face}'

    # Getters and setters for all attributes, all in ANNUAL terms
    @property
    def term(self):
        # Convert to self.term to ANNUAL basis for cleaner formulas
        return self._term / 12
    @term.setter
    def term(self, iterm):
        self._term = iterm

    @property
    def rate(self):
        return self._rate
    @rate.setter
    def rate(self, irate):
        self._rate = irate

    @property
    def face(self):
        return self._face
    @face.setter
    def face(self, iface):
        self._face = iface

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, itype):
        self._type = itype

    '''
    Exercise 2.1.2: Object-level methods to find monthly payments, total payment, and total interest
    '''
    # Method to find monthly payment, with period as the dummy parameter
    # Delegates to the class-level method
    def monthlyPayment(self, period=0):
        # When the loan matures OR it is defaulted, it shouldnt produce any more monthly payment. Cap it at 0
        if self.isDefault or period > self.term * 12:
            return 0
        return Loan.calcMonthlyPmt(self.term, self.rate, self.face)
        # # Implement the formula to determine periodic payment
        # numerator = self.rate * self.face * (1 + self.rate) ** (self.term)
        # denominator = (1 + self.rate) ** self.term - 1
        # pmt = numerator / denominator
        # return pmt

    # Object-level method so we must adjust for self.term
    def totalPayment(self):
        # Simply multiply the monthly payment with the number of periods
        # Multiply term by 12 because self.term is in annual
        return self.monthlyPayment() * self.term * 12

    # Similar to totalPayment, this is an object-level method
    # however, we don't adjust for self.face b/c it's not annual or monthly.
    def totalInterest(self):
        # Simply subtract the principal from the total payment, the rest is interest
        return self.totalPayment() - self.face

    '''
    Exercise 2.1.3: Recursion vs Formula
    '''

    # RECURSION
    def interestDueRecursion(self, period):
        # Call the balanceRecursion(period-1) to find the outstanding principal of the previous period
        # self.rate/12 because user's input is annual
        return self.rate/12 * self.balanceRecursion(period - 1)
    def principalDueRecursion(self, period):
        # Call the interestDueRecursion to find the interest due of the same period
        return self.monthlyPayment() - self.interestDueRecursion(period)
    def balanceRecursion(self, period):
        # Base case: when loan is first issued, the outstanding principal is equal to the face value
        # The loop will eventually return to this case
        if period == 0:
            return self.face
        # Other periods: outstanding = previous period's outstanding - principal due this period
        else:
            return self.balanceRecursion(period - 1) - self.principalDueRecursion(period)

    # FORMULA
    def interestDueFormula(self, period):
        # Object level method so we must adjust for self.rate which is originally in annual terms
        if self.isDefault == False:
            return self.rate/12 * self.balanceFormula(period - 1)
        else:
            return 0
    def principalDueFormula(self, period):
        # Pass in period for the monthlyPayment method, it doesn'period matter anyway because the parameter is a dummy,
        # But MortgageMixin efficiency in Exercise 2.2.2 forces you to put in
        # So that the MortgageMixin one has a "real" period parameter
        if self.isDefault == False:
            return self.monthlyPayment(period) - self.interestDueFormula(period)
        else:
            return 0
    def balanceFormula(self, period):
        # If the loan is not defaulted, return the value
        if self.isDefault == False:
            return Loan.calcBalance(self.term, self.rate, self.face, period)
        # If it is defaulted, return 0 for the balance
        else:
            return 0

    '''
    Exercise 2.1.4: class-level methods
    '''
    # It's important to get the class-level method right, because all the object-level methods delegate to them
    # It's OK to have a messy formulas in the class-level methods, it is way more important to centralize
    # the action so it's easier to debug.
    @classmethod
    def calcMonthlyPmt(cls, term, rate, face):
        # Convert annual to monthly to clean up formulas implementation
        term *= 12
        rate /= 12

        # Implement the formula to determine periodic payment
        numerator = rate * face * (1 + rate) ** term
        denominator = (1 + rate) ** term - 1
        pmt = numerator / denominator
        return pmt

    @classmethod
    def calcBalance(cls, term, rate, face, period):

        # EVERYTHING RESTS on this class-level method. Ensure that it is bug-free (formula, floor of 0, etc.)
        # Implement the formula and adjust rate so that it is in monthly terms
        # Will not use static method because it is too long. rate/12 -> Loan.monthlyRate(rate)
        # Readability, but too inconvenient.

        left_side = face * ((1 + rate/12) ** period)
        right_side = Loan.calcMonthlyPmt(term, rate, face) * ((((1 + rate/12) ** period) - 1) / (rate/12))
        result = left_side - right_side
        # Debug-level log: general formula and steps
        logging.debug('To find the outstanding balance, calculate a subtraction using a formula seen in the code.')
        # Debug-level log: Print out all the values and types of all the variables to see where it may have gone wrong
        logging.debug(
            'left side value: {0}, right_side value: {1}, payment value: {2}'.format(left_side, right_side, result))
        logging.debug(
            'left side type: {0}, right_side type: {1}, payment type: {2}'.format(type(left_side), type(right_side),
                                                                                   type(result)))
        # Cap the FLOOR of the balance at 0, can't have a negative balance!
        return result if result > 0.1 else 0

    '''
    Exercise 2.1.5: Static-level methods    
    '''
    @staticmethod
    # Static method to convert a passed-in ANNUAL rate to MONTHLY
    def monthlyRate(rate):
        return rate/12

    @staticmethod
    # Static method to convert a passed-in MONTHLY rate to ANNUAL
    # Reminder: we can use "rate" again as the parameter even when we already used it in monthlyRate
    # because it's a LOCAL function, it will disappear as soon as the function is done. No global like COBOL
    def annualRate(rate):
        return rate*12

    '''
    Exercise 2.2.1: Inheritance
    '''

    # Method that is meant to be overridden
    # if we name the method .rate(), it weirdly throws an error in our class-level calcMonthlyPmt,
    # because Python interprets the rate PARAMETER as the rate METHOD
    # When you pass a METHOD into a function as a PARAMETER, you don't need the (), hence the confusion
    def getRate(self, period=None):
        '''
        This should be overridden in the derived classes.
        :return: the rate for a passed in period.
        '''
        raise NotImplementedError()


    '''
    Exercise 2.2.7d) recoveryValue
    '''
    'NOTE: ‘recovery value’ of an asset, in terms of a loan, is the amount of money' \
    ' the lender can recover if the borrower defaults ' \
    ' As the lender is not likely to receive full market value of the property, we assume a 60% recovery for all assets'

    def recoveryValue(self, period):
        # Find the current value of the ASSET at the given period t, and multiply by 0.6
        try:
            return self.asset.currentValue(period) * 0.6
        except AttributeError:
            raise AttributeError('Loan object does not have a .asset attribute. Create a new Loan that has an Asset!')

    def equity(self, period):
        # Equity of the asset owner = asset current value - loan's outstanding balance, at a given period t.
        try:
            return self.asset.currentValue(period) - self.balanceFormula(period)
        except AttributeError:
            raise AttributeError('Loan object does not have a .asset attribute. Create a new Loan that has an Asset!')

    '''
    FINAL PROJECT: Build in a simplistic default model: assume that ALL loans in the pool has an equal probability of defaulting
    and they are more likely to default in later periods. In reality, can refine further by looking at 
    1) income-to-loan ratio: lower ratio means more likely to default
    '''

    '''
    randomNumber: a randomNumber which will be supplied by the LoanPool checkDefaultsReturnRecovery() method
    period: period of the loan
    :return: recovery value if the loan defaults for the first time, or 0
    '''
    def checkDefaultReturnRecovery(self, randomNumber, period):
        # If the loan defaults...
        if randomNumber == 0:
            # Return the recovery value of the asset, if this is the "first time" it defaults
            # Because the model allows for defaulting multiple times, but in reality you can only get recovery value once
            if self.isDefault == False:
                # Toggle it to default
                self.isDefault = True
                # Return the recovery value for the individual defaulted loan
                return self.recoveryValue(period)
            # If it already defaulted, return 0 because nothing to recover
            else:
                return 0
        else:
            return 0