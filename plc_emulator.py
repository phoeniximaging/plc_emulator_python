import csv
import json
import time
import os
import datetime

'''
This branch of the plc_emulator goes iterates through the boolean tags of the 'Robot 2 Load Program Parameters' timing diagram.
This begins with 'READY' high (1). 'READY' is dropped (0) and 'LOAD_PROGRAM' is set high (1), this is where mirroring data back would happen.
Then 'READY' is set back high (1) and 'LOAD_PROGRAM' is dropped low (0), representing that the correct part information has been passed to the
Keyence and we are now ready to trigger/scan.
'''

class StopWatch:
    def __init__(self):
        self.trigger_start_time = datetime.datetime.now()
    def start(self):
        self.trigger_start_time = datetime.datetime.now()
    def stop(self):
        self.trigger_end_time = datetime.datetime.now()
    def elapsed(self):
        self.stop()
        self.time_diff = (self.trigger_end_time - self.trigger_start_time)
        self.execution_time = self.time_diff.total_seconds() * 1000
        return self.execution_time

stop_watch = StopWatch() # global stopwatch var
current_stage = 0 # global var to track which "stage" of the timing chart we're currently in

def csv_read(io):
    #csv file reader variable declaration
    #file = open('\\phoenix-101\homes\Howard.Roush\Drive\plc_dummy.csv') #Python doesn't like \\
    #file = open('//phoenix-101/homes/Howard.Roush/Drive/plc_dummy.csv')
    if io == 'i':
        file = open('//phoenix-101/homes/Howard.Roush/Drive/phoenix_to_plc.csv')
    if io == 'o':
        file = open('//phoenix-101/homes/Howard.Roush/Drive/plc_to_phoenix.csv')
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
    #file = open('//phoenix-101/homes/Howard.Roush/Drive/plc_dummy.csv', 'w', newline='')
    file = open('//phoenix-101/homes/Howard.Roush/Drive/plc_to_phoenix.csv', 'w', newline='')
    csv_writer = csv.writer(file)

    for key in results:
        header.append(key)
        values.append(results[key])

    csv_writer.writerow(header)
    csv_writer.writerow(values)

#Reads in .csv (pretend PLC), sets 'START_PROGRAM' to 1, waits 30 seconds, sets to 0, waits 30 seconds, repeats forever
def main():
    global stop_watch
    global current_stage
    #stop_watch = StopWatch()
    #stop_watch.start()
    #print(stop_watch.trigger_start_time)
    #time.sleep(1)
    #stop_watch.stop()
    #print(stop_watch.elapsed())
    #time.sleep(10)

    x = 3 #seconds variable for artificial pause
    while(True):
        print(f'CURRENT STAGE : {current_stage}')
        #global 'current_stage' tracks which stage of the timing process

        # READING BOTH .CSV FILES
        csv_results = csv_read('i') #holds PHOENIX tags / data
        csv_results_plc = csv_read('o') #holds PLC (Grob) tags / data

        if(current_stage == 0):
            #csv_results = csv_read('i') #holds PHOENIX tags / data
            #csv_results_plc = csv_read('o') #holds PLC (Grob) tags / data

            #print('Waiting for Phoenix(READY) = 1...')
            time.sleep(1)

            # Stage 0 : Load Program Parameters
            # If Phoenix(READY) is high, send PLC(LOAD_PROGRAM) high to begin sequence
            if(csv_results['READY'] == 1 and csv_results_plc['LOAD_PROGRAM'] == 0):
                print('\nStage 0 : Load (High)')
                csv_results_plc['LOAD_PROGRAM'] = 1
                print('Writing: \'LOAD_PROGRAM\' : 1')
                csv_write(csv_results_plc)
                print(f'Write Complete! Waiting {x} seconds...')
                time.sleep(x)
                #LOAD PROGRAM SET HIGH AFTER PHOENIX(READY) = 1
            
            #print('!Data Mirrored Here!')
            #TODO on Phoenix Side
            if(csv_results['READY'] == 1 and csv_results_plc['LOAD_PROGRAM'] == 1):
                print('Checking for Mirrored Data...')
                if csv_results['DATA'] == csv_results_plc['DATA']:
                    print('Data Matches (PLC and Phoenix)')
                    #Mirroring complete, Phoenix(READY) goes high then PLC(LOAD_PROGRAM) goes low

                    print('\nStage 0 : Load (Low)')
                    csv_results_plc['LOAD_PROGRAM'] = 0
                    print('Writing: \'LOAD_PROGRAM\' : 0')
                    print(f'Stage({current_stage}) Complete!')
                    csv_write(csv_results_plc)
                    #print(f'Write Complete! Waiting {x} seconds...')
                    time.sleep(x)
                    current_stage += 1 #incrementing to next stage (START/END Program)
        #END STAGE 0
        #START STAGE 1 : START/END Program
        elif (current_stage == 1):
            print('Stage 1 : Writing PLC(START_PROGRAM) = 1')
            #Stage 1 : Step 1 : Set PLC(START_PROGRAM) = 1
            csv_results_plc['START_PROGRAM'] = 1
            csv_write(csv_results_plc)
            current_stage += 1
            time.sleep(1)

        elif(current_stage == 2):
            print('Stage 2 : Checking if PHOENIX(DONE) so we can reset to Stage 0')
            if(csv_results['DONE'] == 1):
                print('PHOENIX(DONE) = 1')
                csv_results_plc['START_PROGRAM'] = 0 #PLC(START_PROGRAM) goes LOW after PHOENIX(DONE) goes HIGH; scan is over and results are ready
                csv_results_plc['END_PROGRAM'] = 1 #Last event flag from PLC side, signifying to PHOENIX that we're ready to start STAGE 0 again
                csv_write(csv_results_plc)
                current_stage += 1
            time.sleep(1)

        elif(current_stage == 3):
            print('Stage 3 : Resetting all flags to Stage 0 status')
            time.sleep(1)
            if(csv_results['DONE'] == 0):
                print('PHOENIX(DONE) = 0\nResetting Flags to Stage 0 State!')
                csv_results_plc['END_PROGRAM'] = 0
                csv_write(csv_results_plc)
                current_stage = 0


#END main

if __name__ == '__main__':
    main()