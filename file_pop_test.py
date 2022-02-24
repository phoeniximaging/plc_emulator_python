import csv
import time

while(True):
    file = open('//phoenix-101/homes/Howard.Roush/Drive/phoenix_to_plc.csv')
    csvreader = csv.reader(file)
    #creating two lists that will be combined in the dictionary 'plc_dict'
    try:
        header = []
        header = next(csvreader) # tag names
        print(header)
        time.sleep(1)
    except Exception as e:
        print(f'EXCEPTION : {e}')
