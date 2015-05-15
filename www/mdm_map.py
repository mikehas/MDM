from mdm_mysql import get_cursor
from pprint import pprint

def map_specialty(specialty):
  pass

def map_address(addr):
  pass

def map_phone(phone):
  pass

def map_to_medical_provider(row):
  return 

def is_match(row1, row2):
  match = True
  for a, b in zip(row1[1:], row2[1:]):
    if a != b:
      match = False
  return false

def nullify(row):
  for i, item in enumerate(row):
    if item == None:
      row[i] = 'NULL'
  return row

def map_medical_provider(app, mysql,  row):
  cursor = mysql.connect().cursor()
  row = nullify(row)

  # Insert Address 1
  app.logger.debug("INSERT INTO address VALUES ("+str(row[0])+",'mailing',"+row[12]+"','"+row[11]+"','"+row[10]+"','"+row[9]+"','"+row[8]+"','"+row[7]+"','"+row[6])



  #cursor.execute("INSERT INTO address VALUES (")
   

def map_all(app, mysql):

  cursor = mysql.connect().cursor()
  cursor.execute("SELECT * FROM rawdata LIMIT 10")

  row = cursor.fetchone() 
  while row != None:
    app.logger.info("Mapping source_id = " + str(row[1]))
    map_medical_provider(app, mysql, row)
    row = cursor.fetchone() 


