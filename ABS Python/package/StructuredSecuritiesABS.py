'''
Minh To
Monday, 6/15/2020: Get back
StructuredSecurities class
'''

import logging
from package.Tranche import StandardTranche
from package.LoanPool import LoanPool

# This class is a composition of Tranche objects (similar to how LoanPool is a composition of Loans)
class StructuredSecurities(object):
    def __init__(self, loanPool):
        if isinstance(loanPool, LoanPool):
            self.loanPool = loanPool
        else:
            logging.error('StructuredSecurities object must have a loanPool parameter')

        # trancheList: the internal list of underlying tranches the Structured Security has
        # Factory method addTranche() below to append tranches to this list
        self.trancheList = []

        self.reset()

##############################################
    # True __init__ function and reset mechanism to period 0 for multiple simulations
    def reset(self):
        self.period = 0

        # totalNotional: the total notional amount of the underlying loan pool
        self.totalNotional = self.loanPool.totalPrincipal()

        # establish a cash reserve account that will be used to supplement payments if there are cash leftover after all payments
        self.cashReserve = 0

        # Reset the underlying loanPool as well as all the tranches to period 0
        self.loanPool.reset()
        for tranche in self:
            tranche.reset()

    # Method to turn the class into a generator that can loop through its tranches:
    def __iter__(self):
        for tranche in self.trancheList:
            yield tranche


    # Factory method to add tranches to the StructuredSecurity object
    def addTranche(self, trancheClass, percentNotional, rate, subordination):
        # tranceClass: StandardTranche, IOTrance, or POTrance
        # percentNotional: percentage of the deal's notional the tranche has
        # rate: rate of the tranche
        # subordination: is the tranche senior or subordinated? 'A' is senior, 'B' is subordinated

        # Instantiate the tranche
        tranche = trancheClass(self.totalNotional * percentNotional, rate, subordination)
        tranche.percentNotional = percentNotional
        # Append the tranche to the StructuredSecurities internal trancheList
        self.trancheList.append(tranche)

    # Method to increment the time period of the underlying tranches and the SS object itself
    def increaseTimePeriod(self):
        for tranche in self:
            tranche.increaseTimePeriod()
        # Also increment period to keep up with the tranches and to calculate the principalDue accurately
        self.period += 1

    # INTERNAL METHOD (only used by doWaterfallSequential) to loop through the tranches, in order of seniority, and make payments to the tranches
    def makePayments(self, cashAmount, sequential):
        '''
        :param cashAmount:  total collections of the ABS available for payout
        (loanPool total payments + recoveries + previous period cash reserve) at the current period
        :param sequential: boolean value specifying principal payout distribution. Passed in by the doWaterfallSequential(sequential) method
        :return: None
        '''

        ##### Interest payments

        for tranche in self:
            # Interest payment is the LESSER between the interest due and the available cashAmount
            # If balance is paid down to 0, interestDue is 0.
            # Or if all cash has already been paid to senior tranche interest payment, interest for subordinated is 0
            interestPayment = min(tranche.interestDue(), cashAmount)
            # Make the interestPayment
            tranche.makeInterestPayment(interestPayment)
            # Subtract it from available cash amount
            cashAmount -= interestPayment
            # Recording shortfall code is at the bottom of makeInterestPayment() method in Tranche class
            # Adding shortfall onto the next period interest due code is in the interestDue() method in Tranche class


        # BASELINE principalDue, aka principal due OF THE LOANPOOL for the SS object period
        principalDue = self.loanPool.totalPrincipalDue(self.period)


        ##### Principal payments, assuming there's money left after interest payments have been made
        # The residual Principal payments due to the tranches are based on the total principal received from the LOANPOOL...
        # ... NOT the total available cash
        for tranche in self:

            # Sequential payout: Senior tranche gets all the principal due if cashAmount allows.
            if sequential:
                # Each tranche's principal due must add the previous period shortfall
                principalDue += tranche.properties[tranche.period - 1]['Principal shortfall']

            # Pro-rata payout: principal payments are proportional to each tranche's percentNotional
            else:
                # Principal due for the TRANCHE = total principal due of the LOANPOOL * percentNotional + any previous shortfall
                principalDue = self.loanPool.totalPrincipalDue(self.period) * (tranche.notional / self.totalNotional)\
                               + tranche.properties[tranche.period - 1]['Principal shortfall']

            # Tranche principal payment = the minimum of principal due, available cashAmount, and balance for the PREVIOUS period
            principalPayment = min(principalDue, cashAmount, tranche.properties[tranche.period - 1]['Notional balance'])

            ##### Making payments, recording them, and reducing cash and principal due for each tranche

            # Record principal due in the tranche properties dictionary
            tranche.properties[tranche.period]['Principal due'] = principalDue

            # SPECIAL CASE: If the tranche is paid off, principalDue is equal to the principal payment
            if principalPayment == tranche.properties[tranche.period - 1]['Notional balance']:
                tranche.properties[tranche.period]['Principal due'] = principalPayment

            # Record the principal payment and the notional balance in the tranche properties dict
            tranche.makePrincipalPayment(principalPayment)

            # Record principal shortfall: max of 0 and difference between tranche due and tranche payment
            principalShortfall = max(0, tranche.properties[tranche.period]['Principal due'] - principalPayment)
            tranche.properties[tranche.period]['Principal shortfall'] = principalShortfall

            # Reduce cash amount by the principal payment
            cashAmount -= principalPayment

            # Record cash leftover after principal payments for each tranche
            tranche.properties[tranche.period]['Cash reserve'] = cashAmount

            # If a tranche has a principal shortfall, then the next tranches should not have any principal due for that period
            if principalShortfall > 1:
                principalDue = principalPayment

            # Reduce principal due by the principal payment
            principalDue -= principalPayment

    # Method to do waterfalls for the SS object for each period until the underlying loanPool runs out of active loans
    def doWaterfallSequential(self, sequential=True):
        '''

        :param sequential: User passed-in param to specify principal payout distribution
        :return: None
        '''

        self.period = 0

        # Evaluate to True until theres no active loan left
        while self.loanPool.activeLoans(self.period):

            # Increment period of self, and also all the tranches
            self.increaseTimePeriod()
            # Check the loanPool for any default in that period, store the total recovery value, and record it in the properties dict
            totalRecovery = self.loanPool.checkDefaultsReturnRecovery(self.period)
            # Total collections for the period = total payments due from the loanPool + total recovery from the defaulted loans + cash reserve stored in the last tranche properties
            totalCollections = self.loanPool.totalPaymentDue(self.period) + totalRecovery + self.trancheList[1].properties[self.period - 1]['Cash reserve']
            # Make the payments for the current period
            self.makePayments(totalCollections, sequential)
            # Record the payments on the Asset side using LoanPool's getWaterfall() method
            self.loanPool.getWaterfall(self.period)
            # Record the loanPool recoveries here
            self.loanPool.properties[self.period]['Recoveries'] = totalRecovery

        # Once the waterfall is done, initialize 2 tallies: 1 for RIY and 1 for AL so as to add them up in simulations
        for tranche in self:
            tranche.properties[tranche.period]['Total RIY'] = 0
            tranche.properties[tranche.period]['Total AL'] = 0


    def simulateWaterfallSequential(self, nSims, sequential=True):
        '''
        Method to run the waterfall multiple times
        structuredSecurity: the StructuredSecurities object, usually an ABS
        loanPool: the LoanPool object of the ABS
        nSims: number of simulations to run
        :return: a dictionary of each tranche's pairs-tuple (weighted RIY, weighted AL)
        '''

        # First we reset the ABS in case another waterfall has already been run on it
        self.reset()

        metricsDict = {}
        dictTuple = {}

        for tranche in self:
            metricsDict[f'{tranche.subordination}'] = {}
            metricsDict[f'{tranche.subordination}'][f'Total RIY'] = 0
            metricsDict[f'{tranche.subordination}'][f'Total AL'] = 0


        # doWaterfallSequential nSims times
        for nSim in range(nSims):
            self.doWaterfallSequential(sequential)

            # After the iteration is done, add it onto the metrics tally in the dictionary
            for tranche in self:
                
                # Add the iteration RIY to the metrics tally 
                metricsDict[f'{tranche.subordination}'][f'Total RIY'] += tranche.RIY()[0]

                # Only add the average life if the tranche is paid down
                if tranche.AL() is not None:
                    metricsDict[f'{tranche.subordination}'][f'Total AL'] += tranche.AL()

            # Reset the ABS and the tranches to doWaterfallSequential all over again
            self.reset()

            # In the last iteration, calculate the weighted metrics for each tranche and store it in the metrics dictionary
            if nSim == nSims - 1:
                for tranche in self:
                    metricsDict[f'{tranche.subordination}'][f'Weighted RIY'] = metricsDict[f'{tranche.subordination}'][f'Total RIY'] / nSims
                    metricsDict[f'{tranche.subordination}'][f'Weighted AL'] = metricsDict[f'{tranche.subordination}'][f'Total AL'] / nSims


        for tranche, metrics in metricsDict.items():
            # Update each tranche's pairs-tuple (weighted RIY, weighted AL) as a value to each tranche as key
            dictTuple[tranche] = (metrics['Weighted RIY'], metrics['Weighted AL'])

        return dictTuple