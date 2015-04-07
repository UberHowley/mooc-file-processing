__author__ = 'IH'
__project__ = 'processMOOC'

import pandas as pd
import utilsMOOC as utils
import matplotlib.pyplot as plt

def run():
    """
    run function - coordinates the main statistical analyses
    :return: None
    """

    # Exception handling in case the logfile doesn't exist
    try:
        data = pd.io.parsers.read_csv(utils.FILENAME_USERLOG+utils.EXTENSION_PROCESSED, encoding="utf-8-sig")
    except OSError as e:
        print("ERROR: " +str(utils.FILENAME_USERLOG+utils.EXTENSION_PROCESSED) +" does not exist. Did you run logfileMOOC.py?")

    # make experimental conditions  categorical variables
    # TODO: Determine if this is necessary/desirable
    data[utils.COL_BADGE] = data[utils.COL_BADGE].astype('category')
    data[utils.COL_IRRELEVANT] = data[utils.COL_IRRELEVANT].astype('category')
    data[utils.COL_VOTING] = data[utils.COL_VOTING].astype('category')
    data[utils.COL_ANONIMG] = data[utils.COL_ANONIMG].astype('category')
    data[utils.COL_USERNAME] = data[utils.COL_USERNAME].astype('category')
    data[utils.COL_VERSION] = data[utils.COL_VERSION].astype('category')
    #print(data.tail())  # print a small sample of the data

    user_input = input("> Print descriptive statistics? [y/n]: ")
    if is_yes(user_input):
        descriptive_stats(data)

    user_input = input("> Display descriptive plot of " + utils.COL_NUMHELPERS + "? [y/n]: ")
    if is_yes(user_input):
        descriptive_plot(data)

    user_input = input("> Display comparison plots of conditions? [y/n]: ")
    if is_yes(user_input):
        compare_plot(data)


def is_yes(stri):
    """
    Return True if the given string contains a 'y'
    :param str: a string, likely a user console input
    :return: True if the string contains the letter 'y'
    """
    return 'y' in stri.lower()

def compare_plot(data):
    """
    Print comparison plots for give data frame
    :param data: pandas dataframe we are exploring
    :return: None
    """
    # TODO: These should be box plots, not bar plots
    conditions = {utils.COL_BADGE, utils.COL_IRRELEVANT, utils.COL_VOTING, utils.COL_USERNAME, utils.COL_VERSION, utils.COL_ANONIMG}
    fig = plt.figure()
    i = 1
    for cond in conditions:
        ax = fig.add_subplot(2, 3, i)
        df_compare = data.groupby(cond)[cond].count()
        print(df_compare)
        ax = df_compare.plot(kind='bar', title=cond)
        ax.set_xlabel(cond)
        ax.set_ylabel(utils.COL_NUMHELPERS)
        i += 1
    plt.show()

def descriptive_plot(data):
    """
    Print descriptive plot for give data frame
    :param data: pandas dataframe we are exploring
    :return: None
    """
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    plt_numhelpers = data[utils.COL_NUMHELPERS]
    plt_numhelpers.index = data[utils.COL_DATE]
    plt_numhelpers = plt_numhelpers.cumsum()
    ax1 = plt_numhelpers.plot(title="Num Helpers Selected Over Time")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Cumulative Helpers Selected")

    ax2 = fig.add_subplot(122)
    plt_numhelpers_hist = data[utils.COL_NUMHELPERS]
    ax2 = plt_numhelpers.plot(kind='hist', title="Histogram Num Helpers Selected")
    ax2.set_xlabel("Number of Helpers Selected (0,1,2,3)")
    ax2.set_ylabel("Count")
    plt.show()

def descriptive_stats(data):
    """
    Print descriptive statistics for give data frame
    :param data: pandas dataframe we are exploring
    :return: None
    """
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

    # Count/Descriptive Stats of individual conditions & mean num helps of each (2^5) conditions
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
