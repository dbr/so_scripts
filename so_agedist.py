#!/usr/bin/env python
"""
Uses the data scraped into so_userinfo.sqlite3 and makes
 a graph showing the distribution of age vs reputation.
"""
from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite

# easy_install pygooglechart
# or http://pygooglechart.slowchop.com/
import pygooglechart


class SoDB:
    def __init__(self):
        self.conn = sqlite.connect("so_userinfo.sqlite3")
        self.cursor = self.conn.cursor()
    
    def __enter__(self):
        self._getAllItems()
        for x in self.cursor:
            yield x
        self.cursor.close()
    
    def __exit__(self, *exc_info):
        pass
    
    def _getAllItems(self):
        query = """SELECT age, rep FROM Users
        WHERE age != ""
        """
        self.cursor.execute(query)
        
    def create_table(self):
        return False #OH NO YOU DON'T
        query = """CREATE TABLE "main"."Users" (
        "Website" TEXT,
        "Name" TEXT,
        "Age" TEXT,
        "Last seen" TEXT,
        "Location" TEXT,
        "Rep" INT,
        "Member for" TEXT,
        "id" INTEGER
        );
        """
        self.cursor.execute(query)
    
    def add_user(self, info):
        query = """INSERT INTO "main"."Users" (
            "Website", "Name", "Age", "Last seen", "Location", 
            "Rep", "Member for", "id"
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?
        );
        """
        self.cursor.execute(query, 
            (info['Website'], info['Name'],
            info['Age'], info['Last seen'],
            info['Location'], info['Rep'],
            info['Member for'], info['id'])
        )
        self.conn.commit()


db = SoDB()
countula = {}
with db as query:
    for row in query:
        age, rep = row
        if age in countula:
            countula[age]['total_rep'] += rep
            countula[age]['rep_all'].append(rep)
        else:
            countula[age] = {'total_rep':rep, 'rep_all':[rep]}

def avg(x):
    return sum(x) / len(x)

for age, info in countula.items():
    countula[age]['rep_avg'] = int(avg(info['rep_all']))


chart = pygooglechart.SimpleLineChart(500, 400)

age_min = 1
age_max = 61

cd = {}
all_rep = []
for x in xrange(age_min, age_max):
    cd[x] = 0
for age, info in countula.items():
    age = int(age)
    try:
        cd[age] = int(info['rep_avg'])
        all_rep.append(cd[age])
    except KeyError:
        print "Out of range value!"

chart.set_axis_labels(pygooglechart.Axis.BOTTOM, xrange(age_min,age_max, 5))
chart.set_axis_labels(pygooglechart.Axis.LEFT, xrange(0,max(all_rep), max(all_rep) / 10))
chart.grid = 10
chart.title = "Stackoverflow.com%20:%20Age%20vs%20Reputation"
outy = [cd[x] for x in xrange(age_min, age_max)]
chart.add_data(outy)
print chart.get_url()