__author__ = 'IH'
__project__ = 'processMOOC'

import pandas as pd
import utilsMOOC as utils
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols
from statsmodels.graphics.api import interaction_plot, abline_plot
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.weightstats import ttest_ind

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

    user_input = input("> Print descriptive statistics? [y/n]: ")
    if is_yes(user_input):
        descriptive_stats(data)
    user_input = input(">> Display descriptive statistics plot? [y/n]: ")
    if is_yes(user_input):
        compare_plot_instances(data)

    user_input = input(">> Display descriptive plot of " + utils.COL_NUMHELPERS + "? [y/n]: ")
    if is_yes(user_input):
        descriptive_plot(data)

    user_input = input("> Display comparison plots of conditions -> "+utils.COL_NUMHELPERS+"? [y/n]: ")
    if is_yes(user_input):
        compare_plot_helpers(data)

    user_input = input("> Print t-test statistics for all conditions? [y/n]: ")
    if is_yes(user_input):
        t_test(data)

    user_input = input("> Print One-Way ANOVA statistics for all conditions? [y/n]: ")
    if is_yes(user_input):
        one_way_anova(data)

    user_input = input("> Print Two-Way ANOVA Interaction badge*voting statistics? [y/n]: ")
    if is_yes(user_input):
        anova_interaction(data)


def is_yes(stri):
    """
    Return True if the given string contains a 'y'
    :param str: a string, likely a user console input
    :return: True if the string contains the letter 'y'
    """
    return 'y' in stri.lower()

def t_test(data):
    """
    T-test to predict each condition --> num helpers selected
    http://statsmodels.sourceforge.net/devel/stats.html

    Note: T-tests are for 1 categorical variable with 2 levels
    :param data: data frame containing the independent and dependent variables
    :return: None
    """
    conditions = {utils.COL_BADGE, utils.COL_IRRELEVANT, utils.COL_VOTING, utils.COL_USERNAME, utils.COL_ANONIMG}
    # utils.COL_VERSION -> has 'TA' and 'student' instead of 'y' and 'n'

    fig = plt.figure()
    i = 1

    for cond in conditions:
        df = data[[cond, utils.COL_NUMHELPERS]].dropna()
        cat1 = df[df[cond] == utils.VAL_IS][utils.COL_NUMHELPERS]
        cat2 = df[df[cond] == utils.VAL_ISNOT][utils.COL_NUMHELPERS]

        print("\n"+utils.FORMAT_LINE)
        print("T-test: " + cond)
        print(utils.FORMAT_LINE)
        print(ttest_ind(cat1, cat2))  # returns t-stat, p-value, and degrees of freedom
        print("(t-stat, p-value, df)")

        ax = fig.add_subplot(2, 3, i)
        ax = df.boxplot(utils.COL_NUMHELPERS, cond, ax=plt.gca())
        ax.set_xlabel(cond)
        ax.set_ylabel(utils.COL_NUMHELPERS)
        i += 1
    # box plot
    user_input = input(">> Display boxplot of conditions? [y/n]: ")
    if is_yes(user_input):
        plt.show()

def one_way_anova(data):
    """
    One-way ANOVA to predict each condition --> num helpers selected
    http://statsmodels.sourceforge.net/devel/examples/generated/example_interactions.html

    Note: 1way ANOVAs are for 1 categorical independent/causal variable with 3+ levels
    :param data: data frame containing the independent and dependent variables
    :return: None
    """
    conditions = {utils.COL_BADGE, utils.COL_IRRELEVANT, utils.COL_VOTING, utils.COL_USERNAME, utils.COL_VERSION, utils.COL_ANONIMG}

    fig = plt.figure()
    i = 1

    for cond in conditions:
        cond_table = data[[cond, utils.COL_NUMHELPERS]].dropna()
        cond_lm = ols(utils.COL_NUMHELPERS + " ~ C(" + cond + ")", data=cond_table).fit()
        anova_table = anova_lm(cond_lm)

        print("\n"+utils.FORMAT_LINE)
        print("One-Way ANOVA: " + cond)
        print(utils.FORMAT_LINE)
        print(anova_table)
        #print(cond_lm.model.data.orig_exog)
        print(cond_lm.summary())

        ax = fig.add_subplot(2, 3, i)
        ax = cond_table.boxplot(utils.COL_NUMHELPERS, cond, ax=plt.gca())
        ax.set_xlabel(cond)
        ax.set_ylabel(utils.COL_NUMHELPERS)
        i += 1
    # box plot
    user_input = input(">> Display boxplot of conditions? [y/n]: ")
    if is_yes(user_input):
        plt.show()


def anova_interaction(data):
    """
    Two-way ANOVA and interaction analysis of badges*voting --> num helpers selected
    http://statsmodels.sourceforge.net/devel/examples/generated/example_interactions.html

    Note: 2way ANOVAs are for 2+ categorical independent/causal variables, with 2+ levels each
    :param data: data frame containing the independent and dependent variables
    :return: None
    """

    exp_data = data[[utils.COL_BADGE, utils.COL_VOTING, utils.COL_NUMHELPERS]]
    factor_groups = exp_data[[utils.COL_BADGE, utils.COL_VOTING, utils.COL_NUMHELPERS]].dropna()

    # two-way anova
    formula = utils.COL_NUMHELPERS + " ~ C(" + utils.COL_BADGE + ") + C(" + utils.COL_VOTING + ")"
    formula_interaction = formula.replace('+', '*')
    badge_vote_lm = ols(formula, data=factor_groups).fit()  # linear model
    print(badge_vote_lm.summary())

    print(utils.FORMAT_LINE)
    print("- " + utils.COL_NUMHELPERS + " = " + utils.COL_BADGE + " * " + utils.COL_VOTING + " Interaction -")
    print(anova_lm(ols(formula_interaction, data=factor_groups).fit(), badge_vote_lm))

    print(utils.FORMAT_LINE)
    print("- " + utils.COL_NUMHELPERS + " = " + utils.COL_BADGE + " + " + utils.COL_VOTING + " ANOVA -")
    print(anova_lm(ols(utils.COL_NUMHELPERS + " ~ C(" + utils.COL_BADGE + ")", data=factor_groups).fit(), ols(utils.COL_NUMHELPERS +" ~ C("+utils.COL_BADGE+") + C(" + utils.COL_VOTING+", Sum)", data=factor_groups).fit()))

    print(utils.FORMAT_LINE)
    print("- " + utils.COL_NUMHELPERS + " = " +  utils.COL_BADGE + " + " + utils.COL_VOTING + " ANOVA -")
    print(anova_lm(ols(utils.COL_NUMHELPERS + " ~ C(" + utils.COL_VOTING + ")", data=factor_groups).fit(), ols(utils.COL_NUMHELPERS +" ~ C("+utils.COL_BADGE+") + C(" + utils.COL_VOTING+", Sum)", data=factor_groups).fit()))

    # interaction plot
    user_input = input(">> Display Interaction plot? [y/n]: ")
    if is_yes(user_input):
        plt.figure(figsize=(6, 6))
        interaction_plot(factor_groups[utils.COL_BADGE], factor_groups[utils.COL_VOTING], factor_groups[utils.COL_NUMHELPERS], colors=['red', 'blue'], markers=['D', '^'], ms=10, ax=plt.gca())
        plt.show()

def compare_plot_helpers(data):
    """
    Print comparison plots for given data frame
    :param data: pandas dataframe we are exploring
    :return: None
    """
    # TODO: These should be box plots, not bar plots
    conditions = {utils.COL_BADGE, utils.COL_IRRELEVANT, utils.COL_VOTING, utils.COL_USERNAME, utils.COL_VERSION, utils.COL_ANONIMG}
    fig = plt.figure()
    i = 1
    for cond in conditions:
        ax = fig.add_subplot(2, 3, i)
        #df_compare = pd.concat([data.groupby(cond)[cond].count(), data.groupby(cond)[utils.COL_NUMHELPERS].mean()], axis=1) # displays num helpers selected in each condition
        df_compare = data.groupby(cond)[utils.COL_NUMHELPERS].mean()  # displays num helpers selected in each condition
        ax = df_compare.plot(kind='bar', title=cond)
        ax.set_xlabel(cond)
        ax.set_ylabel("mean " + utils.COL_NUMHELPERS)
        i += 1
    plt.show()

def compare_plot_instances(data):
    """
    Print comparison plots for given data frame, show num instances in each condition
    :param data: pandas dataframe we are exploring
    :return: None
    """
    conditions = {utils.COL_BADGE, utils.COL_IRRELEVANT, utils.COL_VOTING, utils.COL_USERNAME, utils.COL_VERSION, utils.COL_ANONIMG}
    fig = plt.figure()
    i = 1
    for cond in conditions:
        ax = fig.add_subplot(2, 3, i)
        df_compare = data.groupby(cond)[cond].count()  # displays num instances assigned to each condition
        ax = df_compare.plot(kind='bar', title=cond)
        ax.set_xlabel(cond)
        ax.set_ylabel("count instances")
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
    helpers_by_date = data[utils.COL_NUMHELPERS]
    helpers_by_date.index = data[utils.COL_DATE]
    helpers_by_date = helpers_by_date.cumsum()
    ax1 = helpers_by_date.plot(title="Num Helpers Selected Over Time")
    ax1.locator_params(axis='x', nbins=6)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Cumulative Helpers Selected")

    ax2 = fig.add_subplot(122)
    helpers_hist = data[utils.COL_NUMHELPERS]
    ax2 = helpers_hist.plot(kind='hist', title="Histogram Num Helpers Selected", by=utils.COL_NUMHELPERS)
    ax2.locator_params(axis='x', nbins=4)
    ax2.set_xlabel("Number of Helpers Selected (0,1,2,3)")
    ax2.set_ylabel("Num Instances")
    plt.show()

def descriptive_stats(data):
    """
    Print descriptive statistics for give data frame

    # Note: Descriptive stats help check independent/causal vars (that are categorical) for even assignment/distribution
    # Note: For scalar indepenent variables, you check for normal distribution (easy way: distribution plots)
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
