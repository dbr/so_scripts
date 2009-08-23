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
        # using nobody_'s sqlite database,
        # from http://meta.stackoverflow.com/questions/7682
        self.conn = sqlite.connect("so-export-sqlite-2009-06.db")
        self.cursor = self.conn.cursor()
    
    def __enter__(self):
        self._getAllItems()
        for x in self.cursor:
            yield x
        self.cursor.close()
    
    def __exit__(self, *exc_info):
        pass
    
    def _getAllItems(self):
        query = """SELECT age, reputation FROM users
        WHERE age != ""
        """
        self.cursor.execute(query)


def avg(x):
    return sum(x) / len(x)

def main():
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

    for age, info in countula.items():
        countula[age]['rep_avg'] = int(avg(info['rep_all']))

    # setup the chart
    chart = pygooglechart.SimpleLineChart(500, 400)

    age_min = 1
    age_max = 61

    # force the data into a graphable state
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

    outy = [cd[x] for x in xrange(age_min, age_max)]

    # Add the labels, grids etc to the chart
    chart.set_axis_labels(pygooglechart.Axis.BOTTOM, xrange(age_min,age_max, 5))
    chart.set_axis_labels(pygooglechart.Axis.LEFT, xrange(0,max(all_rep), max(all_rep) / 10))
    chart.grid = 10
    chart.title = "Stackoverflow.com%20:%20Age%20vs%20Reputation"

    # Add the data to the chart
    chart.add_data(outy)

    # And get the google charts URL
    print chart.get_url()

if __name__ == '__main__':
    main()