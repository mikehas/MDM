from pprint import pprint
from mdm_db import Session
from mdm_models import *
from flaskr import app
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, InvalidRequestError, DBAPIError
import time
import string
import re

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
   
    try:
      s2 = Session()
      provider = MedicalProvider(sourceid=row.sourceid, providertype=row.providertype, name=clean_name(row.name), gender=row.gender, dateofbirth=row.dateofbirth, issoleproprietor=row.issoleproprietor, primaryspeciality=row.primaryspecialty, secondaryspeciality=row.secondaryspecialty, timestamp=now, message="basic mapping")
      s2.add(provider)
      s2.commit()
    except Exception, e:
      app.logger.debug("******** ERROR CAUGHT **********" + e.message)
      errors.append(['medical_provider',row.sourceid, e.message])
      s2.close()
      s2 = Session()
    finally:
      s2.close()

    try:
      s2 = Session()
      mail_addr = Address(sourceid=row.sourceid, addresstype='mailing',country=row.mailingcountry,region=row.mailingregion, county=row.mailingcounty, city=row.mailingcity, postalcode=row.mailingpostcode)
      s2.add(clean_address(mail_addr))
      s2.commit()
    except Exception, e:
      app.logger.debug("Sourceid: " + str(row.sourceid) + " Error: " + e.message)
      errors.append(['mailing_address',row.sourceid, e.message])
      session.rollback()
    finally:
      s2.close()

    try:
      s2 = Session()
      practice_addr = Address(sourceid=row.sourceid, addresstype='practice',country=row.practicecountry,region=row.practiceregion, county=row.practicecounty, city=row.practicecity, postalcode=row.practicepostcode)
      s2.add(clean_address(practice_addr))
      s2.commit()
    except Exception, e:
      app.logger.debug("Sourceid: " + str(row.sourceid) + " Error: " + e.message)
      errors.append(['practice_address',row.sourceid, e.message])
      s2.rollback()
    finally:
      s2.close()

    try:
      s2 = Session()
      phone = Phone(sourceid=row.sourceid, exchange=row.phone)
      s2.add(phone)
      s2.commit()
    except Exception, e:
      app.logger.debug("Sourceid: " + str(row.sourceid) + " Error: " + e.message)
      errors.append(['phone',row.sourceid, e.message])
      s2.rollback()
    finally:
      s2.close()

    mapped = mapped + 1

  return mapped, errors

