#!/usr/bin/env python

__author__ = 'IH'
__project__ = 'processMOOC'

import datetime
import logfileMOOC
#import statsMOOC

# LOGFILE NAMES
FILENAME_HELPERLOG = "helper"
FILENAME_SELECTIONLOG = "selection"
FILENAME_VOTELOG = "vote"
FILENAME_USERLOG = "user"
EXTENSION_LOGFILE = ".log"
EXTENSION_PROCESSED = ".csv"

# TEXT-RELATED VARIABLES
CONST_DELIMITER = ","

# limiting date
CONST_FIRST_DAY = datetime.date(2014, 10, 20)
CONST_LAST_DAY = datetime.date(2014, 12, 17)

# TODO: command line input for column delimiters, dates, filenames, etc.

'''
main function - calls the functions that do the processing for each kind of file
'''
def main():
    logfileMOOC.run()  # process our log files
    #statsMOOC.run()

'''
So that processMOOC can act as either a reusable module, or as a standalone program.
'''
if __name__ == '__main__':
    main()
