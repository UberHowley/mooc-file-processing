#!/usr/bin/env python

__author__ = 'IH'
__project__ = 'processMOOC'

import utilsMOOC as utils
import copy
import datetime
import re
from html.parser import HTMLParser
from collections import defaultdict
from QHInstance import QHInstance
from stop_words import get_stop_words
from gensim import corpora, models, similarities

# LOGFILE NAMES
FILENAME_HELPERLOG = utils.FILENAME_HELPERLOG
FILENAME_SELECTIONLOG = utils.FILENAME_SELECTIONLOG
FILENAME_VOTELOG = utils.FILENAME_VOTELOG
FILENAME_USERLOG = utils.FILENAME_USERLOG
FILENAME_CLICKLOG = utils.FILENAME_CLICKLOG
EXTENSION_LOGFILE = utils.EXTENSION_LOGFILE
EXTENSION_PROCESSED = utils.EXTENSION_PROCESSED

# TEXT-RELATED VARIABLES
CONST_DELIMITER = utils.CONST_DELIMITER
CONST_DELIMITERVAR = "<DELIMITER>"
CONST_LINESTART = "{\"level\":\"info\",\"message\":\"<DELIMITER>"

# limiting date
CONST_FIRST_DAY = utils.CONST_FIRST_DAY
CONST_LAST_DAY = utils.CONST_LAST_DAY

# IMAGE VARIABLES
BADGE_NONE = {"http://erebor.lti.cs.cmu.edu/quickhelper/badges/blank.png", "http://i62.tinypic.com/2mgqut2.jpg"}
BADGE_ONE = {"http://erebor.lti.cs.cmu.edu/quickhelper/badges/helper1.png", "http://i61.tinypic.com/24q1jyr.jpg"}
BADGE_TWO = {"http://erebor.lti.cs.cmu.edu/quickhelper/badges/helper2.png", "http://i58.tinypic.com/29yjuww.jpg"}
BADGE_THREE = {"http://erebor.lti.cs.cmu.edu/quickhelper/badges/helper3.png", "http://i62.tinypic.com/214w7wl.jpg"}
BADGE_FOUR = {"http://erebor.lti.cs.cmu.edu/quickhelper/badges/helper4.png", "http://i58.tinypic.com/2cgymgh.jpg"}

BADGE_NONE_TXT = "0"
BADGE_ONE_TXT = "1"
BADGE_TWO_TXT = "2"
BADGE_THREE_TXT = "3"
BADGE_FOUR_TXT = "4"

# mapping from instance ID to conditions (badge, sentence, voting, userid)
count_repeat = 0
dict_last_digs = {}
dict_helpers = defaultdict(list)  # instanceID -> a list of helper IDs shown
dict_selected_helpers = defaultdict(list)  # instanceID -> a list of helper IDs that were selected
dict_badge = {}
dict_sentence = {}
dict_voting = {}
dict_user_id = {}

instances_by_dupkey = defaultdict(list)  # dup key -> instance objects, keeping track of all items by duplicate key
instances_by_id = {}  # instance ID -> instance object
dict_all_helpers = defaultdict(list)  # instance_id -> list (3) helper logfile entries to remove duplicates from later
dict_num_helpers = {}  # instance_id -> num helpers selected, to add to our instances
list_no_duplicates = []  # a list of instances with duplicates removed
list_sentences = []  # a list of a list of all words in post titles + post bodies, indices refer to Instances in list_no_duplicates

# TODO: command line input for column delimiters, dates, filenames, etc.

def run():
    """
    Call the functions that do the processing for each kind of file
    user.log is processed first and then written to file at the end
    :return: None
    """
    # Process of files
    proc_user()
    proc_selection()
    proc_helper()
    proc_vote()
    proc_click()

    remove_duplicates()  # remove duplicates from user.log and helper.log

    # user.log must be written at the end, because we need info from select.log
    list_no_duplicates.sort(key=lambda r:r.timestamp)  # sort by timestamp

    # Writing to userfile and helperfile at the same time
    userfile_out = open(FILENAME_USERLOG+EXTENSION_PROCESSED,'w')
    userfile_out.write(QHInstance.get_headers(delimiter=CONST_DELIMITER)+'\n')
    helperfile_out = open(FILENAME_HELPERLOG+EXTENSION_PROCESSED, 'w')
    helperfile_out.write(utils.COL_HELPERID+CONST_DELIMITER+utils.COL_INSTANCEID+CONST_DELIMITER+utils.COL_NUMSTARS+CONST_DELIMITER+utils.COL_PREVHELPREQ+CONST_DELIMITER+utils.COL_NUMWEEKS+CONST_DELIMITER+utils.COL_TOPICMATCH+CONST_DELIMITER+utils.COL_RELSENTENCE+CONST_DELIMITER+utils.COL_IRRELSENTENCE+CONST_DELIMITER+utils.COL_DATE+CONST_DELIMITER+utils.COL_TIME + CONST_DELIMITER + utils.COL_WASSELECTED + CONST_DELIMITER + utils.COL_BADGE+ CONST_DELIMITER + utils.COL_IRRELEVANT + CONST_DELIMITER + utils.COL_VOTING + CONST_DELIMITER + utils.COL_USERNAME+"\n")

    for qh_instance in list_no_duplicates:
        # set the selected number of helpers for each instance
        setattr(qh_instance, 'num_helpers_selected', dict_num_helpers.get(getattr(qh_instance, 'instance_id'), 0))

        # assign topic
        lda_vector = lda[dict_lda.doc2bow(doc)]
        print(max(lda_vector, key=lambda item: item[1])[0])
        # print(lda.print_topic(max(lda_vector, key=lambda item: item[1])[0]))  # prints the most prominent LDA topic
        line = qh_instance.to_string(delimiter=CONST_DELIMITER)

        # print associated helpers to the helper.log
        for helper_line in dict_all_helpers[getattr(qh_instance, 'instance_id')]:
            helperfile_out.write(helper_line+'\n')
        userfile_out.write(line+'\n')
    userfile_out.close()
    helperfile_out.close()
    print("Done writing " + FILENAME_USERLOG+EXTENSION_LOGFILE+ " and " + FILENAME_HELPERLOG+EXTENSION_LOGFILE)
    print("\tNumber of repeats in "+FILENAME_USERLOG+EXTENSION_LOGFILE+": "+str(count_repeat)+"\n")

    create_lda()

def proc_user():
    """
    Process the user log.
    A line in the Userfile Log represents what user-level variables the user saw (specific information about individual
    helpers shown is stored in the Helperfile Log).
    ex: {"level":"info","message":"<DELIMITER>100<DELIMITER>1413061797181100<DELIMITER>1<DELIMITER>0<DELIMITER>1<DELIMITER>1<DELIMITER>0<DELIMITER>1833503<DELIMITER>2512601<DELIMITER>1657199<DELIMITER>title1<DELIMITER>body1<DELIMITER>","timestamp":"2014-10-11T21:09:57.182Z"}
    Help Seeker User ID, Instance ID, Badge Shown?, Irrelevant Sentence Shown?, Voting Shown?, Anonymized Image Shown?, User ID Shown?, helper0, helper1, helper2, Question title, Question body
    :return: None
    """
    print("Processing "+FILENAME_USERLOG+EXTENSION_LOGFILE)

    with open(FILENAME_USERLOG+EXTENSION_LOGFILE,'r') as f:
        for line in f:
            line = line[len(CONST_LINESTART): len(line)]   # Cut off the extra chars from beginning
            line = line.replace(CONST_DELIMITER, ' ')  # Replace all occurrences of delimiters with empty space
            line = line.replace(CONST_DELIMITERVAR, CONST_DELIMITER)  # Replace delimiter stand-in with actual delimiters
            array_line = line.split(CONST_DELIMITER)
            #print(str(len(array_line))+" " +line)
            col_user_id= array_line[0]
            col_instance_id = array_line[1]
            col_badge_shown = array_line[2]
            col_irrelevant_sentence = array_line[3]
            col_voting = array_line[4]
            col_anon_img = array_line[5]
            col_userid_shown = array_line[6]
            col_helper0 = array_line[7]
            col_helper1 = array_line[8]
            col_helper2 = array_line[9]
            col_ques_title = array_line[10]
            col_ques_body = array_line[11]

            # processing the timestamp
            col_timestamp = get_timestamp(array_line[len(array_line) - 1])  # We know the last column is always a timestamp

            #  processing extra column with a URL
            col_url = ""
            if len(array_line) > 13:
                col_url = array_line[12]
            # if the helper IDs are greater than the minimum, this is likely a TA version instance
            col_version = utils.CONST_TA
            if (int(col_helper0) > utils.CONST_MIN_USERID or int(col_helper1) > utils.CONST_MIN_USERID or int(col_helper2) > utils.CONST_MIN_USERID):
                col_version = utils.CONST_STUDENT

            # turns 0 and 1 conditional variables into categorical variables
            if int(col_badge_shown):
                col_badge_shown = utils.VAL_IS
            else:
                col_badge_shown = utils.VAL_ISNOT
            if int(col_irrelevant_sentence):
                col_irrelevant_sentence = utils.VAL_IS
            else:
                col_irrelevant_sentence = utils.VAL_ISNOT
            if int(col_voting):
                col_voting = utils.VAL_IS
            else:
                col_voting = utils.VAL_ISNOT
            if int(col_anon_img):
                col_anon_img = utils.VAL_IS
            else:
                col_anon_img = utils.VAL_ISNOT
            if int(col_userid_shown):
                col_userid_shown = utils.VAL_IS
            else:
                col_userid_shown = utils.VAL_ISNOT

            # Create QHInstance
            user_instance = QHInstance(col_user_id, col_instance_id, col_version, col_badge_shown, col_irrelevant_sentence, col_voting, col_anon_img, col_userid_shown,col_helper0, col_helper1, col_helper2, col_ques_title, col_ques_body, col_url, col_timestamp)


            # keeping track of instances for printing late (if in correct date range)
            # store instance if it's during the right time period
            # AND if it's not one of the researchers' actions
            # AND only if the message body is longer than __ characters.
            if is_during_course(col_timestamp.date()) and not is_researcher(col_user_id) and len(col_ques_body) > 10:
                instances_by_dupkey[user_instance.get_duplicate_key()].append(user_instance)

            # all duplicates get added to our condition dictionaries
            # since helper.log needs it (i.e., the first entry isn't
            # always the one that was shown!
            dict_badge[col_instance_id] = col_badge_shown
            dict_sentence[col_instance_id] = col_irrelevant_sentence
            dict_voting[col_instance_id] = col_voting
            dict_user_id[col_instance_id] = col_userid_shown

            instances_by_id[col_instance_id] = user_instance  # need this for the click.log

            # Add helper IDs to dictionary of instances to helpers
            dict_helpers[col_instance_id].append(col_helper0)
            dict_helpers[col_instance_id].append(col_helper1)
            dict_helpers[col_instance_id].append(col_helper2)
            #print(user_instance.to_string(delimiter=CONST_DELIMITER))
    print("Done processing "+FILENAME_USERLOG+EXTENSION_LOGFILE+"\n")

def proc_helper():
    """
    Process the helper log file.
    A line in the Helperfile Log represents all the information specific to the helper that the user saw.
    ex: {"level":"info","message":"<DELIMITER>1<DELIMITER>1413061797181100<DELIMITER>8<DELIMITER>http://i58.tinypic.com/2cgymgh.jpg<DELIMITER>3<DELIMITER>This student has been participating in the course for 1 weeks and the matching of his/her interest and the topic of your query is 100.0 .<DELIMITER>","timestamp":"2014-10-11T21:09:57.182Z"}
    :return: None
    """
    print("Processing "+FILENAME_HELPERLOG+EXTENSION_LOGFILE)

    with open(FILENAME_HELPERLOG+EXTENSION_LOGFILE, 'r') as f:
        for line in f:
            line = line[len(CONST_LINESTART): len(line)]  # Cut off the extra chars from beginning
            line = line.replace(CONST_DELIMITER, ' ')  # Replace all occurrences of delimiters with empty space
            line = line.replace(CONST_DELIMITERVAR,CONST_DELIMITER)  # Replace delimiter stand-in with actual delimiters
            # print(line)
            array_line = line.split(CONST_DELIMITER)
            col_helper_id = array_line[0]
            col_instance_id = array_line[1]
            col_helper_name = array_line[2]
            col_badge_shown = get_badge_stars(array_line[3])
            col4 = array_line[4]
            col_rec_sentence = array_line[5]
            col_irrel_sentence = "unknown"  # This was missing in the logs!
            col_num_weeks = get_num_weeks(col_rec_sentence)
            col_topic_match = get_topic_match(col_rec_sentence)

            # Processing the timestamp into a datetime object
            col_timestamp = get_timestamp(array_line[len(array_line) - 1])  # We know the last column is always a timestamp
            col_date = col_timestamp.date()
            col_time = col_timestamp.time()

            # Constructing the new helper logfile line
            line = col_helper_id + CONST_DELIMITER + col_instance_id + CONST_DELIMITER
            line += col_badge_shown + CONST_DELIMITER + col4 + CONST_DELIMITER + col_num_weeks + CONST_DELIMITER
            line += col_topic_match + CONST_DELIMITER + col_rec_sentence + CONST_DELIMITER + col_irrel_sentence + CONST_DELIMITER
            line += str(col_date) + CONST_DELIMITER + str(col_time)

            # determine if this helper was selected
            was_selected = utils.VAL_ISNOT
            if col_instance_id not in dict_helpers:  # that instance didn't occur in user.log
                print("WARNING: instanceID in "+FILENAME_HELPERLOG+EXTENSION_LOGFILE+" not found in " + FILENAME_USERLOG+EXTENSION_LOGFILE+", not writing to file: " + col_instance_id)
            elif col_helper_id in dict_selected_helpers[col_instance_id]:  # this ID was selected in selection.log
                was_selected = utils.VAL_IS
            line += CONST_DELIMITER + str(was_selected)

            # retrieve experimental conditions from dict
            if col_instance_id not in dict_badge:
                print("WARNING: "+FILENAME_HELPERLOG+EXTENSION_LOGFILE+" instance does not exist in" + FILENAME_USERLOG+EXTENSION_LOGFILE+": "+col_instance_id)
            line += CONST_DELIMITER + str(dict_badge.get(col_instance_id, "")) + CONST_DELIMITER + str(dict_sentence.get(col_instance_id, "")) + CONST_DELIMITER + str(dict_voting.get(col_instance_id, "")) + CONST_DELIMITER + str(dict_user_id.get(col_instance_id, ""))

            # only store line if it's in our date range and it appeared in user.log
            if is_during_course(col_date) and col_instance_id in dict_helpers:  # that instance didn't occur in user.log:
                dict_all_helpers[col_instance_id].append(line)
            #print(line)
    print("Done processing "+FILENAME_HELPERLOG+EXTENSION_LOGFILE+"\n")

def proc_selection():
    """
    Process the selection log file.
    A line in the Helperfile Log represents one (of three maximum) of the helpers selected by user
    ex: {"level":"info","message":"<DELIMITER>11<DELIMITER>0<DELIMITER>","timestamp":"2014-10-11T21:09:57.211Z"}
    :return:
    """
    print("Processing "+FILENAME_SELECTIONLOG+EXTENSION_LOGFILE)

    file_out = open(FILENAME_SELECTIONLOG+EXTENSION_PROCESSED,'w')
    file_out.write(utils.COL_INSTANCEID+CONST_DELIMITER+utils.COL_HELPERSELECTED+CONST_DELIMITER+utils.COL_SELECTEDHELPER_ID+CONST_DELIMITER+utils.COL_DATE+CONST_DELIMITER+utils.COL_TIME+"\n")

    with open(FILENAME_SELECTIONLOG+EXTENSION_LOGFILE,'r') as f:
        for line in f:
            line = line[len(CONST_LINESTART): len(line)]  # Cut off the extra chars from beginning
            line = line.replace(CONST_DELIMITER, ' ')  # Replace all occurrences of delimiters with empty space
            line = line.replace(CONST_DELIMITERVAR,CONST_DELIMITER)  # Replace delimiter stand-in with actual delimiters
            # print(line)
            array_line = line.split(CONST_DELIMITER)
            col_instance_id = array_line[0]
            col_helper_selected = array_line[1]

            # Processing the timestamp into a datetime object
            col_timestamp = get_timestamp(array_line[len(array_line) - 1])  # We know the last column is always a timestamp
            col_date = col_timestamp.date()
            col_time = col_timestamp.time()

            # Constructing the new selection logfile line
            line = col_instance_id + CONST_DELIMITER + col_helper_selected + CONST_DELIMITER

            # retrieve helper user ID
            if len(col_helper_selected) > 1:  #i.e., it's not 0,1, or 2 ("NONE")
                line += ""
            else:
                array_helpers = dict_helpers[col_instance_id]  # all helpers shown for this instance
                helper_id = ""
                if len(array_helpers) < int(col_helper_selected)+1:  # less helpers than the index of this helper
                    print("WARNING: Helper index ("+col_helper_selected+") referenced in " + FILENAME_SELECTIONLOG+EXTENSION_LOGFILE+" is outside possible number of helpers (i.e., "+str(len(array_helpers))+"): " + col_instance_id)
                elif 0 <= int(col_helper_selected) <= 2:  # valid index is 0, 1, or 2
                    helper_id = array_helpers[int(col_helper_selected)]
                else:  # we have an invalid helper index
                    print("WARNING: Helper index ("+col_helper_selected+") referenced in " + FILENAME_SELECTIONLOG+EXTENSION_LOGFILE+" does not exist in instance: " + col_instance_id)
                line += helper_id

                # record this as a selected helper for helper.log
                dict_selected_helpers[col_instance_id].append(helper_id)
                dict_num_helpers[col_instance_id] = int(dict_num_helpers.get(col_instance_id, 0)) + 1  # add one to our number of helpers selected

            # continue...
            line += CONST_DELIMITER + str(col_date) + CONST_DELIMITER + str(col_time)

            # only write line if it's in our date range
            if is_during_course(col_date):
                file_out.write(line+'\n')

    print("Done processing "+FILENAME_SELECTIONLOG+EXTENSION_LOGFILE+"\n")
    file_out.close()

def proc_vote():
    """
    Process the vote log file.
    A line in the Upvote Log represents each instance a Helper up or downvotes a QuickHelp request.
    ex: {"level":"info","message":"<DELIMITER>2231948<DELIMITER>1<DELIMITER>1<DELIMITER>","timestamp":"2014-10-11T06:05:13.668Z"}
    :return: None
    """
    print("Processing "+FILENAME_VOTELOG+EXTENSION_LOGFILE)

    file_out = open(FILENAME_VOTELOG+EXTENSION_PROCESSED,'w')
    file_out.write(utils.COL_HELPERID+CONST_DELIMITER+utils.COL_INSTANCEID+CONST_DELIMITER+utils.COL_VOTE+CONST_DELIMITER+utils.COL_DATE+CONST_DELIMITER+utils.COL_TIME+"\n")

    with open(FILENAME_VOTELOG+EXTENSION_LOGFILE,'r') as f:
        for line in f:
            line = line[len(CONST_LINESTART): len(line)]  # Cut off the extra chars from beginning
            line = line.replace(CONST_DELIMITER, ' ')  # Replace all occurrences of delimiters with empty space
            line = line.replace("<i>", '')  # Vote.log has some HTML to remove
            line = line.replace("</i>", '')
            line = line.replace(CONST_DELIMITERVAR,CONST_DELIMITER)  # Replace delimiter stand-in with actual delimiters
            # print(line)
            array_line = line.split(CONST_DELIMITER)
            col_helper_id = array_line[0]
            col_instance_id = array_line[1]
            col_vote = array_line[2]

            # Processing the timestamp into a datetime object
            col_timestamp = get_timestamp(array_line[len(array_line) - 1])  # We know the last column is always a timestamp
            col_date = col_timestamp.date()
            col_time = col_timestamp.time()

            # Constructing the new vote logfile line
            line = col_helper_id + CONST_DELIMITER + col_instance_id + CONST_DELIMITER + col_vote + CONST_DELIMITER
            line += str(col_date) + CONST_DELIMITER + str(col_time)

            # only write line if it's in our date range
            if is_during_course(col_date):
                file_out.write(line+'\n')
            #print(line)
    print("Done processing "+FILENAME_VOTELOG+EXTENSION_LOGFILE+"\n")
    file_out.close()

def proc_click():
    """
    Process the click log file.
    A line in the Click Log represents each instance a Helper up or downvotes a QuickHelp request.
    {"level":"info","message":"<DELIMITER><i>helper_id</i><DELIMITER><i>instance_id</i><DELIMITER>https://www.edx.org//courses/UTArlingtonX/LINK5.10x/3T2014/discussion/forum/8d9482b366ae4999b706b2d7372d8393/threads/54808da7a2a525e05300156b<DELIMITER>","timestamp":"2014-12-04T16:35:45.863Z"}
    :return: None
    """
    print("Processing "+FILENAME_CLICKLOG+EXTENSION_LOGFILE)

    file_out = open(FILENAME_CLICKLOG+EXTENSION_PROCESSED,'w')
    file_out.write(utils.COL_HELPERID+CONST_DELIMITER+utils.COL_INSTANCEID+CONST_DELIMITER+utils.COL_DATE_SENT+CONST_DELIMITER+utils.COL_TIME_SENT+CONST_DELIMITER+utils.COL_DATE_CLICKED+CONST_DELIMITER+utils.COL_TIME_CLICKED+CONST_DELIMITER+utils.COL_QTITLE+CONST_DELIMITER+utils.COL_QBODY+CONST_DELIMITER+utils.COL_URL+"\n")

    with open(FILENAME_CLICKLOG+EXTENSION_LOGFILE,'r') as f:
        for line in f:
            line = line[len(CONST_LINESTART): len(line)]  # Cut off the extra chars from beginning
            line = line.replace(CONST_DELIMITER, ' ')  # Replace all occurrences of delimiters with empty space
            line = line.replace("<i>", '')  # Click.log has some HTML to remove
            line = line.replace("</i>", '')
            line = line.replace(CONST_DELIMITERVAR,CONST_DELIMITER)  # Replace delimiter stand-in with actual delimiters

            array_line = line.split(CONST_DELIMITER)
            col_helper_id = array_line[0]
            col_instance_id = array_line[1]
            col_url = array_line[2]

            # Processing the timestamp into a datetime object
            col_timestamp = get_timestamp(array_line[len(array_line) - 1])  # We know the last column is always a timestamp
            col_date_clicked = col_timestamp.date()
            col_time_clicked = col_timestamp.time()

            # Retrieving timestamp when URL was sent
            col_date_sent = ""
            col_time_sent = ""
            qtitle = ""
            qbody = ""
            if col_instance_id in instances_by_id:  # instance id might be 'instance_id'
                col_date_sent = getattr(instances_by_id[col_instance_id], 'timestamp').date()
                col_time_sent = getattr(instances_by_id[col_instance_id], 'timestamp').time()
                qtitle = getattr(instances_by_id[col_instance_id], 'question_title')
                qbody = getattr(instances_by_id[col_instance_id], 'question_body')
            else:
                print("WARNING: Encountered instance ID in " + FILENAME_CLICKLOG+EXTENSION_LOGFILE+" that is not in " + FILENAME_USERLOG+EXTENSION_LOGFILE+": " + col_instance_id)

            # Constructing the new vote logfile line
            line = col_helper_id + CONST_DELIMITER + col_instance_id + CONST_DELIMITER + str(col_date_sent) + CONST_DELIMITER
            line += str(col_time_sent) + CONST_DELIMITER + str(col_date_clicked) + CONST_DELIMITER
            line += str(col_time_clicked) + CONST_DELIMITER + qtitle + CONST_DELIMITER + qbody + CONST_DELIMITER + col_url

            # only write line if the email with URL was sent in our date range
            if col_instance_id in instances_by_id and is_during_course(col_date_sent):
                file_out.write(line+'\n')
                # TODO: there's duplicates in the click logs from clicking several times that need to be removed
            #print(line)
    print("Done processing "+FILENAME_CLICKLOG+EXTENSION_LOGFILE+"\n")
    file_out.close()

def remove_duplicates():
    """
     Remove duplicates from our list of instances, based on whatever key was used in duplicate_instances
    Also removes duplicate from our helper logs
    :return: A list of QHInstances with all duplicates removed
    """
    for duplicate_key in instances_by_dupkey:  # iterate through each key in our duplicate-arranged list
        selected_dup = None  # instance with a selection (the one shown)
        for dup in instances_by_dupkey[duplicate_key]:  # for each instance object in these duplicates
            if getattr(dup, utils.COL_NUMHELPERS, 0) > 0:  # If it has helpers selected, it's the one
                selected_dup = dup
        if selected_dup is None:
                selected_dup = create_new_duplicate(instances_by_dupkey[duplicate_key])  # Clear out non-matching condition variables
        list_no_duplicates.append(selected_dup)  # Record selected_dup as our correct one
        # Store this sentence, too
        list_sentences.append(clean_string(getattr(selected_dup, 'question_title', '')+' '+getattr(selected_dup,'question_body','')))

        if len(instances_by_dupkey[duplicate_key]) > 1:  # if we have more than one value attached to this key, they're duplicates
            global count_repeat
            count_repeat += len(instances_by_dupkey[duplicate_key])-1
    return list_no_duplicates

def create_new_duplicate(duplicates):
    """
     Given a list of duplicates, return a QHInstance that only has entries for columns
    that have identical values for all items in the list (i.e. "isBadgeShown" is 0 for all instances, etc)
    :param duplicates: a list of items that are pre-determined to be duplicates
    :return: a new QHInstance containing only info the duplicates share
    """
    # Creating our default duplicate object to return
    new_duplicate = copy.copy(duplicates[0])

    if len(duplicates) > 1:  # we have [several] duplicates
        badge = getattr(new_duplicate, 'cond_badge')
        sentence = getattr(new_duplicate,'cond_irrelevant_sentence')
        voting = getattr(new_duplicate, 'cond_voting')
        #anon_img = getattr(new_duplicate, 'cond_anon_img')  # Didn't implement the image condition, so don't worry about it
        uid = getattr(new_duplicate, 'cond_user_id')
        h0 = getattr(new_duplicate, 'id_helper0')
        h1 = getattr(new_duplicate, 'id_helper1')
        h2 = getattr(new_duplicate, 'id_helper2')

        same_badge = True
        same_sentence = True
        same_voting = True
        #same_img = True  # Didn't implement the image condition, so don't worry about it
        same_uid = True
        same_h0 = True
        same_h1 = True
        same_h2 = True

        for dup in duplicates:  # iterate through each duplicate-arranged list
            # Only check if they've been the same so far...
            if same_badge and not badge == getattr(dup, 'cond_badge'):  # attribute is not the same
                same_badge = False
                setattr(new_duplicate, 'cond_badge', "")
            if same_sentence and not sentence == getattr(dup, 'cond_irrelevant_sentence'):  # attribute is not the same
                same_sentence = False
                setattr(new_duplicate, 'cond_irrelevant_sentence', "")
            if same_voting and not voting == getattr(dup, 'cond_voting'):  # attribute is not the same
                same_voting = False
                setattr(new_duplicate, 'cond_voting', "")
            if same_uid and not uid == getattr(dup, 'cond_user_id'):  # attribute is not the same
                same_uid = False
                setattr(new_duplicate, 'cond_user_id', "")
            if same_h0 and not h0 == getattr(dup, 'id_helper0'):  # attribute is not the same
                same_h0 = False
                setattr(new_duplicate, 'id_helper0', "")
            if same_h1 and not h1 == getattr(dup, 'id_helper1'):  # attribute is not the same
                same_h1 = False
                setattr(new_duplicate, 'id_helper1', "")
            if same_h2 and not h2 == getattr(dup, 'id_helper2'):  # attribute is not the same
                same_h2 = False
                setattr(new_duplicate, 'id_helper2', "")
    return new_duplicate

def is_during_course(instance_date):
    """
    Determine if given date is within the range of dates the course took place
    :param instance_date: date to check if it's in range
    :return: True if given date is in our restricted time range
    """
    if instance_date is not None:
        if CONST_LAST_DAY >= instance_date >= CONST_FIRST_DAY:
            return True
        else:  # Not in given course date range
            return False
    else:
        print("ERROR:: logfileMOOC.is_during_course(): Cannot process date column: " + instance_date)
        return False

def is_researcher(userID):
    """
    Check if given user is one of the researchers
    :param userID: The user ID we want to see if it's a researcher/TA
    :return: True if userID is that of a researcher
    """
    return int(userID) < utils.CONST_MIN_USERID or int(userID) in utils.exclude_ids  # TAs and researchers had userIDs less than 0

def get_timestamp(tstamp):
    """
    Clean the timestamp from a messy string in the logfiles
    :param tstamp: string containing the timestamp
    :return: the datetime object
    """
    tstamp = tstamp[tstamp.index(':')+1: (len(tstamp)-2)].replace("\"",'')  # remove meta tags
    tstamp = tstamp.replace('Z', '')  # TODO: Figure out how to convert the Z at the end
    try:
        tstamp = datetime.datetime.strptime(tstamp,'%Y-%m-%dT%H:%M:%S.%f')
    except ValueError as err:
        print(tstamp, err)
    return tstamp

def get_badge_stars(url):
    """
    Determine how many stars were on the badge, depending on badge URL
    :param url: the urlk of the image of the badge shown
    :return: a string containing the number of stars in that badge
    """
    if url in BADGE_NONE:
        return BADGE_NONE_TXT
    elif url in BADGE_ONE:
        return BADGE_ONE_TXT
    elif url in BADGE_TWO:
        return BADGE_TWO_TXT
    elif url in BADGE_THREE:
        return BADGE_THREE_TXT
    elif url in BADGE_FOUR:
        return BADGE_FOUR_TXT
    else:
        print("ERROR:: logfileMOOC.get_badge_stars(): Missing badge ID: " + url)

def get_topic_match(sentence):
    """
    Find what the topic match percentage was given the topic match sentence
    :param sentence: the relevant sentence containing topic match info
    :return: topic match percentage
    """
    if sentence.find("Teaching Assistants") >= 0:
        return utils.CONST_TA
    else:
        tm = sentence[len(sentence)-7:len(sentence)-1]
        tm = float(tm.strip("abcdefghijklmnopqrstuvwxyz% "))
        if tm < 1:  # Turning decimals into percentage numbers
            tm = tm*100
        return str(tm)

def get_num_weeks(sentence):
    """
    Find how many weeks the helper's been around, given the topic match sentence
    :param sentence: the relevant sentence containing the number of weeks info
    :return: number of weeks been in the course
    """
    if sentence.find("Teaching Assistants") >= 0:
        return utils.CONST_TA
    else:
        return sentence[sentence.find("week")-2: sentence.find("week")]

def clean_string(sentence):
    """
    Clean the string by removing all punctuation
    http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
    :param sentence: the string potentially containing HTML and other non-alphanumerics
    :return: the string cleaned of all tags, undesirables
    """
    s = MLStripper()
    s.feed(sentence)
    no_html = s.get_data()
    # This code apparently removes all text in a string without any HTML
    if len(no_html) < 10:
        no_html = sentence
    cleaned = re.sub(r'\W+', ' ', no_html)  # removes everything except alphanumerics and spaces

    stoplist = set('for a of the and to in'.split())  # removing common words
    texts = [word for word in cleaned.lower().split() if word not in stoplist]  # turning each word into an item in a list
    return texts

class MLStripper(HTMLParser):
    """
    A class for stripping HTML tags from a string
    """
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def create_lda():
    """
    Runs all posts through an LDA topic model, to determine the basic topic of the post.
    http://chrisstrelioff.ws/sandbox/2014/11/13/getting_started_with_latent_dirichlet_allocation_in_python.html
    http://radimrehurek.com/topic_modeling_tutorial/2%20-%20Topic%20Modeling.html
    :return: LDA model built from existing documents
    """
    print("Creating LDA topic model from " + str(len(list_sentences)) + " documents.")
    num_topics = utils.NUM_LDA_TOPICS
    chunk_size = int(len(list_sentences)/100)
    if chunk_size < 1:
        chunk_size = 1  # small number of sentences

    all_tokens = sum(list_sentences, [])
    # process our stop words like all our words have been processed
    tokens_stop = []
    for word in get_stop_words('en'):
        tokens_stop.extend(clean_string(word))
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    # remove words that appear only once or are stop words
    texts = [[word for word in sentence if word not in tokens_once and word not in tokens_stop]
        for sentence in list_sentences]

    # constructing topic model
    dict_lda = corpora.Dictionary(texts)
    mm_corpus = [dict_lda.doc2bow(text) for text in texts]
    lda = models.ldamodel.LdaModel(corpus=mm_corpus, id2word=dict_lda, num_topics=num_topics, update_every=1, chunksize=chunk_size, passes=1)

    print("Done creating LDA topic model")

    # get list of lda topic names
    lda = create_lda()
    print(utils.FORMAT_LINE)
    # printing each topic
    for topic in lda.print_topics(utils.NUM_LDA_TOPICS):
        print(topic)
    print("\n")
    # naming each topic
    topic_names = []
    for topic in lda.print_topics(utils.NUM_LDA_TOPICS):
        topic_names.append(input("> A name for this topic: " + topic + ": "))
    print(utils.FORMAT_LINE)

    # predict topic for each document
    for doc in list_sentences:
        lda_vector = lda[dict_lda.doc2bow(doc)]
        print(max(lda_vector, key=lambda item: item[1])[0])
        # print(lda.print_topic(max(lda_vector, key=lambda item: item[1])[0]))  # prints the most prominent LDA topic
    return lda

'''
So that logfileMOOC can act as either a reusable module, or as a standalone program.
'''
if __name__ == '__main__':
    print("Running logfileMOOC")
    run()