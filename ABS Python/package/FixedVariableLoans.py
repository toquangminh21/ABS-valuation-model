'''
FixedRateLoan and VariableRateLoan classes
'''

# When you run this class program you get a ModuleNotFoundError, but your main program still works well. WTF?
from package.Loan import Loan

# Derives from Loan
class FixedRateLoan(Loan):
    # Nothing specific to a FixedRateLoan that needs its own __init__ function,
    # So technically, we don't even need to have an __init__ function
    # But I'll write one to call super() to invoke the base class __init__ function
    # In case the base class Loan's name is changed
    def __init__(self, term, rate, face, asset=None):
      # Equivalent to Loan.__init__(self, term, rate, face)
      # super(FixedRateLoan, self) will "translate" into Loan
      # Because this is a function within a function, self is implicitly passed in already
        super(FixedRateLoan, self).__init__(term, rate, face, asset)

    # Dummy period parameter, so that it's consistent with the VRL class
    def getRate(self, period=None):
        return self.rate

# Derives from Loan
class VariableRateLoan(Loan):
    # This time, an __init__ function is necessary, because the VRL class has a specific ratedict attribute
    # that must be initialized
    def __init__(self, term, rateDict, face, asset=None):
        self._rateDict = rateDict
        # Then we call the super to get the self.term and self.face attributes
        # as well as other getters/setters and Loan methods
        # None because a VRL should not have a rate attribute, it should have a rateDict attribute. Big difference
        # I.e. vrl.rate == None and vrl.rateDict == {0: 0.06, 18: 0.03}
        super(VariableRateLoan, self).__init__(term, None, face, asset)

    def getRate(self, period):
        # First, we put all the rateDict KEYS into a list, so we can sort and check where the period falls into
        # The expression "*" UNPACKS any ITERABLE OBJECT, and we put it between square brackets
        # Thus making it a list for our manipulation purposes
        # [*self.rateDict] would also works fine, because dictionaries return their keys when iterated through
        # [*self.rateDict.keys()] makes our intent more explicit, however, at the cost of TIME
        # Costs us a function look-up and invocation
        # https://stackoverflow.com/a/45253740

        # A simple if-else statement to validate that the period argument is between 0-360
        # self.term * 12 to convert into months.
        if period > self.term * 12:
            print('ERROR: the period must lie between 0 and the term of the mortgage!')
            # So it doesn't print out None
            return ''
        else:
            # Must use _rateDict b/c we don't have getters/setters yet => Use protected members
            periodList = [*self._rateDict.keys()]

            # Add the period into the list
            periodList.append(period)

            # Approach: Sort the list, then return the key that is IMMEDIATELY LOWER than the period
            # then return the VALUE of that KEY in the rateDict
            # 2 problems
            # 1) If the period is the same as the period change, this will NOT work because Python is searching FORWARD
            # 2) There should be a maximum upper bound to the period - the term of the loan
            # => we'll have to 1)search backward 2)argument validation, setting the upper bound for the argument

            # Put the list in reverse/descending order
            periodList.sort(reverse=True)
            # Find the index of the passed-in period in the list, then return the key that is
            # IMMEDIATELY LOWER than the period
            # Ex: timeline of 0 --> 180. Reverse list is [180, 0]. If 360 is passed in, list becomes [360, 180, 0]
            # The line below will then return 0+1 = 1st index, aka the rate for 180
            key = periodList[periodList.index(period) + 1]

            # then return the VALUE of that KEY in the rateDict, and that will be our rate for that period!
            return self._rateDict[key]

        # NOTE: argument validation:
        # The most Pythonic idiom is to clearly document what the function expects
        # and then just try to use whatever gets passed to your function
        # and either LET EXCEPTIONS PROPAGATE or just catch attribute errors and raise a TypeError instead
        # Type-checking should be avoided as much as possible as it goes against duck-typing.
        # Value testing can be OK – depending on the context.
