#!/usr/bin/env python

__author__ = 'IH'
__project__ = 'processMOOC'

import utilsMOOC as utils
import sys
import fileinput
import copy
import datetime
from collections import defaultdict
from QHInstance import QHInstance

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
BADGE_NONE = "http://erebor.lti.cs.cmu.edu/quickhelper/badges/blank.png"
BADGE_NONE2 = "http://i62.tinypic.com/2mgqut2.jpg"
BADGE_ONE = "http://erebor.lti.cs.cmu.edu/quickhelper/badges/helper1.png"
BADGE_ONE2 = "http://i61.tinypic.com/24q1jyr.jpg"
BADGE_TWO = "http://erebor.lti.cs.cmu.edu/quickhelper/badges/helper2.png"
BADGE_TWO2 = "http://i58.tinypic.com/29yjuww.jpg"
BADGE_THREE = "http://erebor.lti.cs.cmu.edu/quickhelper/badges/helper3.png"
BADGE_THREE2 = "http://i62.tinypic.com/214w7wl.jpg"
BADGE_FOUR = "http://erebor.lti.cs.cmu.edu/quickhelper/badges/helper4.png"
BADGE_FOUR2 = "http://i58.tinypic.com/2cgymgh.jpg"

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
list_no_dups_helpers = []  # a list of all helper instances with duplicates removed

# TODO: command line input for column delimiters, dates, filenames, etc.

'''
run function - calls the functions that do the processing for each kind of file
user.log is processed first and then written to file at the end
'''
def run():
    # Process of files
    proc_user()
    proc_selection()
    proc_helper()
    proc_vote()
    proc_click()

    remove_duplicates()  # remove duplicates from user.log and helper.log

    # user.log must be written at the end, because we need info from select.log
    file_out = open(FILENAME_USERLOG+EXTENSION_PROCESSED,'w')
    file_out.write(QHInstance.get_headers(delimiter=CONST_DELIMITER)+'\n')
    for qh_instance in list_no_duplicates:
        # set the selected number of helpers for each instance
        setattr(qh_instance, 'num_helpers_selected', dict_num_helpers.get(getattr(qh_instance, 'instance_id'), 0))
        line = qh_instance.to_string(delimiter=CONST_DELIMITER)
        file_out.write(line+'\n')
    file_out.close()
    print("Number of repeats in "+FILENAME_USERLOG+EXTENSION_LOGFILE+": "+str(count_repeat)+"\n")
    print("Done writing " + FILENAME_USERLOG+EXTENSION_LOGFILE+"\n")

    # helper.log written at end so as to only remove duplicates once
    file_out = open(FILENAME_HELPERLOG+EXTENSION_PROCESSED, 'w')
    file_out.write(utils.COL_HELPERID+CONST_DELIMITER+utils.COL_INSTANCEID+CONST_DELIMITER+utils.COL_NUMSTARS+CONST_DELIMITER+utils.COL_PREVHELPREQ+CONST_DELIMITER+utils.COL_NUMWEEKS+CONST_DELIMITER+utils.COL_TOPICMATCH+CONST_DELIMITER+utils.COL_RELSENTENCE+CONST_DELIMITER+utils.COL_IRRELSENTENCE+CONST_DELIMITER+utils.COL_DATE+CONST_DELIMITER+utils.COL_TIME + CONST_DELIMITER + utils.COL_WASSELECTED + CONST_DELIMITER + utils.COL_BADGE+ CONST_DELIMITER + utils.COL_IRRELEVANT + CONST_DELIMITER + utils.COL_VOTING + CONST_DELIMITER + utils.COL_USERNAME+"\n")
    # iterate through our list of helper instances without duplicates
    for h_line in list_no_dups_helpers:
        file_out.write(h_line + '\n')
    file_out.close()
    print("Done writing " + FILENAME_HELPERLOG+EXTENSION_LOGFILE+"\n")

'''
A line in the Userfile Log represents what user-level variables the user saw (specific information about individual helpers
shown is stored in the Helperfile Log).
ex: {"level":"info","message":"<DELIMITER>100<DELIMITER>1413061797181100<DELIMITER>1<DELIMITER>0<DELIMITER>1<DELIMITER>1<DELIMITER>0<DELIMITER>1833503<DELIMITER>2512601<DELIMITER>1657199<DELIMITER>title1<DELIMITER>body1<DELIMITER>","timestamp":"2014-10-11T21:09:57.182Z"}
Help Seeker User ID, Instance ID, Badge Shown?, Irrelevant Sentence Shown?, Voting Shown?, Anonymized Image Shown?, User ID Shown?, helper0, helper1, helper2, Question title, Question body
'''
def proc_user():
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
            col_date = get_date(array_line[len(array_line) - 1])  # We know the last column is always a timestamp
            col_time = get_time(array_line[len(array_line) - 1])

            #  it has an extra column for a URL
            col_url = ""
            if len(array_line) > 13:
                col_url = array_line[12]
            # if the helper IDs are greater than the minimum, this is likely a TA version instance
            col_version = utils.CONST_TA
            if (int(col_helper0) > utils.CONST_MIN_USERID or int(col_helper1) > utils.CONST_MIN_USERID or int(col_helper2) > utils.CONST_MIN_USERID):
                col_version = utils.CONST_STUDENT

            # Create QHInstance
            user_instance = QHInstance(col_user_id, col_instance_id, col_version, col_badge_shown, col_irrelevant_sentence, col_voting, col_anon_img, col_userid_shown,col_helper0, col_helper1, col_helper2, col_ques_title, col_ques_body, col_url, col_date, col_time)


            # keeping track of instances for printing late (if in correct date range)
            # store instance if it's during the right time period
            # AND if it's not one of the researchers' actions
            # AND only if the message body is longer than __ characters.
            if is_during_course(col_date) and not is_researcher(col_user_id) and len(col_ques_body) > 10:
                if not instances_by_dupkey.get(user_instance.get_duplicate_key(), False):  # This is a new instance
                    print("New instance: " + user_instance.get_duplicate_key())
                else:
                    print("Old instance: " + user_instance.get_duplicate_key())
                instances_by_dupkey[user_instance.get_duplicate_key()].append(user_instance)
                # TODO: Because we're using a dict here, we lose all timestamp ordering

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

'''
A line in the Helperfile Log represents all the information specific to the helper that the user saw.
{"level":"info","message":"<DELIMITER>1<DELIMITER>1413061797181100<DELIMITER>8<DELIMITER>http://i58.tinypic.com/2cgymgh.jpg<DELIMITER>3<DELIMITER>This student has been participating in the course for 1 weeks and the matching of his/her interest and the topic of your query is 100.0 .<DELIMITER>","timestamp":"2014-10-11T21:09:57.182Z"}
'''
def proc_helper():
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
            col_date = get_date(array_line[len(array_line) - 1])  # We know the last column is always a timestamp
            col_time = get_time(array_line[len(array_line) - 1])

            # Constructing the new helper logfile line
            line = col_helper_id + CONST_DELIMITER + col_instance_id + CONST_DELIMITER
            line += col_badge_shown + CONST_DELIMITER + col4 + CONST_DELIMITER + col_num_weeks + CONST_DELIMITER
            line += col_topic_match + CONST_DELIMITER + col_rec_sentence + CONST_DELIMITER + col_irrel_sentence + CONST_DELIMITER
            line += col_date + CONST_DELIMITER + col_time

            # determine if this helper was selected
            was_selected = 0
            if col_instance_id not in dict_helpers:  # that instance didn't occur in user.log
                print("WARNING: instanceID in "+FILENAME_HELPERLOG+EXTENSION_LOGFILE+" not found in " + FILENAME_USERLOG+EXTENSION_LOGFILE+", not writing to file: " + col_instance_id)
            elif col_helper_id in dict_selected_helpers[col_instance_id]:  # this ID was selected in selection.log
                was_selected = 1
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

'''
A line in the Helperfile Log represents one (of three maximum) of the helpers selected by user
{"level":"info","message":"<DELIMITER>11<DELIMITER>0<DELIMITER>","timestamp":"2014-10-11T21:09:57.211Z"}
'''
def proc_selection():
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
            col_date = get_date(array_line[len(array_line) - 1])  # We know the last column is always a timestamp
            col_time = get_time(array_line[len(array_line) - 1])

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
            line += CONST_DELIMITER + col_date + CONST_DELIMITER + col_time

            # only write line if it's in our date range
            if is_during_course(col_date):
                file_out.write(line+'\n')

    print("Done processing "+FILENAME_SELECTIONLOG+EXTENSION_LOGFILE+"\n")
    file_out.close()

'''
A line in the Upvote Log represents each instance a Helper up or downvotes a QuickHelp request.
{"level":"info","message":"<DELIMITER>2231948<DELIMITER>1<DELIMITER>1<DELIMITER>","timestamp":"2014-10-11T06:05:13.668Z"}
'''
def proc_vote():
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
            col_date = get_date(array_line[len(array_line) - 1])  # We know the last column is always a timestamp
            col_time = get_time(array_line[len(array_line) - 1])

            # Constructing the new vote logfile line
            line = col_helper_id + CONST_DELIMITER + col_instance_id + CONST_DELIMITER + col_vote + CONST_DELIMITER
            line += col_date + CONST_DELIMITER + col_time

            # only write line if it's in our date range
            if is_during_course(col_date):
                file_out.write(line+'\n')
            #print(line)
    print("Done processing "+FILENAME_VOTELOG+EXTENSION_LOGFILE+"\n")
    file_out.close()

'''
A line in the Click Log represents each instance a Helper up or downvotes a QuickHelp request.
{"level":"info","message":"<DELIMITER><i>helper_id</i><DELIMITER><i>instance_id</i><DELIMITER>https://www.edx.org//courses/UTArlingtonX/LINK5.10x/3T2014/discussion/forum/8d9482b366ae4999b706b2d7372d8393/threads/54808da7a2a525e05300156b<DELIMITER>","timestamp":"2014-12-04T16:35:45.863Z"}
'''
def proc_click():
    print("Processing "+FILENAME_CLICKLOG+EXTENSION_LOGFILE)

    file_out = open(FILENAME_CLICKLOG+EXTENSION_PROCESSED,'w')
    file_out.write(utils.COL_HELPERID+CONST_DELIMITER+utils.COL_INSTANCEID+CONST_DELIMITER+utils.COL_DATE_SENT+CONST_DELIMITER+utils.COL_TIME_SENT+CONST_DELIMITER+utils.COL_DATE_CLICKED+CONST_DELIMITER+utils.COL_TIME_CLICKED+CONST_DELIMITER+CONST_DELIMITER+utils.COL_QTITLE+CONST_DELIMITER+utils.COL_QBODY+CONST_DELIMITER+utils.COL_URL+"\n")

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
            col_date_clicked = get_date(array_line[len(array_line) - 1])  # We know the last column is always a timestamp
            col_time_clicked = get_time(array_line[len(array_line) - 1])

            # Retrieving timestamp when URL was sent
            col_date_sent = ""
            col_time_sent = ""
            qtitle = ""
            qbody = ""
            if col_instance_id in instances_by_id:  # instance id might be 'instance_id'
                col_date_sent = getattr(instances_by_id[col_instance_id], 'date')
                col_time_sent = getattr(instances_by_id[col_instance_id], 'time')
                qtitle = getattr(instances_by_id[col_instance_id], 'question_title')
                qbody = getattr(instances_by_id[col_instance_id], 'question_body')
            else:
                print("WARNING: Encountered instance ID in " + FILENAME_CLICKLOG+EXTENSION_LOGFILE+" that is not in " + FILENAME_USERLOG+EXTENSION_LOGFILE+": " + col_instance_id)

            # Constructing the new vote logfile line
            line = col_helper_id + CONST_DELIMITER + col_instance_id + CONST_DELIMITER + col_instance_id + CONST_DELIMITER
            line += col_date_sent + CONST_DELIMITER + col_time_sent + CONST_DELIMITER + col_date_clicked + CONST_DELIMITER
            line += col_time_clicked + CONST_DELIMITER + qtitle + CONST_DELIMITER + qbody + CONST_DELIMITER + col_url

            # only write line if the email with URL was sent in our date range
            if col_instance_id in instances_by_id and is_during_course(col_date_sent):
                file_out.write(line+'\n')
                # TODO: there's duplicates in the click logs from clicking several times that need to be removed
            #print(line)
    print("Done processing "+FILENAME_CLICKLOG+EXTENSION_LOGFILE+"\n")
    file_out.close()

'''
 Removes duplicates from our list of instances, based on whatever key was used in duplicate_instances
 Also removes duplicates from our helper logs
'''
def remove_duplicates():
    for duplicate_key in instances_by_dupkey:  # iterate through each key in our duplicate-arranged list
        selected_dup = None  # instance with a selection (the one shown)
        for dup in instances_by_dupkey[duplicate_key]:  # for each instance object in these duplicates
            if getattr(dup, utils.COL_NUMHELPERS, 0) > 0:  # If it has helpers selected, it's the one
                selected_dup = dup
        if selected_dup is None:
                selected_dup = create_new_duplicate(instances_by_dupkey[duplicate_key])  # Clear out non-matching condition variables
        list_no_duplicates.append(selected_dup)  # Record selected_dup as our correct one
        list_no_dups_helpers.extend(dict_all_helpers[getattr(selected_dup, 'instance_id')])  # Record the 3 helper lines for our one selected instance

        if len(instances_by_dupkey[duplicate_key]) > 1:  # if we have more than one value attached to this key, they're duplicates
            global count_repeat
            count_repeat += len(instances_by_dupkey[duplicate_key])-1
    return list_no_duplicates

'''
 Given a list of duplicates, return a QHInstance that only has entries for columns
 that have identical values for all items in the list (i.e. "isBadgeShown" is 0 for all instances, etc)
'''
def create_new_duplicate(duplicates):
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

'''
Determine if given date is within the range of dates the course took place
'''
def is_during_course(instance_date):
    if len(instance_date) == 10:
        array_date = instance_date.split("-")
        date_converted = datetime.date(int(array_date[0]), int(array_date[1]), int(array_date[2]))
        if CONST_LAST_DAY >= date_converted >= CONST_FIRST_DAY:
            return True
        else:  # Not in given course date range
            return False
    else:
        print("ERROR:: logfileMOOC.is_during_course(): Cannot process date column: " + instance_date)
        return False
'''
Determine if given user is one of the researchers
'''
def is_researcher(userID):
    if int(userID) < 0 or int(userID) in utils.exclude_ids: # TAs and researchers had userIDs less than 0
        return True
    else: # Not a researcher!
        return False

'''
Gets the date from a messy timestamp in the logfiles
'''
def get_date(tstamp):
    tstamp = tstamp[tstamp.index(':')+1: (len(tstamp)-2)].replace("\"",'')
    return tstamp[0:tstamp.find("T")]

'''
Gets the time from a messy timestamp in the logfiles
'''
def get_time(tstamp):
    tstamp = tstamp[tstamp.index(':')+1: (len(tstamp)-2)].replace("\"",'')
    return tstamp[tstamp.find("T")+1: len(tstamp)-1]

'''
Determines how many stars were on the badge, depending on badge URL
'''
def get_badge_stars(url):
    if url == BADGE_NONE or url == BADGE_NONE2:
        return BADGE_NONE_TXT
    elif url == BADGE_ONE or url == BADGE_ONE2:
        return BADGE_ONE_TXT
    elif url == BADGE_TWO or url == BADGE_TWO2:
        return BADGE_TWO_TXT
    elif url == BADGE_THREE or url == BADGE_THREE2:
        return BADGE_THREE_TXT
    elif url == BADGE_FOUR or url == BADGE_FOUR2:
        return BADGE_FOUR_TXT
    else:
        print("ERROR:: logfileMOOC.get_badge_stars(): Missing badge ID: " + url)

'''
Finds what the topic match percentage was given the topic match sentence
'''
def get_topic_match(sentence):
    if sentence.find("Teaching Assistants") >= 0:
        return "TA"
    else:
        tm = sentence[len(sentence)-7:len(sentence)-1]
        tm = float(tm.strip("abcdefghijklmnopqrstuvwxyz% "))
        if tm < 1:
            tm = tm*100
        return str(tm)

'''
Finds how many weeks the helper's been around, given the topic match sentence
'''
def get_num_weeks(sentence):
    if sentence.find("Teaching Assistants") >= 0:
        return "TA"
    else:
        return sentence[sentence.find("week")-2: sentence.find("week")]

'''
So that logfileMOOC can act as either a reusable module, or as a standalone program.
'''
if __name__ == '__main__':
    run()