#! /usr/bin/env python

'''

MySQLdb Docs:
http://mysql-python.sourceforge.net/MySQLdb.html


'''
import os
import ConfigParser
import MySQLdb

home = os.path.expanduser("~")
mycnf = os.path.join(home, 'my.cnf')

conf = ConfigParser.ConfigParser()
conf.readfp(open(mycnf))

db = MySQLdb.connect(host = conf.get('mysql','host'),
                     user = conf.get('mysql','user'),
                     passwd = conf.get('mysql', 'password'),
                     db = conf.get('mysql', 'database'))

q_test = 'show tables'

cur = db.cursor()

print "\nBASIC STATEMENT EXAMPLE"

cur.execute(q_test)
for row in cur.fetchall():
  print row

print "\nPARAMETERIZED STATEMENT EXAMPLE"

campus = "California Polytechnic State University-San Luis Obispo"
q_select_all = "select * from campuses c where c.campus = %s"

cur.execute(q_select_all, (campus,))

for row in cur.fetchall():
   print row

