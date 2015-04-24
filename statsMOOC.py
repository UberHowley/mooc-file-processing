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
    conditions = [utils.COL_BADGE, utils.COL_IRRELEVANT, utils.COL_VOTING, utils.COL_USERNAME, utils.COL_ANONIMG]  # all our categorical IVs
    # TODO: decide if 'conditions' should include version or not

    user_input = input("> Print descriptive statistics? [y/n]: ")
    if is_yes(user_input):
        descriptive_stats(data[conditions+[utils.COL_VERSION, utils.COL_NUMHELPERS]].dropna())
    user_input = input(">> Display descriptive statistics plot? [y/n]: ")
    if is_yes(user_input):
        compare_plot_instances(data[conditions+[utils.COL_VERSION]])

    user_input = input(">> Display descriptive plot of " + utils.COL_NUMHELPERS + "? [y/n]: ")
    if is_yes(user_input):
        descriptive_plot(data)

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

    user_input = input("> Do analysis of message post topics? [y/n]: ")
    if is_yes(user_input):
        try:
            topic_data = data[[utils.COL_TOPIC]+conditions+[utils.COL_VERSION, utils.COL_NUMHELPERS]].dropna()
        except KeyError:
            print("ERROR in statsMOOC.py: No such column as " + utils.COL_TOPIC + ". Did you run logfileMOOC.py?")
        topic_stats(topic_data)


def is_yes(stri):
    """
    Return True if the given string contains a 'y'
    :param str: a string, likely a user console input
    :return: True if the string contains the letter 'y'
    """
    return 'y' in stri.lower()

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
        cat1 = df[df[cond] == utils.VAL_IS][outcome]
        cat2 = df[df[cond] == utils.VAL_ISNOT][outcome]

        print("\n"+utils.FORMAT_LINE)
        print("T-test: " + cond)
        print(utils.FORMAT_LINE)
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

        print("\n"+utils.FORMAT_LINE)
        print("One-Way ANOVA: " + cond)
        print(utils.FORMAT_LINE)
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

    print(utils.FORMAT_LINE)
    print("- " + col_names[2] + " = " + col_names[0] + " * " + col_names[1] + " Interaction -")
    print(anova_lm(ols(formula_interaction, data=factor_groups).fit(), interaction_lm))

    print(utils.FORMAT_LINE)
    print("- " + col_names[2] + " = " + col_names[0] + " + " + col_names[1] + " ANOVA -")
    print(anova_lm(ols(col_names[2] + " ~ C(" + col_names[0] + ")", data=factor_groups).fit(), ols(col_names[2] +" ~ C("+col_names[0]+") + C(" + col_names[1]+", Sum)", data=factor_groups).fit()))

    print(utils.FORMAT_LINE)
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
    print(utils.FORMAT_LINE)
    print("Descriptive statistics for: \'" + outcome+"\'")
    print(data_lastDV[outcome].describe())
    print(utils.FORMAT_LINE)

    # Descriptive Statistics of conditions
    print(utils.FORMAT_LINE)
    print("Descriptive statistics for: all conditions")
    df_conditions = data_lastDV[col_names]
    print(df_conditions.describe())
    df_conditions = data_lastDV[col_names+[outcome]]  # add numerical column back in for descriptive stats

    # Count/Descriptive Stats of individual conditions & mean num helps of each (2^5) conditions
    for cond in col_names:
        print(utils.FORMAT_LINE)
        print("Counts & Mean " + outcome + " for: \'" + cond)
        print(pd.concat([df_conditions.groupby(cond)[cond].count(), df_conditions.groupby(cond)[outcome].mean()], axis=1))

def topic_stats(topic_data_lastDV):
    """
    Do basic analysis of LDA topics
    :param data: pandas dataframe we are exploring (topic in first column, followed by IVs, and DV in last index)
    :return: None
    """
    col_names = topic_data_lastDV.columns.values.tolist()  # get the columns' names
    topic = col_names.pop(0)  # first item is the topic
    outcome = col_names.pop()  # remove the last item in the list
    topic_data = topic_data_lastDV[[topic, outcome]]

    # descriptive stats
    print(utils.FORMAT_LINE)
    print(topic_data[topic].describe())
    print(utils.FORMAT_LINE)

    fig = plt.figure()
    # bar chart of topics
    ax1 = fig.add_subplot(121)
    df_compare = topic_data.groupby(topic)[topic].count()  # displays num instances assigned to each condition
    ax1 = df_compare.plot(kind='bar', title=topic)
    ax1.set_xlabel(topic)
    ax1.set_ylabel("count instances")
    # scatter plot
    ax2 = fig.add_subplot(122)
    df_compare = topic_data_lastDV.groupby(topic)[outcome].mean()  # displays num helpers selected in each topic
    ax2 = df_compare.plot(kind='bar', title=topic)
    ax2.set_xlabel(topic)
    ax2.set_ylabel("mean " + outcome)
    plt.show()

    # One Way ANOVA
    cond_lm = ols(outcome + " ~ C(" + topic + ")", data=topic_data).fit()
    anova_table = anova_lm(cond_lm)

    print("\n"+utils.FORMAT_LINE)
    print("One-Way ANOVA: " + topic + " -->" + outcome)
    print(utils.FORMAT_LINE)
    print(anova_table)
    #print(cond_lm.model.data.orig_exog)
    print(cond_lm.summary())

    # boxplot of topics --> num helpers selected
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax = topic_data.boxplot(outcome, topic, ax=plt.gca())
    ax.set_xlabel(topic)
    ax.set_ylabel(outcome)
    plt.show()

    for cond in col_names:
        anova_interaction(topic_data_lastDV[[topic, cond, outcome]])
        plot_interaction(topic_data_lastDV[[topic, cond, outcome]])

'''
...So that statsMOOC can act as either a reusable module, or as a standalone program.
'''
if __name__ == '__main__':
    run()
