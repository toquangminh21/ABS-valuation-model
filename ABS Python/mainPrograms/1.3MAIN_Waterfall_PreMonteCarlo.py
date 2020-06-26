'''
Main program to test our StructuredSecurities class with a random component added to the default model
'''

from package.StructuredSecuritiesABS import StructuredSecurities
from package.Tranche import StandardTranche
from package.LoanPool import Loan, LoanPool
from package.Auto import Car
import time, numpy



def main():

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
    # Add a standard tranche: 80% notional, 5% rate, senior
    ABS.addTranche(StandardTranche, 0.8, 0.05, 'A')
    # Add a standard tranche: 20% notional, 8% rate, junior
    ABS.addTranche(StandardTranche, 0.2, 0.08, 'B')


    # Do waterfall (will take a while - 1,500 loans)
    ABS.doWaterfallSequential()

    print('ABS Waterfall: done')

    ##### Assets
    # Write the LoanPool Waterfall to the AssetWaterfall.csv file
    with open('13AssetWaterfall.csv', 'w') as file:

        # Write the header row
        file.write('Period,Principal,Interest,Total,Balance\n')

        # Loop through all the periods and write the LoanPool record into the csv file
        for period, waterfall in ABS.loanPool.properties.items():

            # period is key, waterfall is value. waterfall is the dictionary that holds the record for each period
            file.write('{0},{1},{2},{3},{4}\n'.format(period, waterfall['Principal'], waterfall['Interest'], waterfall['Total'], waterfall['Balance']))


    print('Writing asset waterfall to csv: done')


    ##### Liabilities
    # Write the Tranches Waterfall to the LiabilitiesWaterfall.csv file
    with open('13LiabilitiesWaterfall.csv', 'w') as file:

        # Write the header row
        file.write('Period,Recoveries,TotalCollections(+ Reco + Reserve),A Interest Due,A Interest Paid,A Interest Shortfall,B Interest Due,'
                   'B Interest Paid,B Interest Shortfall,A Prin Due,A Prin Paid,A Prin Shortfall,Cash Reserve,'
                   'B Prin Due,B Prin Paid,B Prin Shortfall,A Balance,B Balance,Cash Reserve\n')

        # Loop through the periods of the LoanPool and write the record for the tranches into the csv file
        for period in ABS.loanPool.properties:

            ### Hardcode: assuming our ABS will only have 2 tranches. Will not work with variable length trancheList.
            trancheA = ABS.trancheList[0].properties[period]
            trancheB = ABS.trancheList[1].properties[period]

            file.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18}\n'.format(
                period, ABS.loanPool.properties[period]['Recoveries'],
                ABS.loanPool.properties[period]['Total'] + ABS.loanPool.properties[period]['Recoveries'] + ABS.trancheList[1].properties[period - 1]['Cash reserve'],
                trancheA['Interest due'], trancheA['Interest payment'],
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
        print(f'Annual RIY (bps): {tranche.RIY()[0]}')
        print(f'Letter rating: {tranche.RIY()[1]}')
        print(f'Average life: {tranche.AL()}')
        print('')

    '''
    Part 3: Simulations with default scenarios and calculating weighted metrics
    '''
    print('\n=== Part 3: Weighted metrics: 5 simulations')
    start = time.time()
    nSims = int(5)
    monteTolerance = 0.01

    # simulateWaterfallSequential will run doWaterfallSequential nSims times, and output the weighted RIY and weighted AL of each tranche
    # :return: a dictionary of lists with key = tranche, value = pairs-list [weighted RIY, weighted AL]
    weightedMetricsDict = ABS.simulateWaterfallSequential(nSims)

    for tranche, metrics in weightedMetricsDict.items():
        print(f'{tranche} (Weighted RIY, Weighted AL): {metrics}')


    # monteDict will store a dictionary with key = tranche, value = 3-items-tuples (weighted RIY, weighted AL, fair rate)
    monteDict = ABS.runMonteSequential(nSims, monteTolerance)
    for tranche, metrics in monteDict.items():
        print(f'{tranche} (Weighted RIY, Weighted AL, Fair rate): {metrics}')
        # Letter grade rating in Tranche class under RIY() method


    end = time.time()
    print(f'Time taken for {nSims} simulations: {end - start} seconds')


    '''
    Part 4: Simulations with multiprocessing
    '''
    print('\n=== Part 4: Simulations with multiprocessing: 5 simulations with 5 sub-processes'
    inputQ = mp.Queue()
    outputQ = mp.Queue()
    nProcesses = 5
    start = time.time()

    # 5 simulations total
    for i in range(5):
        inputQ.put((ABS.runMonteSequential, (nSims/nProcesses, monteTolerance) ))

    processes = [mp.Process(target=doWork, args=(inputQ, outputQ) ) for i in range(nProcesses)]

    for process in processes:
        process.start()

    # join() to ensure main will not proceed until all sub-processes are done
    for process in processes:
        process.join()


    result = {}
    # [Weighted RIY, Weighted AL, Fair rate]
    result['A'] = [0, 0, 0]
    result['B'] = [0, 0, 0]

    while True:
        try:
            r = outputQ.get(timeout=1)
            for tranche, metricsTuple in r.items():
                # Aggregate resulting tranche metrics and average them
                result[tranche.subordination][0] += (r[tranche][0]) / nSims
                result[tranche.subordination][1] += (r[tranche][1]) / nSims
                result[tranche.subordination][2] += (r[tranche][2]) / nSims
        except Empty:
            break

    print(f'Results: {result}')

    end = time.time()

    print(f'{nSims} simulations with {nProcesses} processes time taken: {end - start} seconds')

def doWork(inputQ, outputQ):
    while True:
        try:
            function, args = inputQ.get(timeout=1)
            result = function(*args)
            # Put a dictionary with key = tranche, value = 3-items-tuples (weighted RIY, weighted AL, fair rate)
            outputQ.put(result)
        except:
            print('A doWork sub-process has finished')
            break

if __name__ == '__main__':
    main()
