__author__ = 'IH'
__project__ = 'processMOOC'

import pandas as pd
import utilsMOOC as utils

'''
run function - coordinates the main statistical analyses
'''
def run():

    data = pd.io.parsers.read_csv(utils.FILENAME_USERLOG+utils.EXTENSION_PROCESSED, encoding="utf-8-sig")

    # make experimental conditions  categorical variables
    data[utils.COL_BADGE] = data[utils.COL_BADGE].astype('category')
    data[utils.COL_IRRELEVANT] = data[utils.COL_IRRELEVANT].astype('category')
    data[utils.COL_VOTING] = data[utils.COL_VOTING].astype('category')
    data[utils.COL_ANONIMG] = data[utils.COL_ANONIMG].astype('category')
    data[utils.COL_USERNAME] = data[utils.COL_USERNAME].astype('category')
    data[utils.COL_VERSION] = data[utils.COL_VERSION].astype('category')
    #print(data.tail())  # print a small sample of the data

    # Summary of Number of Helpers Selected
    print(utils.FORMAT_LINE)
    print("Descriptive statistics for: \'" + utils.COL_NUMHELPERS+"\'")
    print(data[utils.COL_NUMHELPERS].describe())
    print(utils.FORMAT_LINE)

    # Descriptive Stats of conditions
    print(utils.FORMAT_LINE)
    print("Descriptive statistics for: \'" + utils.COL_BADGE+"\'")
    print(data.groupby(utils.COL_BADGE)[utils.COL_BADGE].describe())
    print(utils.FORMAT_LINE)

'''
...So that statsMOOC can act as either a reusable module, or as a standalone program.
'''
if __name__ == '__main__':
    run()
