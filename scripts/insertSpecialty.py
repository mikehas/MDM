#! /usr/bin/env python

#import binascii
import sys
import os

if len(sys.argv) < 2:
   print("Insufficient arguments. Usage: insert.py <fileName>")
   sys.exit()

if os.path.isfile(sys.argv[1]) == False:
   print("Input file does not exist")
   sys.exit()

# Open the file and generate the appropriate length one time pad key.
f = open(sys.argv[1], 'rb')
f2 = open(sys.argv[1][:-4] + '.sql', 'w')

raw = f.readline()
raw = f.readline()
f2.write('INSERT INTO Specialty VALUES\n')
lines = []

while len(raw) > 0:
   raw = raw.replace('\n', '')
   raw = raw.replace('\r', '')
   raw = raw.replace('\'', '\\\'')
   raw = raw.replace(',', '~~~')
   raw = raw.replace('\t',',')

   while ',,' in raw:
      raw = raw.replace(',,', ',NULL,')

   # Handle last and first params being NULL
   if raw[-1] == ',':
      raw = raw + 'NULL'

   if raw[0] == ',':
      raw = 'NULL' + raw

   param = raw.split(",")
   insert = "(" + param[0] + "," + param[1] + ","

   if param[2] == 'NULL':
      insert = insert + param[2] + ","
   else:
      insert = insert + "\'" + param[2] + "\',"

   if param[3] == 'NULL':
      insert = insert + param[3] + ","
   else:
      insert = insert + "\'" + param[3] + "\',"

   if param[4] == 'NULL':
      insert = insert + param[4] + "),"
   else:
      insert = insert + "\'" + param[4] + "\'),\n"

   insert = insert.replace('~~~', ',')
   raw = f.readline()

   if len(raw) > 0:
      f2.write(insert)
   else:
      f2.write(insert[:-2])

f2.write(';')
f.close()
f2.close()
