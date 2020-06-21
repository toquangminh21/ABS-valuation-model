'''
Minh To
Monday, 6/1/2020: A New Hope (1977)
Tranche class
'''

import logging, numpy
'NOTE: The classes will not be using private members. We are all adults here. Dont access the forbidden fruit.'

# Abstract base class. No methods. Set up for attributes and argument validation
class Tranche(object):
    # totalNotional: the value of the tranche
    # rate: the interest rate of the tranche
    # subordination: seniority/cash flow priority of the tranche. 'A' for senior, 'B' for subordinated. Use for outputting
    def __init__(self, notional, rate, subordination):
        # Argument validation
        if isinstance(notional, (float, int)):
            self.notional = notional
        else:
            logging.error('totalNotional must be a float')

        if isinstance(rate, float) and rate < 1:
            self.rate = rate
        else:
            logging.error('rate must be a float that is less than 1')

        self.subordination = subordination

        # True __init__ function
        self.reset()

##############################################
    # True __init__ function and reset mechanism to period 0 for multiple simulations
    def reset(self):

        # Set each object period when instantiated to 0
        # Object-level > class-level attribute because we want each new instance to have its own period, not shared
        self.period = 0

        # Create an attribute to store the totalNotional balance for the current period, because many calculations are dependent on it
        self.currentNotionalBalance = self.notional

        # properties attribute: dict of dicts, to store the tranche's corresponding properties (principal payment, interest payment, totalNotional balance, etc.) for each PERIOD (key)
        self.properties = {self.period: {}}
        # Initialize the tranche's properties to 0
        self.properties[self.period]['Interest due'] = 0
        self.properties[self.period]['Interest payment'] = 0
        self.properties[self.period]['Interest shortfall'] = 0

        self.properties[self.period]['Principal due'] = 0
        self.properties[self.period]['Principal payment'] = 0
        self.properties[self.period]['Notional balance'] = self.currentNotionalBalance
        self.properties[self.period]['Principal shortfall'] = 0

        # Quick fix so that TotalCollections in 13MAIN work
        self.properties[-1] = {}
        self.properties[-1]['Cash reserve'] = 0

        self.properties[self.period]['Cash reserve'] = 0


    def __repr__(self):
        return f'{type(self).__name__}: {self.notional}-{self.rate}-{self.subordination}'

##############################################
    ##### IRR: the interest rate that results in the NPV of the tranche to be 0
    # Assumption: each tranche is bought at its notional amount
    # Method to store all the cashflows of a tranche to a list, so we can use the numpy.irr to calculate IRR of the tranche

    # Method to return the IRR of a tranche
    def IRR(self):
        # Loop through all the periods and store the inflows to the list
        cashFlows = [-self.notional]
        # Derived classes will have a properties attribute to track cashflows
        # Loop through period 1 to the last period that the tranche has on record
        for period in range(1, self.period + 1):
            cashFlows.append(self.properties[period]['Principal payment'] + self.properties[period]['Interest payment'])
        # Return the IRR, multiplied by 12 to annualize
        return round(numpy.irr(cashFlows) * 12, 4)

##############################################
    ##### RIY: Reduction in yield: tranche rate less the annual IRR.
    # RIY specifies how much the investor lost out on => Maximum = 100% + tranche rate
    # used to give a letter rating to the security. The smaller the better for the investor

    def RIY(self):
        # Quoted in bps. Round to a whole number and multiply by 100 for numpy.arange to work
        RIY = round((self.rate - self.IRR()) * 10000, 0) * 100

        # ratingDict of appendix A
        ratingDict = {'Aaa': numpy.arange(0, 6), 'Aa1': numpy.arange(6, 67), 'Aa2': numpy.arange(67, 130),
                'Aa3': numpy.arange(130, 270),
                'A1': numpy.arange(270, 520), 'A2': numpy.arange(520, 890), 'A3': numpy.arange(890, 1300),
                'Baa1': numpy.arange(1300, 1900), 'Baa2': numpy.arange(1900, 2700)
            , 'Baa3': numpy.arange(2700, 4600), 'Ba1': numpy.arange(4600, 7200), 'Ba2': numpy.arange(7200, 10600),
                'Ba3': numpy.arange(10600, 14300), 'B1': numpy.arange(14300, 18300)
            , 'B2': numpy.arange(18300, 23100), 'B3': numpy.arange(23100, 31100), 'Caa': numpy.arange(31100, 250000),
                'Ca': numpy.arange(250000,
                                   99999900)}  # in case IRR is lower than -100% because defaults happen too early
        # give the RIY a letter grade
        for letterGrade in ratingDict:
            if int(RIY) in ratingDict[letterGrade]:
                return int(RIY / 100), letterGrade

##############################################
    ##### AL: Average life: average time that each dollar of a tranche's unpaid principal remains unpaid
    ##### some tranches get paid down (0 balance) quicker than others, while some never get fully paid down at all.
    # Metric to get a sense of how long it will take them to recoup their principal
    # (will they get most of it back early on in the waterfall, or will it take closer to the end)?


    def AL(self):

        # if at the final period, balance is zero, which means it's paid off, use the formula
        if self.properties[self.period]['Notional balance'] <= 0.001:
            # Formula: inner sumproduct of the time period numbers (0, 1, 2, 3, etc.) and the principal payments,
            # divided by the initial principal.
            sum = 0
            for i in range(self.period + 1):
                sum += i * self.properties[i]['Principal payment']
            return sum / self.notional

        # if not, return None
        else:
            return None



# Derived class from abstract Tranche base class
class StandardTranche(Tranche):

    # See comments in Tranche class regarding parameters
    def __init__(self, notional, rate, subordination):
        # Call super to get the Tranche's attribute
        super(StandardTranche, self).__init__(notional, rate, subordination)
        # All the initialization code is in the reset method, so that we dont have to repeat code when we need to reset the tranche
        self.reset()


##############################################
    # Method to increase the time period of the tranche by 1
    def increaseTimePeriod(self):

        # A period cant be blank, so raise an error if principal/interest payments are not yet recorded before trying to increase the period
        if 'Principal payment' not in self.properties[self.period]:
            raise Exception('Principal payment has not been recorded for this period yet. Record before incrementing period')
        if 'Interest payment' not in self.properties[self.period]:
            raise Exception('Interest payment has not been recorded for this period yet. Record before incrementing period')

        # Increment time period by 1, and add it as a new key to the properties dictionary
        # The value will be a dictionary that contains all the info (principal/interest payment, etc.) for the corresponding period
        self.period += 1
        self.properties[self.period] = {}

##############################################
    # Method to RECORD the PRINCIPAL PAYMENT for the current OBJECT time period, using a dict
    # Input is the amount of principal payment to be recorded
    def makePrincipalPayment(self, principalPayment):

        # If the tranche's principal payment for the current period has already been recorded, raise an Exception
        if 'Principal payment' in self.properties[self.period]:
            raise Exception(f'Principal payment for period {self.period} has already been recorded')

        # If its not recorded yet, record the principal payment and call the notionalBalance() method to update the currentNotionalBalance for the current period
        self.properties[self.period]['Principal payment'] = principalPayment
        self.properties[self.period]['Notional balance'] = self.notionalBalance()

        # If the tranche's notional for the current period is paid down to 0, tranche has no more principal payment due
        # => Record everything as 0
        if self.currentNotionalBalance <= 0.001:
            self.properties[self.period]['Principal due'] = principalPayment

        # Principal shortfall recording and adding to next period will be done in the StructuredSecurities makePayments() method,
        # Because we cant find principal due here, it's only found in the SS object with the underlying loanPool

##############################################
    # Method to RECORD the INTEREST PAYMENT for the current OBJECT time period, using a dict
    # Input is the amount of interest payment to be recorded
    def makeInterestPayment(self, interestPayment):

        # If the tranche's interest payment for the current period has already been recorded, raise an Exception
        if 'Interest payment' in self.properties[self.period]:
            raise Exception(f'Interest payment for period {self.period} has already been recorded')

        # Or if the interest due for the current period is 0, record everything as 0
        # Find interest due for the current period by calling the object-level method interestDue(), defined below
        if self.interestDue() <= 0.001:
            self.properties[self.period]['Interest due'] = 0
            self.properties[self.period]['Interest payment'] = 0
            self.properties[self.period]['Interest shortfall'] = 0

        # If there's no problem, record the interest payment and interest due for the current period
        self.properties[self.period]['Interest due'] = self.interestDue()
        self.properties[self.period]['Interest payment'] = interestPayment

        # Interest shortfall = max of 0 and difference b/w interest due and interest payment
        self.properties[self.period]['Interest shortfall'] = max(0, self.interestDue() - interestPayment)

##############################################
    # principalDue formula will be in the StructuredSecurities class makePayments() method
    # Because principal due is based on the underlying loanPool

##############################################
    # Method to return the amount of interest due for the current time period
    # Formula: totalNotional balance of the previous time period * rate + interest shortfalls in the previous period
    def interestDue(self):
        self.currentInterestDue = self.properties[self.period - 1]['Notional balance'] * self.rate/12 + self.properties[self.period - 1]['Interest shortfall']
        return self.currentInterestDue

##############################################
    # Method to RETURN the totalNotional owed to the tranche for the CURRENT OBJECT time period (after all the payments are made)
    # Because its for the object's current period, no parameters are needed
    def notionalBalance(self):
        # Formula: totalNotional of previous period - principal payment of current period
        self.currentNotionalBalance = self.properties[self.period - 1]['Notional balance'] - self.properties[self.period]['Principal payment']
        return self.currentNotionalBalance


