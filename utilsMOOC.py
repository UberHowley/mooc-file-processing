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
CONST_FIRST_DAY = datetime.date(2014, 10, 27)  # the first day we got the system working properly
CONST_LAST_DAY = datetime.date(2014, 12, 17)

# COLUMN HEADER NAMES
COL_USERID = "userID"
COL_INSTANCEID = "instanceID"
COL_DATE = "Date"
COL_TIME = "Time"
# conditions
COL_BADGE = "isBadgeCondition"
COL_IRRELEVANT = "isIrrelevantSentence"
COL_VOTING = "isVotingCondition"
COL_ANONIMG = "isAnonImg"
COL_USERNAME = "isUsernameCondition"
# user.log
COL_QTITLE = "quesTitle"
COL_QBODY = "quesBody"
COL_HELPER0 = "helper0"
COL_HELPER1 = "helper1"
COL_HELPER2 = "helper2"
COL_NUMHELPERS = "numHelpersSelected"
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