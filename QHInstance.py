__author__ = 'IH'
__project__ = 'processMOOC'

import utilsMOOC as utils
import datetime
import copy

class QHInstance(object):
    ' A line in the Userfile Log represents what user-level variables the user saw (specific information about individual helpers shown is stored in the Helperfile Log).'
    # ex: {"level":"info","message":"<DELIMITER>100<DELIMITER>1413061797181100<DELIMITER>1<DELIMITER>0<DELIMITER>1<DELIMITER>1<DELIMITER>0<DELIMITER>1833503<DELIMITER>2512601<DELIMITER>1657199<DELIMITER>title1<DELIMITER>body1<DELIMITER>","timestamp":"2014-10-11T21:09:57.182Z"}
    # Help Seeker User ID, Instance ID, Badge Shown?, Irrelevant Sentence Shown?, Voting Shown?, Anonymized Image Shown?, User ID Shown?, helper0, helper1, helper2, Question title, Question body
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

    def __init__(self, uid, iid, cvers, cb, cis, cv, cai, cui, h0, h1, h2, qt, qb, u, ts):
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

    '''
     Overwriting the copy operator, probably not necessary as these are all primitive types
    '''
    def __copy__(self):
        new_instance = type(self)(self.user_id, self.instance_id, self.version, self.cond_badge, self.cond_irrelevant_sentence, self.cond_voting, self.cond_anon_img, self.cond_user_id, self.id_helper0, self.id_helper1, self.id_helper2, self.question_title, self.question_body,self.url, self.timestamp)
        setattr(new_instance, 'version', self.version)
        setattr(new_instance, 'num_helpers_selected', self.num_helpers_selected)
        return new_instance

    '''
    Duplicates have the same author, question title, and date
    '''
    def is_duplicate(self,compare_to):
        if self.user_id == compare_to.user_id and self.question_title == compare_to.question_title and self.timestamp.date() == compare_to.timestamp.date():
            return True
        return False

    '''
    Returns an 'ID' that is the same as its duplicates
    '''
    def get_duplicate_key(self):
        return self.user_id + self.question_title + str(self.timestamp.date())

    def get_headers(delimiter):
        return utils.COL_USERID + delimiter + utils.COL_INSTANCEID + delimiter + utils.COL_VERSION + delimiter + utils.COL_BADGE + delimiter + utils.COL_IRRELEVANT + delimiter + utils.COL_VOTING + delimiter + utils.COL_ANONIMG + delimiter + utils.COL_USERNAME + delimiter + utils.COL_HELPER0 + delimiter + utils.COL_HELPER1 + delimiter + utils.COL_HELPER2 + delimiter + utils.COL_NUMHELPERS + delimiter + utils.COL_QTITLE + delimiter + utils.COL_QBODY + delimiter + utils.COL_URL + delimiter +utils.COL_DATE + delimiter + utils.COL_TIME

    def to_string(self, delimiter):
        line = str(self.user_id) + delimiter + str(self.instance_id) + delimiter + str(self.version) + delimiter
        line += str(self.cond_badge) + delimiter + str(self.cond_irrelevant_sentence) + delimiter + str(self.cond_voting)
        line += delimiter + str(self.cond_anon_img) + delimiter + str(self.cond_user_id) + delimiter + str(self.id_helper0)
        line += delimiter + str(self.id_helper1) + delimiter + str(self.id_helper2) + delimiter + str(self.num_helpers_selected)
        line += delimiter + self.question_title + delimiter + self.question_body + delimiter + self.url + delimiter
        line += str(self.timestamp.date()) + delimiter + str(self.timestamp.time())
        return line

