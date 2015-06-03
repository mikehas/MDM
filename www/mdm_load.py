#! /usr/bin/env python

import os
import sys
import csv
import json
import re

def load_nucc(csv_file):
  f = open(csv_file, 'rb')
  f.readline()
  reader = csv.reader(f, delimiter=',')

  columns = ['SourceID', 'ProviderType', 'Name', 'Gender', 'DateOfBirth', 'isSoleProprietor', 'MailingStreet', 'MailingUnit', 'MailingCity', 'MailingRegion', 'MailingPostCode', 'MailingCounty', 'MailingCountry', 'PracticeStreet', 'PracticeUnit', 'PracticeCity', 'PracticeRegion', 'PracticePostCode', 'PracticeCounty', 'PracticeCountry', 'Phone', 'PrimarySpecialty', 'SecondarySpecialty']
  column_is_int = [False, False]

  sql_formatted_columns = '(' + ",".join("{0}".format(w) for w in columns) + ')'

  print "Parsing file..."
  for j, row in enumerate(reader):
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

