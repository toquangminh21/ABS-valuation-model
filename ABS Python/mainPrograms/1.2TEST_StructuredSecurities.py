'''
1.2) Main program to test our StructuredSecurities class
USE THE SAME DATA as the Waterfall Example.csv file to see if the resulting numbers are identical with Mark's
'''

from package.StructuredSecuritiesABS import StructuredSecurities
from package.Tranche import StandardTranche
from package.LoanPool import Loan, LoanPool
from package.Auto import Lamborghini, FixedAutoLoan


def main():
    print('=== 1.2 Test) StructuredSecurities object')
    car = Lamborghini(90000, 0.05)
    ##### ASSET SIDE
    'Note: USE THE SAME DATA as the Waterfall Example.csv file to see if the resulting numbers are identical with Mark'
    # Instantiate 2 Loans and a loanPool and an ABS on that loanPool
    # 10-month, 8% annual rate, 100k face value loan
    loan1 = Loan(10, 0.08, 100000, car)
    # 8-month, 6% annual rate, 75k face value loan
    loan2 = Loan(8, 0.06, 75000, car)
    loanPool = LoanPool([loan1, loan2])
    security = StructuredSecurities(loanPool)

    # Toggle to pro-rata by passing in False for setSequential() method:
    security.setSequential(True)


    ##### LIABILITIES SIDE
    # Append a senior, 6% rate, and 80% notional StandardTranche A to the security
    security.addTranche(StandardTranche, 0.8, 0.06, 'A')
    # Append a subordinated, 8% rate, and 20% notional tranche B to the security
    security.addTranche(StandardTranche, 0.2, 0.08, 'B')

    # Print out the security's internal trancheList
    print('\n=== StructuredSecurities object internal tranche list: ')
    print(security.trancheList)

    # Do waterfall and print it out by Loans (Assets) and Tranches (Liabilities)
    security.doWaterfallSequential()

    print('\n=== ASSETS SIDE: Waterfall of the total loanPool and broken down by loans:')
    # LoanPool waterfall
    for period, waterfall in security.loanPool.properties.items():
        print(f'LoanPool: period {period}: {waterfall}')

    print('')

    # (DISABLED - too much memory with 1,500 loans) Individual Loans waterfall
    for loan in security.loanPool:
        for period, waterfall in loan.properties.items():
            print(f'{loan}: period {period}: {waterfall}')
        print('')

    print('\n=== LIABILITIES SIDE: Waterfall broken down by tranches:')
    for tranche in security.trancheList:
        for period, waterfall in tranche.properties.items():
            print(f'Tranche {tranche.subordination}: period {period}: {waterfall}')
        print('')

    print(f'ABS cash reserve leftover: {security.cashReserve}\n')

    for tranche in security.trancheList:
        print(f'Tranche {tranche.subordination}:')
        print(f'Annual IRR: {tranche.IRR()}')
        print(f'Annual RIY: {tranche.RIY()[0]}')
        print(f'Letter rating: {tranche.RIY()[1]}')
        print(f'Average life: {tranche.AL()}')
        print('')

if __name__ == '__main__':
    main()