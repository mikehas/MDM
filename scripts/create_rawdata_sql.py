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

columns = ['SourceID', 'ProviderType', 'Name', 'Gender', 'DateOfBirth', 'isSoleProprietor', 'MailingStreet', 'MailingUnit', 'MailingCity', 'MailingRegion', 'MailingPostCode', 'MailingCounty', 'MailingCountry', 'PracticeStreet', 'PracticeUnit', 'PracticeCity', 'PracticeRegion', 'PracticePostCode', 'PracticeCounty', 'PracticeCountry', 'Phone', 'PrimarySpecialty', 'SecondarySpecialty']

sql_formatted_columns = '(' + ",".join("'{0}'".format(w) for w in columns) + ')'

lines = []
errors = []

# Arrays to hold column statistics
non_nulls = [0] * len(columns)
nulls = [0] * len(columns)
min_chars = [10000] * len(columns)
total_chars = [0] * len(columns)
max_chars = [0] * len(columns)

unique_chars = [0] * len(columns)
for i, col in enumerate(columns): 
  unique_chars[i] = dict()

for j, row in enumerate(reader):
  if len(row) != len(columns):
    errors.append("ERROR: Line " + str(j) + " incorrect number of elements (length=" + str(len(row)) )
  for i, item in enumerate(row):
    row[i] = item.strip()
    if item == '':
       row[i] = 'NULL'
       nulls[i] = nulls[i] + 1
    else:
       non_nulls[i] = non_nulls[i] + 1
       row[i] = "\"" + row[i] + "\""
       max_chars[i] = len(row[i]) if len(row[i]) > max_chars[i] else max_chars[i]
       min_chars[i] = len(row[i]) if len(row[i]) < min_chars[i] else min_chars[i]
       total_chars[i] = total_chars[i] + len(row[i])
       for c in row[i]:
	 if c in unique_chars[i]:
           unique_chars[i][c] = unique_chars[i][c] + 1; 
         else:
           unique_chars[i][c] = 1;

  lines.append("INSERT INTO " + tablename + " " + sql_formatted_columns + " VALUES (" + ",".join(row) + ");")

outfile.write("\n".join(lines))

if len(errors) > 0:
  print("\n".join(errors))

padding = 18
print "COLUMN STATISTICS\n"
print(" " * (padding) + "\tNULL \tN_NULL \tMIN \tMAX \tAVG \t UNIQUE_CHARS\n")

for i, col in enumerate(columns):
  avg = 0 if non_nulls[i] == 0 else total_chars[i] / non_nulls[i]
  min = 0 if min_chars[i] == 10000 else min_chars[i]
  chars = []
  for key, val in unique_chars[i].iteritems():
    chars.append(key)
  chars.sort()    
  chars = ''.join(chars)

  print(columns[i] + " " * (padding - len(columns[i])) + "\t" + str(nulls[i]) + "\t" + str(non_nulls[i]) + "\t" + str(min) + "\t" + str(max_chars[i]) + "\t" + str(avg) + "\t" + str(chars))

print "\nDone\n"
