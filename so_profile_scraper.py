print "Don't use this, use the StackOverflow data dump instead!"
print " http://blog.stackoverflow.com/2009/06/stack-overflow-creative-commons-data-dump/ "
import sys;sys.exit(1)

# Original script:

import urllib
from BeautifulSoup import BeautifulSoup as bs

class NameNotFound(Exception):pass

profile_url = "http://beta.stackoverflow.com/users/%s"
total_data_count = 0

def getsoupsrc(url):
    global total_data_count
    
    con = urllib.urlopen(url)
    src = con.read()
    total_data_count += len(src)
    soup = bs(src)
    return soup

def parse_userid(id):
    soup = getsoupsrc(profile_url % x)
    uinfo = soup.findAll("table", {'class':'user-details'})[0]
    
    parsed_info = {}
    
    for col in uinfo:
        try:
            item_name = col.next.td.contents[0]
            key = unicode(item_name).strip()
            val = unicode(item_name.findNext().contents[0]).strip()
            parsed_info[key] = val
        except Exception, errormsg:
            pass
    
    rep = unicode(
        soup.findAll('div', {'class':"summarycount"})[0].contents[0]
    ).strip().replace(",", "")

    parsed_info['Rep'] = int(rep)
    
    parsed_info['id'] = id
    
    return parsed_info

from sqlite3 import dbapi2 as sqlite

class SoDB:
    def __init__(self):
        self.conn = sqlite.connect("so_userinfo.sqlite3")
        self.cursor = self.conn.cursor()
    
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
import sys
if len(sys.argv) > 1:
    print "Starting on", sys.argv[1]
    start_profile = int(sys.argv[1])
else:
    start_profile = 1

higher_profile = 21071

error_count = 0
for x in xrange(start_profile, higher_profile):
    try:
        print "Processing user", x
        info = parse_userid(x)
        db.add_user(info)
    except KeyboardInterrupt:
        print "Got keyboard interupt!"
        print "Currently on user id", x
        break
    except Exception, errormsg:
        error_count += 1
        print "Error on user", x
        print errormsg

print "Total data transfered: %03f KB" % (float(total_data_count) / 1024)
print "Total errors: %s" % (error_count)
