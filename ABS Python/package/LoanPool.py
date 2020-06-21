'''
LoanPool class from Level 4
'''

import numpy, random

# When you run this class program you get a ModuleNotFoundError, but your main program still works well. WTF?
from package.Loan import Loan
# For lambda use
import functools, logging

class LoanPool(object):
    # Because we don't know how many loans are in a given LoanPool/portfolio, we will have a default parameter blank list
    # Easier to work with .csv files than *args
    def __init__(self, loansList = []):

        # if user did not put in any list of Loan objects for the argument
        if not loansList:
            raise TypeError('ERROR: You didn\'t pass in any list of Loans for the parameters! Please create new')

        # loop through the loans in the loan list, and check if they are of type Loan. If yes, store in attribute
        for loan in loansList:
            if isinstance(loan, Loan):
                self._loansList = loansList
            else:
                logging.error('User inputs {loan} in the list which is of type {type}. The LoanPool expects a list of '
                              'Loan objects'.format(loan=loan, type=type(loan)))

                raise TypeError('ERROR: LoanPool object must have a list of Loan objects. Please create new.')

        self.reset()

##############################################
    # True __init__ function and reset mechanism to period 0 for multiple simulations
    def reset(self):

        # properties attribute is a dictionary that records all the payments of each period. Used to display Waterfall on the Assets side
        # initialize with period 0
        self.properties = {0: {'Principal': 0, 'Interest': 0, 'Total': 0, 'Balance': self.totalBalance(0), 'Recoveries': 0}}

        # Loop through underlying Loans and reset them too
        for loan in self:
            loan.reset()

    def __iter__(self):
        # Loop over the loan tuple and yield the individual loans
        for loan in self._loansList:
            yield loan

    @property
    def loansList(self):
        return self._loansList
    @loansList.setter
    def loansList(self, ituple):
        self._loansList = ituple


    '''
    2.2.5a
    '''
    # Loop over the loan tuple - yield the individual loans, return each of the face value, and sum them all up
    # Similar principles apply to all the other methods as well
    def totalPrincipal(self):
        return sum(loan.face for loan in self._loansList)

    '''
    2.2.5b
    '''
    # This method will throw an error if there is a variable rate loan in the mix, because variableLoan.rate == None
    # I will not handle this error case, because the course focuses on fixed loans, but I have no doubt I can solve it
    def totalBalance(self, period=0):
        return sum(loan.balanceFormula(period) for loan in self._loansList)

    '''
    2.2.5c)
    '''

    def totalPrincipalDue(self, period=0):
        return sum(loan.principalDueFormula(period) for loan in self._loansList)
    
    def totalInterestDue(self, period=0):
        return sum(loan.interestDueFormula(period) for loan in self._loansList)

    def totalPaymentDue(self, period=1):
        if period == 0:
            return 0
        return sum(loan.monthlyPayment(period) for loan in self._loansList)

    '''
    2.2.5d)
    '''
    def activeLoans(self, period):
        # Loop through all the individual loans in the tuple, access their outstanding balance at period t
        # and append them to a list
        return len([loan.balanceFormula(period) for loan in self._loansList if loan.balanceFormula(period) > 0.])
        # for loan in self._loansList:
        #     loanBalanceList.append(loan.balanceFormula(period))
        # # If-else to remove any loan that has a balance of <= 0.001, because
        # # 1) at t = 360 some loans have a balance of a tiny amount but not exactly 0, i.e 5e-18, so 0.001 to catch this
        # # 2) the outstanding balance formula will still work if user inputs a period over the loan's term
        # # but it will be NEGATIVE, so we must account for NEGATIVE balance
        #
        # # List comprehension: return the LENGTH of a list of POSITIVE balances at period t
        # return len([balance for balance in loanBalanceList if balance > 0.1])


    '''
    2.2.5e) Lambda is unreadable. Not using that.
    '''
    # First, create a list of the weights of each individual loan in the portfolio
    def calcWAM(self, period):
        # List that has the outstanding balance at period t
        # Access the individual loans' balanceFormula() method to calculate their outstanding balance at period t
        # and put in a list
        balanceList = [loan.balanceFormula(period) for loan in self._loansList]

        # List that has the weight percentages of the individual loans at period t
        # Loop through the loans and divide their balance by the total balance at period t
        # Balance will dip into negative, which will affect our calculation, so we filter out any negative balance
        # Problem: self.totalBalance(period) does NOT filter out negative values. Solution:
        weightList = [balance/self.totalBalance(period) for balance in balanceList if balance > 0.1]

        # List that has the years left to maturity. Unit is years not months, so we use annualized period: divide by 12
        # Maturity will also dip into negative, which will affect our calculation, so we filter IN if maturity > 0
        maturityList = [loan.term - period / 12 for loan in self._loansList if loan.term - period / 12 > 0]

        # Debugging
        # print('weightList: ' + str(weightList))
        # print('maturityList: ' + str(maturityList))

        # Ex: [.25, .5, .25] and [28.3, 15.6, 12.9]
        # Zip 2 list -> List comprehension to put them in tuple pairs and multiply them -> Sum up and return the result
        # Literally Excel Sumproduct
        return sum([weight * maturity for weight, maturity in zip(weightList, maturityList)])

    def calcWAR(self, period):
        # Similar principles like .calcWAM() method above: find the weight using 2 list comps. See comments above
        balanceList = [loan.balanceFormula(period) for loan in self._loansList]
        weightList = [balance/self.totalBalance(period) for balance in balanceList if balance > 0.1]

        # Will throw an error if a VRL is in the mix because VRL.rate == NoneType
        # Although I have already implemented a .getRate() function for VRL
        # Will also throw an error if a class inherits from the base Loan class instead of the recommended FRL/VRL
        # Because the base class getRate() method is Not Implemented
        # 10-minute BUG: also have to filter out, but rate is constant unlike maturity, so have to filter out by balance
        rateList = [loan.rate for loan in self._loansList if loan.balanceFormula(period) > 0.1]

        # Debugging
        # print('weightList: ' + str(weightList))
        # print('rateList: ' + str(rateList))

        # Return sum of weighted interest rates, rounded to 5 decimals
        return round(sum([weight * rate for weight, rate in zip(weightList, rateList)]), 5)

    '''
    Final Project Part 2:
    Record the Assets Waterfall for each period
    '''
    # Method to record the total payments, both principal and interest, and balance of the LoanPool and each individual loans
    # for the passed in period
    def getWaterfall(self, period):
        self.properties[period] = {}
        # Recording recoveries code is in the checkDefaultsReturnRecovery() method
        self.properties[period]['Principal'] = self.totalPrincipalDue(period)
        self.properties[period]['Interest'] = self.totalInterestDue(period)
        self.properties[period]['Total'] = self.totalInterestDue(period) + self.totalPrincipalDue(period)
        self.properties[period]['Balance'] = self.totalBalance(period)

        ##### Disabled

        # # Loop through the individual loans the LoanPool object holds, and record their waterfall
        # for loan in self:
        #     loan.properties[period] = {}
        #     loan.properties[period]['Principal'] = loan.principalDueFormula(period)
        #     loan.properties[period]['Interest'] = loan.interestDueFormula(period)
        #     loan.properties[period]['Total'] = loan.interestDueFormula(period) + loan.principalDueFormula(period)
        #     loan.properties[period]['Balance'] = loan.balanceFormula(period)

    '''
    Final Project Part 3:
    Build in a simplistic default model: assume that ALL loans in the pool has an equal probability of defaulting
    and they are more likely to default in later periods. In reality, can refine further by looking at 
    1) income-to-loan ratio: lower ratio means more likely to default
    '''
    '''
    Default table:
    
    Period range    Default probability
    1-10            0.0005
    11-60           0.001
    61-120          0.002
    121-180         0.004
    181-210         0.002
    211-360         0.001
    '''


    '''
    period: period of the loanPool
    :return: total cumulative recovery value of all the defaulted loans in the loanPool in that period
    '''
    def checkDefaultsReturnRecovery(self, period):
        defaultDictionary = {range(1, 11): 0.0005, range(11, 61): 0.001, range(61, 121): 0.002,
                             range(121, 181): 0.004, range(181, 211): 0.002, range(211, 361): 0.001}

        # Initialize total recovery for the period
        totalRecovery = 0

        # Range = 1/default probability so that the odds of picking a number in that range
        # is equal to the odds of a loan defaulting in that period
        for Range in defaultDictionary:
            if period in Range:
                upperBound = 1 / defaultDictionary[Range] - 1  # -1 because we start at 0

        for loan in self:
            # the odds of picking a number in this range is equal to the odds of a loan defaulting in that period
            randomNum = random.randint(0, upperBound)
            # checkDefaultReturnRecovery method in the Loan class will pass in the parameters to register if the loan defaults
            # It also return the recovery value of any defaulted loan in the period and we sum those up
            loanRecovery = loan.checkDefaultReturnRecovery(randomNum, period)
            totalRecovery += loanRecovery

        return totalRecovery