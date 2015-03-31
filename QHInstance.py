__author__ = 'IH'
__project__ = 'processMOOC'

import utilsMOOC as utils

class QHInstance(object):
    ' A line in the Userfile Log represents what user-level variables the user saw (specific information about individual helpers shown is stored in the Helperfile Log).'
    # ex: {"level":"info","message":"<DELIMITER>100<DELIMITER>1413061797181100<DELIMITER>1<DELIMITER>0<DELIMITER>1<DELIMITER>1<DELIMITER>0<DELIMITER>1833503<DELIMITER>2512601<DELIMITER>1657199<DELIMITER>title1<DELIMITER>body1<DELIMITER>","timestamp":"2014-10-11T21:09:57.182Z"}
    # Help Seeker User ID, Instance ID, Badge Shown?, Irrelevant Sentence Shown?, Voting Shown?, Anonymized Image Shown?, User ID Shown?, helper0, helper1, helper2, Question title, Question body
    user_id = "-1"
    instance_id = "-1"
    cond_badge = "-1"
    cond_irrelevant_sentence = "-1"
    cond_voting = "-1"
    cond_anon_id = "-1"
    cond_user_id = "-1"
    id_helper0 = "-1"
    id_helper1 = "-1"
    id_helper2 = "-1"
    question_title = "-1"
    question_body = "-1"
    num_helpers_selected = 0
    date = "-1"
    time = "-1"
    url = ""

    def __init__(self, uid, iid, cb, cis, cv, cai, cui, h0, h1, h2, qt, qb, d, t):
        self.user_id = uid
        self.instance_id = iid
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
        self.date = d
        self.time = t

    '''
    Duplicates have the same author, question title, and date
    '''
    def is_duplicate(self,compare_to):
        if self.user_id == compare_to.user_id and self.question_title == compare_to.question_title and self.date == compare_to.date:
            return True
        return False

    '''
    Returns an 'ID' that is the same as its duplicates
    '''
    def get_duplicate_key(self):
        return self.cond_user_id+self.question_title+self.date

    def get_headers(delimiter):
        return utils.COL_USERID + delimiter + utils.COL_INSTANCEID + delimiter + utils.COL_BADGE + delimiter + utils.COL_IRRELEVANT + delimiter + utils.COL_VOTING + delimiter + utils.COL_ANONIMG + delimiter + utils.COL_USERNAME + delimiter + utils.COL_HELPER0 + delimiter + utils.COL_HELPER1 + delimiter + utils.COL_HELPER2 + delimiter + utils.COL_NUMHELPERS + delimiter + utils.COL_QTITLE + delimiter + utils.COL_QBODY + delimiter + utils.COL_URL + delimiter +utils.COL_DATE + delimiter + utils.COL_TIME

    def to_string(self, delimiter):
        return self.user_id + delimiter + self.instance_id + delimiter + self.cond_badge + delimiter + self.cond_irrelevant_sentence + delimiter + self.cond_voting + delimiter + self.cond_anon_img + delimiter + self.cond_user_id + delimiter + self.id_helper0 + delimiter + self.id_helper1 + delimiter + self.id_helper2 + delimiter + str(self.num_helpers_selected) + delimiter + self.question_title + delimiter + self.question_body + delimiter + self.url + delimiter +self.date + delimiter + self.time