'''
Main program to test our StructuredSecurities class with a LoanPool of 1,500 loans
Write in the data from Loans.csv file
'''

from package.StructuredSecuritiesABS import StructuredSecurities
from package.Tranche import StandardTranche
from package.LoanPool import Loan, LoanPool
from package.Auto import Car
import time, numpy



def main():

    '''
    Part 1: run the default-free waterfall model on a 2-tranche ABS with an underlying loan pool of 1,500 loans
    '''

    print('=== WATERFALL')
    start = time.time()
    # Initialize a blank list to append 1,500 loans and later pass into the loanPool object
    loansList = []

    with open('Loans.csv', 'r') as file:

        # Skip the header row
        next(file)

        # Iterate over all rows/loans and split them by comma
        for row in file:

            # Store the values
            temp = row.split(',')
            asset = eval(f'{temp[5]}({(temp[6])})')
            # Parse necessary data and instantiate the loans
            loan = Loan(int(temp[4]), float(temp[3]), float(temp[2]), asset)
            # Append
            loansList.append(loan)
            if len(loansList) == 200:
                break

    print('Appending loans: done')

    # Pool into a LoanPool object
    loanPool = LoanPool(loansList)
    # Instantiate the ABS
    ABS = StructuredSecurities(loanPool) # Useful attributes: ABS.totalNotional, ABS.trancheList, ABS.cashReserve
    # Add a standard tranche: 80% notional, 15% rate, senior
    ABS.addTranche(StandardTranche, 0.8, 0.15, 'A')
    # Add a standard tranche: 20% notional, 20% rate, junior
    ABS.addTranche(StandardTranche, 0.2, 0.20, 'B')
    # Set payout mode to sequential
    ABS.setSequential(True)


    # Do waterfall (will take a while - 1,500 loans)
    ABS.doWaterfallSequential()

    print('ABS Waterfall: done')

    ##### Assets
    # Write the LoanPool Waterfall to the AssetWaterfall.csv file
    with open('12AssetWaterfall.csv', 'w') as file:
        # Write the header row
        file.write('Period,Principal,Interest,Total,Balance\n')
        # Loop through all the periods and write the LoanPool record into the csv file
        for period, waterfall in ABS.loanPool.properties.items():
            # period is key, waterfall is value. waterfall is the dictionary that holds the record for each period
            file.write('{0},{1},{2},{3},{4}\n'.format(period, waterfall['Principal'], waterfall['Interest'], waterfall['Total'], waterfall['Balance']))

    print('Writing asset waterfall to csv: done')

    ##### Liabilities
    # Write the Tranches Waterfall to the LiabilitiesWaterfall.csv file
    with open('12LiabilitiesWaterfall.csv', 'w') as file:
        # Write the header row
        file.write('Period,Collections,A Interest Due,A Interest Paid,A Interest Shortfall,B Interest Due,'
                   'B Interest Paid,B Interest Shortfall,A Prin Due,A Prin Paid,A Prin Shortfall,Cash Reserve,'
                   'B Prin Due,B Prin Paid,B Prin Shortfall,A Balance,B Balance,Cash Reserve\n')
        # Loop through the periods of the LoanPool and write the record for the tranches into the csv file
        for period in ABS.loanPool.properties:
            ### Hardcode: assuming our ABS will only have 2 tranches. Will not work with variable length trancheList.
            trancheA = ABS.trancheList[0].properties[period]
            trancheB = ABS.trancheList[1].properties[period]
            file.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17}\n'.format(
                period, ABS.loanPool.totalPaymentDue(period), trancheA['Interest due'],
                trancheA['Interest payment'],
                trancheA['Interest shortfall'], trancheB['Interest due'],
                trancheB['Interest payment'],
                trancheB['Interest shortfall'], trancheA['Principal due'],
                trancheA['Principal payment'],
                trancheA['Principal shortfall'], trancheA['Cash reserve'],
                trancheB['Principal due'],
                trancheB['Principal payment'], trancheB['Principal shortfall'],
                trancheA['Notional balance'],
                trancheB['Notional balance'], trancheB['Cash reserve']
            ))

    print('Writing liabilities waterfall to csv: done')

    end = time.time()
    print(f'Time taken for part 1: {end-start} seconds')

    '''
    Part 2: Metrics on the ABS: IRR, AL, DIRR
    '''
    print('\n=== Part 2: Metrics on the Tranches: IRR, AL, DIRR')

    for tranche in ABS.trancheList:
        print(f'Tranche {tranche.subordination}:')
        print(f'Annual IRR: {tranche.IRR()}')
        print(f'Annual RIY: {tranche.RIY()[0]}')
        print(f'Letter rating: {tranche.RIY()[1]}')
        print(f'Average life: {tranche.AL()}')
        print('')


if __name__ == '__main__':
    main()
