from mdm_mysql import get_cursor
from pprint import pprint
from mdm_db import Session
from mdm_models import *
from flaskr import app
import time

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

def map_all():

  session = Session()
  rawdata = session.query(RawData).limit(10)

  for i, row in enumerate(rawdata):
    now = time.strftime('%Y-%m-%d %H:%M:%S') 
    
    provider = MedicalProvider(sourceid=row.sourceid, providertype=row.providertype, name=row.name, gender=row.gender, dateofbirth=row.dateofbirth, issoleproprietor=row.issoleproprietor, primaryspeciality=row.primaryspecialty, secondaryspeciality=row.secondaryspecialty, timestamp=now, message="basic mapping")
    session.add(provider)
    session.commit()

    mail_addr = Address(sourceid=row.sourceid, addresstype='mailing',country=row.mailingcountry,region=row.mailingregion, county=row.mailingcounty, city=row.mailingcity, postalcode=row.mailingpostcode)
    session.add(mail_addr)
    session.commit()

    practice_addr = Address(sourceid=row.sourceid, addresstype='practice',country=row.practicecountry,region=row.practiceregion, county=row.practicecounty, city=row.practicecity, postalcode=row.practicepostcode)
    session.add(practice_addr)
    session.commit()

