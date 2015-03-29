__author__ = 'IH'
__project__ = 'processDALMOOC'

class QuickHelperInstance(object):
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

    def get_headers(delimiter):
        return "UserID" + delimiter + "InstanceID" + delimiter + "isBadgeCondition" + delimiter + "isIrrelevantSentence" + delimiter + "isVotingCondition" + delimiter + "isAnonymousImg" + delimiter + "isUsernameCondition" + delimiter + "helper0" + delimiter + "helper1" + delimiter + "helper2" + delimiter + "numHelpersSelected" + delimiter + "qTitle" + delimiter + "qBody" + delimiter + "date" + delimiter + "time"

    def to_string(self, delimiter):
        return self.user_id + delimiter + self.instance_id + delimiter + self.cond_badge + delimiter + self.cond_irrelevant_sentence + delimiter + self.cond_voting + delimiter + self.cond_anon_img + delimiter + self.cond_user_id + delimiter + self.id_helper0 + delimiter + self.id_helper1 + delimiter + self.id_helper2 + delimiter + str(self.num_helpers_selected) + delimiter + self.question_title + delimiter + self.question_body + delimiter + self.date + delimiter + self.time