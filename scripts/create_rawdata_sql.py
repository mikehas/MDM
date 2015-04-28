#! /usr/bin/env python

import os
import sys
import csv

if len(sys.argv) < 3:
  print "Usage " + sys.argv[0] + " <file.tsv> <output.sql>"
  print "e.g, (" + sys.argv[0] + " ../src/Providers.tsv RawData.sql"
  exit(1)

print "Starting\n"
f = open(sys.argv[1], 'rb')
f.readline()
reader = csv.reader(f, delimiter='\t')

outfile = open(sys.argv[2], 'w+')
tablename = sys.argv[2].split('.')[0]

columns = "(ProviderID, ProviderType, Name, Gender, DateOfBirth, isSoleProprietor, MailingStreet, MailingUnit, MailingCity, MailingRegion, MailingPostCode, MailingCounty, MailingCountry, PracticeStreet, PracticeUnit, PracticeCity, PracticeRegion, PracticePostCode, PracticeCounty, PracticeCountry, Phone, PrimarySpecialty, SecondarySpecialty)"

outfile.write("INSERT INTO " + tablename + " " + columns + "  VALUES\n")

lines = []

for row in reader:
  for i, item in enumerate(row):
    if item == '':
       row[i]= 'NULL'
    else:
       row[i] = "\"" + row[i] + "\""

  lines.append('(' + ",".join(row) + ')\n')

outfile.write(",".join(lines))

print "Done\n"
print "Note: You many need to increase the mysql server's max packet size in you my.cnf file to run to run the outputed sql file.\n"
print "\t[mysqld]\n\tmax_allowed_packet=16M\n"
