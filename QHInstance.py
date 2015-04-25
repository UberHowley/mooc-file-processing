__author__ = 'IH'
__project__ = 'processMOOC'

import utilsMOOC as utils
import datetime
import copy

class QHInstance(object):
    """
    A line in the Userfile Log represents what user-level variables the user saw (specific information about individual helpers shown is stored in the Helperfile Log).
    ex: {"level":"info","message":"<DELIMITER>100<DELIMITER>1413061797181100<DELIMITER>1<DELIMITER>0<DELIMITER>1<DELIMITER>1<DELIMITER>0<DELIMITER>1833503<DELIMITER>2512601<DELIMITER>1657199<DELIMITER>title1<DELIMITER>body1<DELIMITER>","timestamp":"2014-10-11T21:09:57.182Z"}
    ex: Help Seeker User ID, Instance ID, Badge Shown?, Irrelevant Sentence Shown?, Voting Shown?, Anonymized Image Shown?, User ID Shown?, helper0, helper1, helper2, Question title, Question body
    """
    user_id = "-1"
    instance_id = ""
    version = ""
    cond_badge = ""
    cond_irrelevant_sentence = ""
    cond_voting = ""
    cond_anon_img = ""
    cond_user_id = ""
    id_helper0 = ""
    id_helper1 = ""
    id_helper2 = ""
    question_title = ""
    question_body = ""
    num_helpers_selected = 0
    timestamp = None
    url = ""
    lda_topic = ""
    is_help_topic = ""

    def __init__(self, uid, iid, cvers, cb, cis, cv, cai, cui, h0, h1, h2, qt, qb, u, ts, hr):
        """
        Initialize a new QHInstance with the necessary information
        :param uid: user id
        :param iid: instance id
        :param cvers: TA/student version
        :param cb: badge condition
        :param cis: irrelevant sentence condition
        :param cv: voting condition
        :param cai: anonymous image condition
        :param cui: anonymous user id condition
        :param h0: helper id at index 0
        :param h1: helper id at index 1
        :param h2: helper id at index 2
        :param qt: question/post title
        :param qb: question/post body
        :param u: url
        :param ts: timestamp
        :param hr: is help request
        :return: None
        """
        self.user_id = uid
        self.instance_id = iid
        self.version = cvers
        self.cond_badge = cb
        self.cond_irrelevant_sentence = cis
        self.cond_voting = cv
        self.cond_anon_img = cai
        self.cond_user_id = cui
        self.id_helper0 = h0
        self.id_helper1 = h1
        self.id_helper2 = h2
        self.question_title = qt
        self.question_body = qb
        self.url = u
        self.timestamp = ts
        self.is_help_topic = hr

    def __copy__(self):
        """
        Overwrite the copy operator (probably not necessary as these are all primitive types)
        :return: None
        """
        new_instance = type(self)(self.user_id, self.instance_id, self.version, self.cond_badge, self.cond_irrelevant_sentence, self.cond_voting, self.cond_anon_img, self.cond_user_id, self.id_helper0, self.id_helper1, self.id_helper2, self.question_title, self.question_body,self.url, self.timestamp, self.is_help_topic)
        setattr(new_instance, 'version', self.version)
        setattr(new_instance, 'num_helpers_selected', self.num_helpers_selected)
        return new_instance


    def is_duplicate(self, compare_to):
        """
        Determine if given instance is a duplicate
        :param compare_to: the QHInstance we're comparing against for similarity
        :return: True if the given item has the same duplicate key as self item
        """
        return self.get_duplicate_key == compare_to.get_duplicate_key()

    def get_duplicate_key(self):
        """
        Returns an 'ID' that is the same as its duplicates
        :return: a key that it shares with its duplicates
        """
        return self.user_id + self.question_title + str(self.timestamp.date())

    def get_headers(delimiter):
        """
        Retrieve column headers for a QHInstance object for printing
        :param delimiter: character to split each column header
        :return: None
        """
        return utils.COL_USERID + delimiter + utils.COL_INSTANCEID + delimiter + utils.COL_VERSION + delimiter + utils.COL_BADGE + delimiter + utils.COL_IRRELEVANT + delimiter + utils.COL_SENTENCE_TYPE + delimiter + utils.COL_VOTING + delimiter + utils.COL_ANONIMG + delimiter + utils.COL_USERNAME + delimiter + utils.COL_HELPER0 + delimiter + utils.COL_HELPER1 + delimiter + utils.COL_HELPER2 + delimiter + utils.COL_NUMHELPERS + delimiter + utils.COL_TOPIC + delimiter + utils.COL_HELP_TOPIC + delimiter + utils.COL_QTITLE + delimiter + utils.COL_QBODY + delimiter + utils.COL_URL + delimiter +utils.COL_DATE + delimiter + utils.COL_TIME

    def to_string(self, delimiter):
        """
        Create a string for printing this QHInstance, coordinating with the headers
        :param delimiter: character to split each column
        :return: a string for printing this QHInstance, coordinating with the headers
        """
        # want a second column that says exactly what kind of sentence type we're dealing with (rele, irrele, TA)
        sentence_type = self.cond_irrelevant_sentence
        if len(sentence_type) < 1:
            sentence_type = self.cond_irrelevant_sentence  # do nothing, it's a duplicate with non-matching conditions
        elif self.version is utils.CONST_TA:
            sentence_type = self.version
        elif self.version is utils.CONST_STUDENT and self.cond_irrelevant_sentence is utils.VAL_IS:
            sentence_type = "irrelevant"
        elif self.version is utils.CONST_STUDENT:
            sentence_type = "relevant"

        line = str(self.user_id) + delimiter + str(self.instance_id) + delimiter + str(self.version) + delimiter
        line += str(self.cond_badge) + delimiter + str(self.cond_irrelevant_sentence) + delimiter + sentence_type
        line += delimiter + str(self.cond_voting)
        line += delimiter + str(self.cond_anon_img) + delimiter + str(self.cond_user_id) + delimiter + str(self.id_helper0)
        line += delimiter + str(self.id_helper1) + delimiter + str(self.id_helper2) + delimiter + str(self.num_helpers_selected)
        line += delimiter + self.lda_topic + delimiter + str(self.is_help_topic) + delimiter
        line += self.question_title + delimiter + self.question_body + delimiter
        line += self.url + delimiter + str(self.timestamp.date()) + delimiter + str(self.timestamp.time())
        return line

