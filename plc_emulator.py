import csv
import json
import time
import os


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
    x = 30 #seconds variable for artificial pause
    while(True):
        csv_results = csv_read()
        #print(csv_results)
        #set START_PROGRAM high then wait 30 seconds (triggering Keyence)
        csv_results['START_PROGRAM'] = 1
        print('Writing: \'START_PROGRAM\' : 1')
        csv_write(csv_results)
        print(f'Write Complete! Waiting {x} seconds...')
        time.sleep(x)

        #set START_PROGRAM low then wait 30 seconds
        csv_results['START_PROGRAM'] = 0
        print('Writing: \'START_PROGRAM\' : 0')
        csv_write(csv_results)
        print(f'Write Complete! Waiting {x} seconds...')
        time.sleep(x)


if __name__ == '__main__':
    main()