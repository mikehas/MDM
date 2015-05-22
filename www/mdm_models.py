from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

from mdm_db import Base, Session

class RawData(Base):
  __tablename__ = 'RawData'

  sourceid = Column(Integer, primary_key=True, autoincrement=False)
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
  __tablename__ = 'MedicalProvider'
 
  sourceid = Column(Integer, primary_key=True)
  providertype = Column(String)
  name = Column(String)
  gender = Column(String)
  dateofbirth = Column(String)
  issoleproprietor = Column(String)
  primaryspecialty = Column(String)
  secondaryspecialty = Column(String)
  timestamp = Column(DateTime)
  message = Column(String) 

class Address(Base):
  __tablename__ = 'Address'

  sourceid = Column(String, primary_key=True)
  addresstype = Column(String, primary_key=True)
  country = Column(String)
  region = Column(String)
  county = Column(String)
  city = Column(String)
  postalcode = Column(String)
  street = Column(String)
  unit = Column(String)

class Phone(Base):
  __tablename__ = 'Phones'

  sourceid = Column(Integer, primary_key=True)
  country = Column(String)
  area = Column(String)
  exchange = Column(String)
  subscriber = Column(String)
  ext = Column(String)

class MasteredProvider(Base):
  __tablename__ = 'MasteredMedicalProvider'

  masterid = Column(Integer, primary_key=True, autoincrement=True)
  providertype = Column(String)
  name = Column(String)
  gender = Column(String)
  dateofbirth = Column(String)
  issoleproprietor = Column(String)

class Matched(Base):
  __tablename__ = 'Matched'

  sourceid = Column(Integer, primary_key=True)
  masterid = Column(Integer, primary_key=True)
  timestamp = Column(DateTime)
  matchrule = Column(String)
  message = Column(String)

class MatchedMailingAddress(Base):
  __tablename__ = 'MatchedMailingAddress'

  sourceid = Column(Integer, primary_key=True)
  masterid = Column(Integer, primary_key=True)
  addresstype = Column(String)

class MatchedPhone(Base):
  __tablename__ = 'MatchedPhone'

  sourceid = Column(Integer, primary_key=True)
  masterid = Column(Integer, primary_key=True)

class MatchedPracticeAddress(Base):
  __tablename__ = 'MatchedPracticeAddress'

  sourceid = Column(Integer, primary_key=True)
  masterid = Column(Integer, primary_key=True)
  addresstype = Column(String)

class MatchedPrimarySpecialty(Base):
  __tablename__ = 'MatchedPrimarySpecialties'

  masterid = Column(Integer, primary_key=True)
  specialty = Column(String, primary_key=True)

class MatchedSecondarySpecialty(Base):
  __tablename__ = 'MatchedSecondarySpecialties'

  masterid = Column(Integer, primary_key=True)
  specialty = Column(String, primary_key=True)


