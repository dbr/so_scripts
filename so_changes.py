#!/usr/bin/python
"""
Some improvements to Will's script from..
http://stackoverflow.com/questions/6936/using-what-ive-learned-from-stackoverflow-html-scraper

Tracks changes in your reputation, showing which questions/answers account for each point.
"""
from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite
import re, os, sys, time, urllib
from optparse import OptionParser

p = OptionParser()
p.add_option("-u", "--user", type="int", default=745, help="Your user id", dest="user")
opts, args = p.parse_args()

stTime = time.strftime("%Y-%m-%d %H:%M:%S")
print stTime

questLen = 60 #digits before elipses kick in
connection = sqlite.connect('dbr_stackoverflow.sqlite3')
cursor = connection.cursor()

profile = urllib.urlopen(
    'http://stackoverflow.com/users/%i/myProfile.html' % (opts.user)
).read()

rep = re.compile('summarycount">.*?([,\d]+)</div>.*?Reputation', re.S).search(profile).group(1)
rep = rep.replace(",","")

badge = re.compile('iv class="summarycount".{10,60} (\d+)</d.{10,140}Badges', re.S).search(profile).group(1)
stQuestion = re.compile('Questions</h.*?Answers</h', re.S).search(profile).group()
stAnswer = re.compile('Answers</h.*?</table>', re.S).search(profile).group()
mQuestion = re.compile('question-summary narrow.*?vote-count-post"><strong.*?>(-?\d*).*?/questions/(\d*).*?>(.*?)</a>', re.S).findall(stQuestion)
mAnswer   = re.compile('(answer-summary"><a href="/questions/(\d*).*?votes.*?>(-?\d+).*?href.*?>(.*?)<.a)', re.S).findall(stAnswer)

print "\nQuestions:"
for quest in mQuestion:
    cursor.execute(
        "SELECT count(id), votes FROM Questions WHERE id = ? AND type=0;",
        (quest[1], )
    )
    item = cursor.fetchone()
    if item[0] > 0:
        lastQ = (int(quest[0]) - item[1])
        if lastQ==0:lastQ=""
        cursor.execute(
            'UPDATE Questions SET votes = ? WHERE id = ? AND type = 0',
            (quest[0], quest[1])
        )
    else:
        cursor.execute(
            'INSERT INTO Questions VALUES(?,?,0,?);',
            (quest[2], quest[0], quest[1])
        )
        lastQ = "(NEW)"
    if len(quest[2]) > questLen:
        elips="..." #in case the question is really long
        nElips = 0
    else:
        elips=""
        nElips = 3
    print '%s%s %s%s' % (quest[2][:questLen].ljust(questLen+nElips," "),elips, ("("+str(quest[0])+")").ljust(5," "), lastQ)

print "\nAnswers:" + str(len(mAnswer))
for answer in mAnswer:
    aId = answer[1]
    aVotes = answer[2]
    aQuestion = answer[3]

    cursor.execute(
        'SELECT count(id), votes FROM Questions WHERE id = ? AND type=1;',
        (aId, )
    )
    item = cursor.fetchone()
    if item[0] > 0:
        lastQ = int(aVotes) - item[1]
        if lastQ==0:lastQ=""
        cursor.execute('UPDATE Questions SET votes = %s WHERE id = %s AND type = 1' % (aVotes, aId))
    else:
        cursor.execute('INSERT INTO Questions VALUES("'+aQuestion+'",'+aVotes+',1,'+aId+');')
        lastQ = "(NEW)"
    if len(aQuestion) > questLen:
        elips="..."
        nElips = 0
    else:
        elips=""
        nElips = 3
    print '%s%s %s%s' % (aQuestion[:questLen].ljust(questLen+nElips," "),elips, ("("+str(aVotes)+")").ljust(5," "), lastQ)

cursor.execute('SELECT rep, badges, questions, answers , COUNT(date) FROM profile WHERE user = ' + str(opts.user) + ' ORDER BY date DESC;')
oldData = cursor.fetchone()
if oldData[4] == 0:
    oldData = [0,0,0,0]

cursor.execute("INSERT INTO profile VALUES(?,?,?,?,?,?);",
    (rep,badge,len(mQuestion),len(mAnswer),stTime, opts.user))

print
print '%s Questions, %s new' % (len(mQuestion),(len(mQuestion) - oldData[2]))
print '%s Answers, %s new' % (len(mAnswer),(len(mAnswer) - oldData[3]))
print '%s Reputation (%+i)' % (rep, (int(rep) - oldData[0]))
print '%s Badges, %s new' % (badge, (int(badge) - oldData[1]))
connection.commit()


#the below is incase you want to make your own database file
##CREATE TABLE "main"."Questions" (
##    "Question" TEXT,
##    "votes" INTEGER,
##    "type" INTEGER,
##    "id" INTEGER
##);

##CREATE TABLE "main"."profile" (
##    "rep" INTEGER,
##    "badges" INTEGER,
##    "questions" INTEGER,
##    "answers" INTEGER,
##    "date" TEXT,
##    "user" INTEGER
##);
