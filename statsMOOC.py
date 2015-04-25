__author__ = 'IH'
__project__ = 'processMOOC'

import pandas as pd
import utilsMOOC as utils
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
from statsmodels.formula.api import ols
from statsmodels.graphics.api import interaction_plot
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.weightstats import ttest_ind

VAL_IS = utils.VAL_IS
VAL_ISNOT = utils.VAL_ISNOT
FORMAT_LINE = utils.FORMAT_LINE

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
    try:
        helper_data = pd.io.parsers.read_csv(utils.FILENAME_HELPERLOG+utils.EXTENSION_PROCESSED, encoding="utf-8-sig")
    except OSError as e:
        print("ERROR: " +str(utils.FILENAME_HELPERLOG+utils.EXTENSION_PROCESSED) +" does not exist. Did you run logfileMOOC.py?")

    conditions = [utils.COL_BADGE, utils.COL_IRRELEVANT, utils.COL_VOTING, utils.COL_USERNAME, utils.COL_ANONIMG]  # all our categorical IVs
    # TODO: decide if 'conditions' should include version or not

    orig_data = helper_data[[utils.COL_NUMSTARS+utils.COL_SHOWN, utils.COL_WASSELECTED]].dropna()
    converted = orig_data[[utils.COL_NUMSTARS+utils.COL_SHOWN]].apply(lambda f: convert_badge_stars(f), axis=1)
    print(converted.tail())
    chi_square(converted)

    user_input = input("> Print descriptive statistics? [y/n]: ")
    if is_yes(user_input):
        descriptive_stats(data[conditions+[utils.COL_VERSION, utils.COL_NUMHELPERS]].dropna())
    user_input = input(">> Display descriptive statistics plot? [y/n]: ")
    if is_yes(user_input):
        compare_plot_instances(data[conditions+[utils.COL_VERSION]])

    user_input = input(">> Display descriptive plot of " + utils.COL_NUMHELPERS + "? [y/n]: ")
    if is_yes(user_input):
        descriptive_plot(data[[utils.COL_DATE, utils.COL_NUMHELPERS]])

    user_input = input("> Display comparison plots of conditions -> "+utils.COL_NUMHELPERS+"? [y/n]: ")
    if is_yes(user_input):
        compare_plot_helpers(data[conditions+[utils.COL_VERSION, utils.COL_NUMHELPERS]].dropna())

    user_input = input("> Print t-test statistics for all conditions? [y/n]: ")
    if is_yes(user_input):
        t_test(data[conditions+[utils.COL_VERSION, utils.COL_NUMHELPERS]].dropna())

    user_input = input("> Print One-Way ANOVA statistics for all conditions? [y/n]: ")
    if is_yes(user_input):
        one_way_anova(data[conditions+[utils.COL_VERSION, utils.COL_NUMHELPERS]].dropna())

    user_input = input("> Print Two-Way ANOVA Interaction badge*voting statistics? [y/n]: ")
    if is_yes(user_input):
        exp_data = data[[utils.COL_BADGE, utils.COL_VOTING, utils.COL_NUMHELPERS]]
        anova_interaction(exp_data)
        user_input = input(">> Display Interaction plot? [y/n]: ")
        if is_yes(user_input):
            plot_interaction(exp_data)

    user_input = input("> Do linear regression analyses? [y/n]: ")
    if is_yes(user_input):
        print("WARNING: Don't have any numerical causal --> numerical outcome predictions yet!")
        #linear_regression(helper_data[[utils.COL_NUMSTARS+utils.COL_SHOWN, utils.COL_WASSELECTED]].dropna())

    user_input = input("> Do chi-square analyses? [y/n]: ")
    if is_yes(user_input):
        print("WARNING: Don't have any categorical causal --> categorical outcome predictions yet!")
        #chi_square()

    user_input = input("> Do analysis of message post topics? [y/n]: ")
    if is_yes(user_input):
        try:
            topic_data = data[[utils.COL_TOPIC]+conditions+[utils.COL_VERSION, utils.COL_NUMHELPERS]].dropna()
        except KeyError:
            print("ERROR in statsMOOC.py: No such column as " + utils.COL_TOPIC + ". Did you run logfileMOOC.py?")
        one_stats(topic_data)

    user_input = input("> Do analysis of help requests? [y/n]: ")
    if is_yes(user_input):
        try:
            help_data = data[[utils.COL_HELP_TOPIC]+conditions+[utils.COL_VERSION, utils.COL_NUMHELPERS]].dropna()
        except KeyError:
            print("ERROR in statsMOOC.py: No such column as " + utils.COL_HELP_TOPIC + ". Did you run logfileMOOC.py?")
        one_stats(help_data)


def is_yes(stri):
    """
    Return True if the given string contains a 'y'
    :param str: a string, likely a user console input
    :return: True if the string contains the letter 'y'
    """
    return 'y' in stri.lower()

def convert_badge_stars(star):
    """
    Convert the given badge star from a number to a category
    :param star: the number of stars
    :return: a categorical representation of the number of stars
    """
    dict = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four"}
    return dict[star]

def linear_regression(data_lastDV):
    """
    Compute slope, intercept of best fit line...and plot, if desired
    http://stackoverflow.com/questions/19379295/linear-regression-with-pandas-dataframe
    Note: linear regression is for a numerical causal variable predicting a numerical outcome variable
    :param data_lastDV: dataframe where outcome variable is last, all other columns should be numerical
    """
    data_lastDV = data_lastDV.dropna()
    col_names = data_lastDV.columns.values.tolist()  # get the columns' names
    outcome = col_names.pop()  # remove the last item in the list

    fig = plt.figure()
    i = 1
    rows = 2  # TODO: determine how best to distribute plots based on num analyses
    for cond in col_names:
        x = data_lastDV[[cond]].values
        y = data_lastDV[[outcome]].values

        '''
        X = sm.add_constant(x)
        model = sm.OLS(y, X, missing='drop')  # ignores entries where x or y is NaN
        fit = model.fit()
        m = fit.params[1]
        b = fit.params[0]
        # could also retrieve stderr in each via fit.bse
        '''

        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        print(FORMAT_LINE)
        print("Linear regression: " + cond + " --> " + outcome)
        print("[slope, intercept, r_value, p_value, std_err]: " + str(stats.linregress(x,y)))
        print("r-squared:", r_value**2)
        print(FORMAT_LINE)

        # plotting
        N = 100  # could be just 2 if you are only drawing a straight line...
        points = np.linspace(x.min(), x.max(), N)
        ax = fig.add_subplot(rows, len(col_names)/rows, i)
        ax = plt.plot(points, slope*points + intercept)

        i+= 1

    user_input = input(">> Display linear regression plot? [y/n]: ")
    if is_yes(user_input):
        fig.tight_layout()
        plt.show()

def chi_square(data_lastDV):
    """
    Compute frequencies and do a Chi-Squared test.
    http://nbviewer.ipython.org/github/dboyliao/cookbook-code/blob/master/notebooks/chapter07_stats/04_correlation.ipynb
    Note: chi-square tests are for when the outcome variable is categorical
    :param data_lastDV: dataframe where outcome variable is last, all other columns should be numerical
    """
    data_lastDV = data_lastDV.dropna()
    col_names = data_lastDV.columns.values.tolist()  # get the columns' names
    outcome = col_names.pop()  # remove the last item in the list

    for cond in col_names:
        x = data_lastDV[[cond]].values
        y = data_lastDV[[outcome]].values

        # create a contingency table, with the frequencies of all possibilities
        cont_table = pd.crosstab(y, x)
        # compute the chi-square test statistic and the associated p-value.
        stats.chi2_contingency(cont_table.values)

def t_test(data_lastDV):
    """
    T-test to predict each condition --> num helpers selected
    Last column is the outcome variable (DV)
    http://statsmodels.sourceforge.net/devel/stats.html

    Note: T-tests are for 1 categorical variable with 2 levels
    :param data: data frame containing the independent and dependent variables
    :return: None
    """

    col_names = data_lastDV.columns.values.tolist()  # get the columns' names
    outcome = col_names.pop()  # remove the last item in the list

    fig = plt.figure()
    i = 1

    for cond in col_names:
        df = data_lastDV[[cond, outcome]].dropna()
        cat1 = df[df[cond] == VAL_IS][outcome]
        cat2 = df[df[cond] == VAL_ISNOT][outcome]

        print("\n"+FORMAT_LINE)
        print("T-test: " + cond)
        print(FORMAT_LINE)
        print(ttest_ind(cat1, cat2))  # returns t-stat, p-value, and degrees of freedom
        print("(t-stat, p-value, df)")

        ax = fig.add_subplot(2, 3, i)
        ax = df.boxplot(outcome, cond, ax=plt.gca())
        ax.set_xlabel(cond)
        ax.set_ylabel(outcome)
        i += 1
    # box plot
    user_input = input(">> Display boxplot of conditions? [y/n]: ")
    if is_yes(user_input):
        fig.tight_layout()
        plt.show()

def one_way_anova(data_lastDV):
    """
    One-way ANOVA to predict each condition --> num helpers selected
    http://statsmodels.sourceforge.net/devel/examples/generated/example_interactions.html

    Note: 1way ANOVAs are for 1 categorical independent/causal variable with 3+ levels
    :param data: data frame containing the independent and dependent variables (DV is last item in list)
    :return: None
    """
    col_names = data_lastDV.columns.values.tolist()  # get the columns' names
    outcome = col_names.pop()  # remove the last item in the list

    fig = plt.figure()
    i = 1

    for cond in col_names:
        cond_table = data_lastDV[[cond, outcome]].dropna()
        cond_lm = ols(outcome + " ~ C(" + cond + ")", data=cond_table).fit()
        anova_table = anova_lm(cond_lm)

        print("\n"+FORMAT_LINE)
        print("One-Way ANOVA: " + cond)
        print(FORMAT_LINE)
        print(anova_table)
        #print(cond_lm.model.data.orig_exog)
        print(cond_lm.summary())

        ax = fig.add_subplot(2, 3, i)
        ax = cond_table.boxplot(outcome, cond, ax=plt.gca())
        ax.set_xlabel(cond)
        ax.set_ylabel(outcome)
        i += 1
    # box plot
    user_input = input(">> Display boxplot of conditions? [y/n]: ")
    if is_yes(user_input):
        fig.tight_layout()
        plt.show()

def anova_interaction(data_lastDV):
    """
    Two-way ANOVA and interaction analysis of given data
    http://statsmodels.sourceforge.net/devel/examples/generated/example_interactions.html

    Note: 2way ANOVAs are for 2+ categorical independent/causal variables, with 2+ levels each
    :param data: data frame containing the independent variables in first two columns, dependent in the third
    :return: None
    """

    col_names = data_lastDV.columns.values  # get the columns' names
    factor_groups = data_lastDV[col_names].dropna()
    if len(col_names) < 3:
        print("ERROR in statsMOOC.py: Not enough columns in dataframe to do interaction analysis: " + len(col_names))

    # two-way anova
    formula = col_names[2] + " ~ C(" + col_names[0] + ") + C(" + col_names[1] + ")"
    formula_interaction = formula.replace('+', '*')
    interaction_lm = ols(formula, data=factor_groups).fit()  # linear model
    print(interaction_lm.summary())

    print(FORMAT_LINE)
    print("- " + col_names[2] + " = " + col_names[0] + " * " + col_names[1] + " Interaction -")
    print(anova_lm(ols(formula_interaction, data=factor_groups).fit(), interaction_lm))

    print(FORMAT_LINE)
    print("- " + col_names[2] + " = " + col_names[0] + " + " + col_names[1] + " ANOVA -")
    print(anova_lm(ols(col_names[2] + " ~ C(" + col_names[0] + ")", data=factor_groups).fit(), ols(col_names[2] +" ~ C("+col_names[0]+") + C(" + col_names[1]+", Sum)", data=factor_groups).fit()))

    print(FORMAT_LINE)
    print("- " + col_names[2] + " = " + col_names[1] + " + " + col_names[0] + " ANOVA -")
    print(anova_lm(ols(col_names[2] + " ~ C(" + col_names[1] + ")", data=factor_groups).fit(), ols(col_names[2] +" ~ C("+col_names[0]+") + C(" + col_names[1]+", Sum)", data=factor_groups).fit()))

def plot_interaction(data_lastDV):
    """
    Plot the interaction of the given data (should be three columns)
    :param data: data frame containing the independent variables in first two columns, dependent in the third
    :return: None
    """
    col_names = data_lastDV.columns.values  # get the columns' names
    factor_groups = data_lastDV[col_names].dropna()

    # TODO: fix the boxplot generating a separate plot (why doesn't subplots work?)
    plt.figure()

    plt.subplot(121)
    interaction_plot(factor_groups[col_names[0]], factor_groups[col_names[1]], factor_groups[col_names[2]], colors=['red', 'blue'], markers=['D', '^'], ms=10, ax=plt.gca())

    plt.subplot(122)
    factor_groups.boxplot(return_type='axes', column=col_names[2], by=[col_names[0], col_names[1]])
    plt.show()

def compare_plot_helpers(data_lastDV):
    """
    Print comparison plots for given data frame
    :param data: dataframe with all variables. Outcome variable in last index.
    :return: None
    """
    # TODO: These should be box plots, not bar plots
    col_names = data_lastDV.columns.values.tolist()  # get the columns' names
    outcome = col_names.pop()  # remove the last item in the list

    fig = plt.figure()
    i = 1
    for cond in col_names:
        ax = fig.add_subplot(2, 3, i)
        #df_compare = pd.concat([data.groupby(cond)[cond].count(), data.groupby(cond)[outcome].mean()], axis=1) # displays num helpers selected in each condition
        df_compare = data_lastDV.groupby(cond)[outcome].mean()  # displays num helpers selected in each condition
        ax = df_compare.plot(kind='bar', title=cond)
        ax.set_xlabel(cond)
        ax.set_ylabel("mean " + outcome)
        i += 1
    fig.tight_layout()
    plt.show()

def compare_plot_instances(data_causal):
    """
    Print comparison plots for given data frame, show num instances in each condition
    :param data: pandas dataframe we are exploring
    :return: None
    """
    col_names = data_causal.columns.values  # get the columns' names

    fig = plt.figure()
    i = 1
    for cond in col_names:
        ax = fig.add_subplot(2, 3, i)
        df_compare = data_causal.groupby(cond)[cond].count()  # displays num instances assigned to each condition
        ax = df_compare.plot(kind='bar', title=cond)
        ax.set_xlabel(cond)
        ax.set_ylabel("count instances")
        i += 1
    fig.tight_layout()
    plt.show()


def descriptive_plot(data_date_DV):
    """
    Print descriptive plot for give data frame
    :param data: dataframe, first column is a date last column is numerical outcome variable
    :return: None
    """
    col_names = data_date_DV.columns.values.tolist()  # get the columns' names
    data_date = col_names.pop(0)  # first item is the topic
    outcome = col_names.pop()  # remove the last item in the list

    helpers_by_date = data_date_DV[outcome]
    helpers_by_date.index = data_date_DV[data_date]
    helpers_by_date = helpers_by_date.cumsum()

    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax1 = helpers_by_date.plot(title=outcome+" Selected Over Time")
    ax1.locator_params(axis='x', nbins=6)
    ax1.set_xlabel(data_date)
    ax1.set_ylabel("Cumulative "+outcome)

    ax2 = fig.add_subplot(122)
    helpers_hist = data_date_DV[outcome]
    ax2 = helpers_hist.plot(kind='hist', title="Histogram "+outcome, by=outcome)
    ax2.locator_params(axis='x', nbins=4)
    ax2.set_xlabel(outcome+" (0,1,2,3)")
    ax2.set_ylabel("Num Instances")
    fig.tight_layout()
    plt.show()

def descriptive_stats(data_lastDV):
    """
    Print descriptive statistics for give data frame

    # Note: Descriptive stats help check independent/causal vars (that are categorical) for even assignment/distribution
    # Note: For scalar indepenent variables, you check for normal distribution (easy way: distribution plots)
    :param data: pandas dataframe we are exploring
    :return: None
    """
    col_names = data_lastDV.columns.values.tolist()  # get the columns' names
    outcome = col_names.pop()  # remove the last item in the list

    # Summary of Number of Helpers Selected
    print(FORMAT_LINE)
    print("Descriptive statistics for: \'" + outcome+"\'")
    print(data_lastDV[outcome].describe())
    print(FORMAT_LINE)

    # Descriptive Statistics of conditions
    print(FORMAT_LINE)
    print("Descriptive statistics for: all conditions")
    df_conditions = data_lastDV[col_names]
    print(df_conditions.describe())
    df_conditions = data_lastDV[col_names+[outcome]]  # add numerical column back in for descriptive stats

    # Count/Descriptive Stats of individual conditions & mean num helps of each (2^5) conditions
    for cond in col_names:
        print(FORMAT_LINE)
        print("Counts & Mean " + outcome + " for: \'" + cond)
        print(pd.concat([df_conditions.groupby(cond)[cond].count(), df_conditions.groupby(cond)[outcome].mean()], axis=1))

def one_stats(data_lastDV):
    """
    Do basic analysis of one IV onto one DV
    :param data: pandas dataframe we are exploring (IV-of-interest in first column, followed by IVs, and DV in last index)
    :return: None
    """
    col_names = data_lastDV.columns.values.tolist()  # get the columns' names
    causal = col_names.pop(0)  # first item is the topic
    outcome = col_names.pop()  # remove the last item in the list
    topic_data = data_lastDV[[causal, outcome]]

    # descriptive stats
    print(FORMAT_LINE)
    print(topic_data[causal].describe())
    print(FORMAT_LINE)

    fig = plt.figure()
    # bar chart of topics
    ax1 = fig.add_subplot(121)
    df_compare = topic_data.groupby(causal)[causal].count()  # displays num instances assigned to each condition
    ax1 = df_compare.plot(kind='bar', title=causal)
    ax1.set_xlabel(causal)
    ax1.set_ylabel("count instances")
    # scatter plot
    ax2 = fig.add_subplot(122)
    df_compare = data_lastDV.groupby(causal)[outcome].mean()  # displays num helpers selected in each topic
    ax2 = df_compare.plot(kind='bar', title=causal)
    ax2.set_xlabel(causal)
    ax2.set_ylabel("mean " + outcome)
    plt.show()

    # One Way ANOVA
    cond_lm = ols(outcome + " ~ C(" + causal + ")", data=topic_data).fit()
    anova_table = anova_lm(cond_lm)

    print("\n"+FORMAT_LINE)
    print("One-Way ANOVA: " + causal + " --> " + outcome)
    print(FORMAT_LINE)
    print(anova_table)
    #print(cond_lm.model.data.orig_exog)
    print(cond_lm.summary())

    # boxplot of topics --> num helpers selected
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax = topic_data.boxplot(outcome, causal, ax=plt.gca())
    ax.set_xlabel(causal)
    ax.set_ylabel(outcome)
    plt.show()

    for cond in col_names:
        anova_interaction(data_lastDV[[causal, cond, outcome]])
        plot_interaction(data_lastDV[[causal, cond, outcome]])

'''
...So that statsMOOC can act as either a reusable module, or as a standalone program.
'''
if __name__ == '__main__':
    run()
