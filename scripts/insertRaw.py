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
f2.write('INSERT INTO RawData VALUES\n')
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
   insert = "(" + param[0] + ",\'" + param[1] + "\',"

   if param[2] == 'NULL':
      insert = insert + param[2] + ","
   else:
      insert = insert + "\'" + param[2] + "\',"

   if param[3] == 'NULL':
      insert = insert + param[3] + ","
   else:
      insert = insert + "\'" + param[3] + "\',"

   if param[4] == 'NULL':
      insert = insert + param[4] + ","
   else:
      insert = insert + "\'" + param[4] + "\',"

   if param[5] == 'NULL':
      insert = insert + param[5] + ","
   else:
      insert = insert + "\'" + param[5] + "\',"

   if param[6] == 'NULL':
      insert = insert + param[6] + ","
   else:
      insert = insert + "\'" + param[6] + "\',"

   if param[7] == 'NULL':
      insert = insert + param[7] + ","
   else:
      insert = insert + "\'" + param[7] + "\',"

   if param[8] == 'NULL':
      insert = insert + param[8] + ","
   else:
      insert = insert + "\'" + param[8] + "\',"

   if param[9] == 'NULL':
      insert = insert + param[9] + ","
   else:
      insert = insert + "\'" + param[9] + "\',"

   if param[10] == 'NULL':
      insert = insert + param[10] + ","
   else:
      insert = insert + "\'" + param[10] + "\',"

   if param[11] == 'NULL':
      insert = insert + param[11] + ","
   else:
      insert = insert + "\'" + param[11] + "\',"

   if param[12] == 'NULL':
      insert = insert + param[12] + ","
   else:
      insert = insert + "\'" + param[12] + "\',"

   if param[13] == 'NULL':
      insert = insert + param[13] + ","
   else:
      insert = insert + "\'" + param[13] + "\',"

   if param[14] == 'NULL':
      insert = insert + param[14] + ","
   else:
      insert = insert + "\'" + param[14] + "\',"

   if param[15] == 'NULL':
      insert = insert + param[15] + ","
   else:
      insert = insert + "\'" + param[15] + "\',"

   if param[16] == 'NULL':
      insert = insert + param[16] + ","
   else:
      insert = insert + "\'" + param[16] + "\',"

   if param[17] == 'NULL':
      insert = insert + param[17] + ","
   else:
      insert = insert + "\'" + param[17] + "\',"

   if param[18] == 'NULL':
      insert = insert + param[18] + ","
   else:
      insert = insert + "\'" + param[18] + "\',"

   if param[19] == 'NULL':
      insert = insert + param[19] + ","
   else:
      insert = insert + "\'" + param[19] + "\',"

   if param[20] == 'NULL':
      insert = insert + param[20] + ","
   else:
      insert = insert + "\'" + param[20] + "\',"

   if param[21] == 'NULL':
      insert = insert + param[21] + ","
   else:
      insert = insert + "\'" + param[21] + "\',"

   if param[22] == 'NULL':
      insert = insert + param[22] + "),"
   else:
      insert = insert + "\'" + param[22] + "\'),\n"

   insert = insert.replace('~~~', ',')
   raw = f.readline()

   if len(raw) > 0:
      f2.write(insert)
   else:
      f2.write(insert[:-1])

f2.write(';')
f.close()
f2.close()
