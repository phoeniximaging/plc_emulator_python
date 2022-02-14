import csv
import json
import time
import os

'''
This branch of the plc_emulator goes iterates through the boolean tags of the 'Robot 2 Load Program Parameters' timing diagram.
This begins with 'READY' high (1). 'READY' is dropped (0) and 'LOAD_PROGRAM' is set high (1), this is where mirroring data back would happen.
Then 'READY' is set back high (1) and 'LOAD_PROGRAM' is dropped low (0), representing that the correct part information has been passed to the
Keyence and we are now ready to trigger/scan.
'''

def csv_read():
    #csv file reader variable declaration
    #file = open('\\phoenix-101\homes\Howard.Roush\Drive\plc_dummy.csv') #Python doesn't like \\
    file = open('//phoenix-101/homes/Howard.Roush/Drive/plc_dummy.csv')
    csvreader = csv.reader(file)

    #creating two lists that will be combined in the dictionary 'plc_dict'
    header = []
    header = next(csvreader) # tag names
    values = []
    values = next(csvreader) # values

    #print(len(header))
    #print(values)

    plc_dict = {} # dictionary: key = tag name
    #setting relevant value for each tag
    for x in range(len(header)):
        plc_dict[header[x]] = int(values[x]) #populating dict, casting to int for simplicity

    #print(plc_dict)
    #print()
    #print(type(plc_dict['LOAD_PROGRAM']))
    return plc_dict
#END csv_read

# Writes back to .csv (plc) with current tag values
def csv_write(results):
    header = []
    values = []
    file = open('//phoenix-101/homes/Howard.Roush/Drive/plc_dummy.csv', 'w', newline='')
    csv_writer = csv.writer(file)

    for key in results:
        header.append(key)
        values.append(results[key])

    csv_writer.writerow(header)
    csv_writer.writerow(values)

#Reads in .csv (pretend PLC), sets 'START_PROGRAM' to 1, waits 30 seconds, sets to 0, waits 30 seconds, repeats forever
def main():
    x = 10 #seconds variable for artificial pause
    while(True):
        csv_results = csv_read()
        #print(csv_results)

        # Stage 1 : Load Program Parameters
        # READY = 1, other boolean flags = 0
        print('\nStage 1 : Load')
        csv_results['READY'] = 1
        print('Writing: \'READY\' : 1')
        csv_write(csv_results)
        print(f'Write Complete! Waiting {x} seconds...')
        time.sleep(x)

        # Stage 2 : Load
        # READY = 0, LOAD_PROGRAM = 1, mirror data
        print('\nStage 2: Load')
        csv_results['READY'] = 0
        csv_results['LOAD_PROGRAM'] = 1
        print('Writing \'READY\' : 0 ; \'LOAD_PROGRAM\' : 1')
        # This is where specific data would be mirrored back to a real PLC (part info, date/time)
        print('!Data Mirrored Here!')
        csv_write(csv_results)
        print(f'Write Complete! Waiting {x} seconds...')
        time.sleep(x)

        # Stage 3 : Load
        # READY = 1, LOAD_PROGRAM = 0, "mirroring data" complete
        print('\nStage 3 : Load')
        csv_results['READY'] = 1
        csv_results['LOAD_PROGRAM'] = 0
        print('Writing \'READY\' : 1 ; \'LOAD_PROGRAM\' : 0')
        csv_write(csv_results)
        print(f'Write Complete! Waiting {x} seconds...')
        time.sleep(x)
#END main

if __name__ == '__main__':
    main()