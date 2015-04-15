# mooc-file-processing
This project represents a Python script for processing several logfiles from a Massive Open Online Course.
There were (1) various errors in the logging software (i.e., mysterious duplicates whose instance IDs were different, extra columns on some lines with a URL), (2) general cleaning (i.e., removing test entries, removing entries from our researchers, removing entries outside the course date range), and (3) more complicated post-processing that was necessary (i.e., cross-referencing values from one logfile into another). The code goes two steps further and also assigns an LDA topic to each discussion forum post and runs some basic statistics using pandas.

## running
The main scripts are **logfileMOOC.py** and **statsMOOC.py**. Run logfile first, then stats. If you encounter errors you may want to check **utilsMOOC.py** to ensure all the constants are properly named.

## code
**logfileMOOC.py** processes the logfiles from their '.log' form to comma separated values file. Does all the cross referencing and counting so we can figure out (for instance) how many helpers a particular user selected in the selection.log.

**statsMOOC.py** reads in the processed files from logfileMOOC and does some basic statistics using pandas: descriptive statistics, plots, and a few linear models and ANOVA.

**utilsMOOC.py** a file of constants for running the main scripts (above): filenames, column headers, delimiters, etc. Meant to be modified by the user if any of these things change.

**topicModelLDA.py** an internal class for creating an LDA topic model and predicting the topic of future documents. Also contains a convenient method for cleaning unwanted characters from a string and turning it into a bag of words to be fed to the model.

**QHInstance.py** an internal class representing one usage of the QuickHelper system: the users involved, the conditions shown, the number of helpers selected, the message title and body text, etc.

## logfiles
- **User.log:** A line in the Userfile Log represents what user-level variables the user saw (specific information about individual helpers shown is stored in the Helperfile Log).
> ex: {"level":"info","message":"<DELIMITER>100<DELIMITER>1413061797181100<DELIMITER>1<DELIMITER>0<DELIMITER>1<DELIMITER>1<DELIMITER>0<DELIMITER>1833503<DELIMITER>2512601<DELIMITER>1657199<DELIMITER>title1<DELIMITER>body1<DELIMITER>","timestamp":"2014-10-11T21:09:57.182Z"}
> ex: Help Seeker User ID, Instance ID, Badge Shown?, Irrelevant Sentence Shown?, Voting Shown?, Anonymized Image Shown?, User ID Shown?, helper0, helper1, helper2, Question title, Question body
- **Selection.log:** A line in the Helperfile Log represents one (of three maximum) of the helpers selected by user
> ex: {"level":"info","message":"<DELIMITER>11<DELIMITER>0<DELIMITER>","timestamp":"2014-10-11T21:09:57.211Z"}
- **Helper.log:** A line in the Helperfile Log represents all the information specific to the helper that the user saw.
> ex: {"level":"info","message":"<DELIMITER>1<DELIMITER>1413061797181100<DELIMITER>8<DELIMITER>http://i58.tinypic.com/2cgymgh.jpg<DELIMITER>3<DELIMITER>This student has been participating in the course for 1 weeks and the matching of his/her interest and the topic of your query is 100.0 .<DELIMITER>","timestamp":"2014-10-11T21:09:57.182Z"}
- **Vote.log:** A line in the Helperfile Log represents one (of three maximum) of the helpers selected by user
> ex: {"level":"info","message":"<DELIMITER>11<DELIMITER>0<DELIMITER>","timestamp":"2014-10-11T21:09:57.211Z"}

## other info
A description of the dataset and collection methods can be found here: www.irishowley.com/website/pMOOChelpers.html
An overview of logfile dependencies can be found here: www.irishowley.com/website/pMOOClogfiles.html

