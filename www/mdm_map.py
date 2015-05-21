from flaskr import app
from pprint import pprint
from mdm_db import Session, safe_commit
from mdm_models import *
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, InvalidRequestError, DBAPIError
import time
import string
import re
import mdm_schema

def map_specialty(specialty):
  pass

def clean_address(addr):
  if addr.country is not None:
    addr.country = addr.country.upper()
  if addr.region is not None:
    addr.region = addr.region.upper()
  if addr.county is not None:
    addr.county = addr.county.upper()
  if addr.city is not None:
    addr.city = addr.city.upper()
  if addr.street is not None:
    addr.street = addr.street.upper()
  if addr.unit is not None:
    addr.unit = addr.unit.upper()
  return addr

def map_phone(phone):
  pass

def clean_name(name):
  nameList = re.sub(ur"\p{P}+", "", name).upper().split(' ')
  nameList.sort()
  return string.join(nameList, ' ')

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



@safe_commit
def map_provider(app, row, now):
  provider = MedicalProvider(sourceid=row.sourceid, providertype=row.providertype, name=clean_name(row.name), gender=row.gender, dateofbirth=row.dateofbirth, issoleproprietor=row.issoleproprietor, primaryspecialty=row.primaryspecialty, secondaryspecialty=row.secondaryspecialty, timestamp=now, message="basic mapping")
  return provider

@safe_commit
def map_address(app, row, now):
  mail_addr = Address(sourceid=row.sourceid, addresstype='mailing',country=row.mailingcountry,region=row.mailingregion, county=row.mailingcounty, city=row.mailingcity, postalcode=row.mailingpostcode)
  if mail_addr.country is not None and mail_addr.region is not None and mail_addr.county is not None and mail_addr.city is not None and mail_addr.postalcode is not None:
    return mail_addr

@safe_commit
def map_practice_address(app, row, now):
  practice_addr = Address(sourceid=row.sourceid, addresstype='practice',country=row.practicecountry,region=row.practiceregion, county=row.practicecounty, city=row.practicecity, postalcode=row.practicepostcode)

  if practice_addr.country is not None and practice_addr.region is not None and practice_addr.county is not None and practice_addr.city is not None and practice_addr.postalcode is not None:
    return clean_address(practice_addr)

def map_all():
  session = Session()
  #rawdata = session.query(RawData).limit(10)
  rawdata = session.query(RawData).limit(1000)
  #rawdata = session.query(RawData).all()

  mapped = 0
  errors = []

  for i, row in enumerate(rawdata):
    now = time.strftime('%Y-%m-%d %H:%M:%S') 
    if i % 1000 == 0:
      app.logger.debug("Sourceid: " + str(row.sourceid) + " Processing...")
   
    map_provider(app, row, now)
    map_address(app, row, now)
    map_practice_address(app, row, now)

    mapped = mapped + 1

  app.logger.debug("Chunking and mapping phones...")
  mdm_schema.exec_sql(app, 'scripts/MapPhones.sql')

  return mapped, errors

