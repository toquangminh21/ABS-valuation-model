'''
1.1) Main program to test our StandardTranche class
'''

from package.Tranche import StandardTranche

def main():
    # Initialize a 100k totalNotional, 10% rate standard tranche
    tranche = StandardTranche(100000.0, 0.1)

    # Run 10 periods:
    for i in range(10):
        tranche.increaseTimePeriod()
        tranche.makePrincipalPayment(1000)
        tranche.makeInterestPayment(1000)

    # Print out the tranche dictionary
    print(tranche.properties)


if __name__ == '__main__':
    main()