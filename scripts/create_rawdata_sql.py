#! /usr/bin/env python

import os
import sys
import csv
import json
import re

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

NAME_INDEX = 2

columns = ['SourceID', 'ProviderType', 'Name', 'Gender', 'DateOfBirth', 'isSoleProprietor', 'MailingStreet', 'MailingUnit', 'MailingCity', 'MailingRegion', 'MailingPostCode', 'MailingCounty', 'MailingCountry', 'PracticeStreet', 'PracticeUnit', 'PracticeCity', 'PracticeRegion', 'PracticePostCode', 'PracticeCounty', 'PracticeCountry', 'Phone', 'PrimarySpecialty', 'SecondarySpecialty']
column_is_int = [True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]

sql_formatted_columns = '(' + ",".join("{0}".format(w) for w in columns) + ')'

print "Loading census names..."
all_names = json.load(open("../src/names/all_names.json", "r"))
uncommon_names = json.load(open("../src/names/uncommon_names.json", "r"))
iranian_names = json.load(open("../src/names/iranian_names.json", "r"))
more_uncommon_names = json.load(open("../src/names/more_uncommon_names.json", "r"))
arabic_names = json.load(open("../src/names/arabic_names.json", "r"))

print "Creating statistics arrays"
lines = []
errors = []

# Arrays to hold column statistics
non_nulls = [0] * len(columns)
nulls = [0] * len(columns)
min_chars = [10000] * len(columns)
total_chars = [0] * len(columns)
max_chars = [0] * len(columns)

# Dictionary to hold unique characters
unique_chars = [0] * len(columns)
for i, col in enumerate(columns): 
  unique_chars[i] = dict()

# Dictionary to hold potential titles non-names
titles = dict()

def collect_titles(row):
  p = re.compile('[B-DF-HJ-NP-TV-XZ]{4,}')
  #q = re.compile('.*(SHK|ROJ|KALL|BUTT|AHAD|SKI|UND|PARE|ICH|RAK).*')
  row = row.upper()
  words = row.split()
  for w in words:
    if ( w not in all_names 
         and w not in uncommon_names 
         and w not in more_uncommon_names 
         and w not in iranian_names 
         and w not in arabic_names
         #and q.search(w) < 1
         and len(w) > 1
       ):
      if w not in titles:
        titles[w] = 1
      else:
        titles[w] = titles[w] + 1

print "Parsing file..."
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
       max_chars[i] = len(row[i]) if len(row[i]) > max_chars[i] else max_chars[i]
       min_chars[i] = len(row[i]) if len(row[i]) < min_chars[i] else min_chars[i]
       total_chars[i] = total_chars[i] + len(row[i])

       if i == NAME_INDEX:
         collect_titles(row[i])

       for c in row[i]:
         if c in unique_chars[i]:
           unique_chars[i][c] = unique_chars[i][c] + 1
         else:
           unique_chars[i][c] = 1

       if not column_is_int[i]:
         row[i] = "\"" + row[i] + "\""  # wrap in quotes.

  lines.append("INSERT INTO " + tablename + " " + sql_formatted_columns + " VALUES (" + ",".join(row) + ");")

outfile.write("\n".join(lines))

if len(errors) > 0:
  print("\n".join(errors))


def pad(word, width=7):
  return str(word) + " " * (width - len(str(word)))

print "COLUMN STATISTICS\n"
print(pad("", 20) + pad('NULL') + pad('N_NULL') + pad('MIN') + pad('MAX') + pad('AVG') + pad('UNIQUE_CHARS') + "\n")

for i, col in enumerate(columns):
  avg = 0 if non_nulls[i] == 0 else total_chars[i] / non_nulls[i]
  min = 0 if min_chars[i] == 10000 else min_chars[i]
  chars = []
  for key, val in unique_chars[i].iteritems():
    chars.append(key)
  chars.sort()    
  chars = ''.join(chars)

  print(pad(columns[i], 20) + pad(nulls[i]) + pad(non_nulls[i]) + pad(min) + pad(max_chars[i]) + pad(avg) + pad(chars))

print "\nPotential Professional Titles\n"
print(", ".join(titles))


print "\nDone\n"
