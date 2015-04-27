#!/usr/bin/env python

__author__ = 'IH'
__project__ = 'processMOOC'

import datetime

# LOGFILE NAMES
FILENAME_HELPERLOG = "helper"
FILENAME_SELECTIONLOG = "selection"
FILENAME_VOTELOG = "vote"
FILENAME_USERLOG = "user"
FILENAME_CLICKLOG = "click"
EXTENSION_LOGFILE = ".log"
EXTENSION_PROCESSED = ".csv"

# TEXT-RELATED VARIABLES
CONST_DELIMITER = ","

# limiting date
# CONST_FIRST_DAY = datetime.date(2014, 10, 20)  # actual first day of the course
CONST_FIRST_DAY = datetime.date(2014, 10, 27)  # the first day system worked properly
CONST_LAST_DAY = datetime.date(2014, 12, 17)

# User Inputs
NUM_LDA_TOPICS = 15  # number of topics in topic model
CONST_MIN_USERID = 0  # limiting student user IDs

# exclude these [researcher] IDs:
    # 5556926 - d
    # 5529557 - of
    # 5542424 - rb
    # 2030452 - dg
    # 4480312 - sj
exclude_ids = {4, 5, 100, 200, 300, 400, 5529617, 5384681, 5556926, 5529557, 5553363, 5542424, 2030452, 4480312}

# COLUMN VALUES
VAL_IS = "y"  # conditions values are stored as 0s and 1st but they're actually categorical, not numerical...
VAL_ISNOT = "n"
# COLUMN HEADER NAMES
COL_USERID = "userID"
COL_INSTANCEID = "instanceID"
COL_DATE = "Date"
COL_TIME = "Time"
COL_HELP_TOPIC = "isHelpRequest"
COL_SENTENCE_TYPE = "sentenceCondition"
# conditions
COL_BADGE = "isBadgeCondition"
COL_IRRELEVANT = "isIrrelevantSentence"
COL_VOTING = "isVotingCondition"
COL_ANONIMG = "isAnonImg"
COL_USERNAME = "isUsernameCondition"
# user.log
COL_TOPIC = "topicLDA"
COL_QTITLE = "quesTitle"
COL_QBODY = "quesBody"
COL_HELPER0 = "helper0"
COL_HELPER1 = "helper1"
COL_HELPER2 = "helper2"
COL_NUMHELPERS = "numHelpersSelected"
COL_VERSION = "version"
COL_SHOWN = "_shown"
CONST_TA = "TA"
CONST_STUDENT = "student"
# helper.log
COL_HELPERID = "helperUserID"
COL_PREVHELPREQ = "NumPrevHelpRequests"
COL_NUMSTARS = "numBadgeStars"
COL_NUMWEEKS = "numWeeks"
COL_TOPICMATCH = "topicMatch"
COL_RELSENTENCE = "recommenderSentence"
COL_IRRELSENTENCE = "irrelevantSentence"
COL_WASSELECTED = "wasSelected"
# selection.log
COL_HELPERSELECTED = "index_SelectedHelper"
COL_SELECTEDHELPER_ID = "id_SelectedHelper"
# vote.log
COL_VOTE = "vote"
# click.log
COL_URL = "url"
COL_DATE_SENT = COL_DATE+"UrlSent"
COL_TIME_SENT = COL_TIME+"UrlSent"
COL_DATE_CLICKED = COL_DATE+"UrlClicked"
COL_TIME_CLICKED = COL_TIME+"UrlClicked"

# statsMOOC
FORMAT_LINE = "--------------------"