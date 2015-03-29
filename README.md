# mooc-file-processing
This project represents a Python script for processing several logfiles from a Massive Open Online Course.
There were (1) various errors in the logging software (i.e., mysterious duplicates whose instance IDs were different, extra columns on some lines with a URL), (2) general cleaning that was necessary (i.e., removing test entries, removing entries from our researchers, removing entries outside the course date range), and (3) more complicated post-processing that was necessary (i.e., cross-referencing values from one logfile into another). 

To achieve analyzable logfiles, I learned some Python (i.e., this is my first project in Python).

The log-files that are processed include: 
(1) User.log
   A line in the Userfile Log represents what user-level variables the user saw (specific information about individual helpers
shown is stored in the Helperfile Log).
   ex: {"level":"info","message":"<DELIMITER>100<DELIMITER>1413061797181100<DELIMITER>1<DELIMITER>0<DELIMITER>1<DELIMITER>1<DELIMITER>0<DELIMITER>1833503<DELIMITER>2512601<DELIMITER>1657199<DELIMITER>title1<DELIMITER>body1<DELIMITER>","timestamp":"2014-10-11T21:09:57.182Z"}
Help Seeker User ID, Instance ID, Badge Shown?, Irrelevant Sentence Shown?, Voting Shown?, Anonymized Image Shown?, User ID Shown?, helper0, helper1, helper2, Question title, Question body
(2) Selection.log
   A line in the Helperfile Log represents one (of three maximum) of the helpers selected by user
   ex: {"level":"info","message":"<DELIMITER>11<DELIMITER>0<DELIMITER>","timestamp":"2014-10-11T21:09:57.211Z"}
(3) Helper.log
   A line in the Helperfile Log represents all the information specific to the helper that the user saw.
   ex: {"level":"info","message":"<DELIMITER>1<DELIMITER>1413061797181100<DELIMITER>8<DELIMITER>http://i58.tinypic.com/2cgymgh.jpg<DELIMITER>3<DELIMITER>This student has been participating in the course for 1 weeks and the matching of his/her interest and the topic of your query is 100.0 .<DELIMITER>","timestamp":"2014-10-11T21:09:57.182Z"}
(4) Vote.log
   A line in the Helperfile Log represents one (of three maximum) of the helpers selected by user
   ex: {"level":"info","message":"<DELIMITER>11<DELIMITER>0<DELIMITER>","timestamp":"2014-10-11T21:09:57.211Z"}

A description of the dataset and collection methods can be found here: www.irishowley.com/website/pMOOChelpers.html
An overview of logfile dependencies can be found here: www.irishowley.com/website/pMOOClogfiles.html

