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
    # TODO: Not sure this is necessary/desirable
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

    # Descriptive Statistics of conditions
    print(utils.FORMAT_LINE)
    print("Descriptive statistics for: all conditions")
    df_conditions = data[[utils.COL_BADGE, utils.COL_IRRELEVANT, utils.COL_VOTING, utils.COL_USERNAME, utils.COL_VERSION]]
    print(df_conditions.describe())

    # Count/Descriptive Stats of individual conditions & mean num helpers selected of each (2^5) conditions
    print(utils.FORMAT_LINE)
    print("Counts & Mean " + utils.COL_NUMHELPERS + " for: \'" + utils.COL_BADGE+"\'\n* should be even distribution")
    print(pd.concat([data.groupby(utils.COL_BADGE)[utils.COL_BADGE].count(), data.groupby(utils.COL_BADGE)[utils.COL_NUMHELPERS].mean()], axis=1))
    print(utils.FORMAT_LINE)
    print("Counts & Mean " + utils.COL_NUMHELPERS + " for: \'" + utils.COL_IRRELEVANT+"\'\n* should be even distribution")
    print(pd.concat([data.groupby(utils.COL_IRRELEVANT)[utils.COL_IRRELEVANT].count(), data.groupby(utils.COL_IRRELEVANT)[utils.COL_NUMHELPERS].mean()], axis=1))
    print(utils.FORMAT_LINE)
    print("Counts & Mean " + utils.COL_NUMHELPERS + " for: \'" + utils.COL_VOTING+"\'\n* should be even distribution")
    print(pd.concat([data.groupby(utils.COL_VOTING)[utils.COL_VOTING].count(), data.groupby(utils.COL_VOTING)[utils.COL_NUMHELPERS].mean()], axis=1))
    print(utils.FORMAT_LINE)
    print("Counts & Mean " + utils.COL_NUMHELPERS + " for: \'" + utils.COL_USERNAME+"\'\n* not even distribution due to "+utils.COL_VERSION)
    print(pd.concat([data.groupby(utils.COL_USERNAME)[utils.COL_USERNAME].count(), data.groupby(utils.COL_USERNAME)[utils.COL_NUMHELPERS].mean()], axis=1))
    print(utils.FORMAT_LINE)
    print("Counts & Mean " + utils.COL_NUMHELPERS + " for: \'" + utils.COL_VERSION+"\'")
    print(pd.concat([data.groupby(utils.COL_VERSION)[utils.COL_VERSION].count(), data.groupby(utils.COL_VERSION)[utils.COL_NUMHELPERS].mean()], axis=1))
    print(utils.FORMAT_LINE)

'''
...So that statsMOOC can act as either a reusable module, or as a standalone program.
'''
if __name__ == '__main__':
    run()
