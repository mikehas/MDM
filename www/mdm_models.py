from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from mdm_db import Base, Session

class RawData(Base):
  __tablename__ = 'rawdata'

  sourceid = Column(Integer, primary_key=True)
  providertype = Column(String)
  name = Column(String)
  gender = Column(String)
  dateofbirth = Column(String)
  issoleproprietor = Column(String)
  mailingstreet = Column(String)
  mailingunit = Column(String)
  mailingcity = Column(String)
  mailingregion = Column(String)
  mailingpostcode = Column(String)
  mailingcounty = Column(String)
  mailingcountry = Column(String)
  practicestreet = Column(String)
  practiceunit = Column(String)
  practicecity = Column(String)
  practiceregion = Column(String)
  practicepostcode = Column(String)
  practicecounty = Column(String)
  practicecountry = Column(String)
  phone = Column(String)
  primaryspecialty = Column(String)
  secondaryspecialty = Column(String)

class MedicalProvider(Base):
  __tablename__ = 'medicalprovider'
 
  sourceid = Column(Integer, primary_key=True)
  providertype = Column(String)
  name = Column(String)
  gender = Column(String)
  dateofbirth = Column(String)
  issoleproprietor = Column(String)
  primaryspeciality = Column(String)
  secondaryspeciality = Column(String)
  timestamp = Column(String)
  message = Column(String) 

class Address(Base):
  __tablename__ = 'address'

  sourceid = Column(String, primary_key=True)
  addresstype = Column(String, primary_key=True)
  country = Column(String)
  region = Column(String)
  county = Column(String)
  city = Column(String)
  postalcode = Column(String)
  street = Column(String)
  unit = Column(String)
 
