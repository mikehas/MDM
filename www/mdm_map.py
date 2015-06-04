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
    addr.country = addr.country.strip().upper()
  if addr.region is not None:
    addr.region = addr.region.strip().upper()
  if addr.county is not None:
    addr.county = addr.county.strip().upper()
  if addr.city is not None:
    addr.city = addr.city.strip().upper()
  if addr.street is not None:
    addr.street = addr.street.strip().upper()
  if addr.unit is not None:
    addr.unit = addr.unit.strip().upper()
  return addr

def map_phone(phone):
  pass

def clean_name(name):
  nameList = re.sub(ur"\p{P}+", "", name.strip()).upper().split(' ')
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

def map_all():
  session = Session()
  #rawdata = session.query(RawData).limit(10)
  #rawdata = session.query(RawData).limit(100)
  #rawdata = session.query(RawData).limit(1000)
  rawdata = session.query(RawData).limit(8000)
  #rawdata = session.query(RawData).all()

  mapped = 0
  errors = []

  for i, row in enumerate(rawdata):
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    if i % 1000 == 0:
      app.logger.debug("Sourceid: " + str(row.sourceid) + " Processing...")

    provider = MedicalProvider(sourceid=row.sourceid,\
          providertype=row.providertype, name=clean_name(row.name),\
          gender=row.gender, dateofbirth=row.dateofbirth,\
          issoleproprietor=row.issoleproprietor,\
          primaryspecialty=row.primaryspecialty,\
          secondaryspecialty=row.secondaryspecialty,\
          timestamp=now, message="basic mapping")
    session.add(provider)
    session.flush()

    if row.mailingcountry is not None or row.mailingregion is not None or\
          row.mailingcounty is not None or row.mailingcity is not None or\
          row.mailingpostcode is not None or row.mailingstreet is not None or\
          row.mailingunit is not None:
      mail_addr = clean_address(\
            Address(sourceid=row.sourceid, addresstype='mailing',\
            country=row.mailingcountry,region=row.mailingregion,\
            county=row.mailingcounty, city=row.mailingcity,\
            postalcode=row.mailingpostcode, street=row.mailingstreet,\
            unit=row.mailingunit))
      session.add(mail_addr)

    if row.practicecountry is not None or row.practiceregion is not None or\
          row.practicecounty is not None or row.practicecity is not None or\
          row.practicepostcode is not None or row.practicestreet is not None or\
          row.practiceunit is not None:
      practice_addr = clean_address(\
            Address(sourceid=row.sourceid, addresstype='practice',\
            country=row.practicecountry,region=row.practiceregion,\
            county=row.practicecounty, city=row.practicecity,\
            postalcode=row.practicepostcode, street=row.practicestreet,\
            unit=row.practiceunit))
      session.add(practice_addr)

    mapped = mapped + 1

  session.commit()
  session.close()

  app.logger.debug("Chunking and mapping phones...")
  mdm_schema.exec_sql(app, 'scripts/MapPhones.sql')

  return mapped, errors

