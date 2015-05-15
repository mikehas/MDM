import subprocess
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


def exec_sql(sql_file):
  proc = subprocess.Popen(['mysql', '-u', 'root', 'mhaskell'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
  try:
    out, err = proc.communicate(file(sql_file).read())
  except subprocess.CalledProcessError, e:
    return "command error, cmd=" + str(e.cmd) \
     + " returncode=" + str(e.returncode) \
     + " output=" + str(e.output)
  return out

Base = declarative_base()

class RawData(Base):
  __tablename__ = 'rawdata'

  sourceid = Column(Integer, primary_key=True)
  ProviderType = Column(String)
  Name = Column(String)
  Gender = Column(String)
  DateOfBirth = Column(String)
  isSoleProprietor = Column(String)
  MailingStreet = Column(String)
  MailingUnit = Column(String)
  MailingCity = Column(String)
  MailingRegion = Column(String)
  MailingPostCode = Column(String)
  MailingCounty = Column(String)
  MailingCountry = Column(String)
  PracticeStreet = Column(String)
  PracticeUnit = Column(String)
  PracticeCity = Column(String)
  PracticeRegion = Column(String)
  PracticePostCode = Column(String)
  PracticeCounty = Column(String)
  PracticeCountry = Column(String)
  Phone = Column(String)
  PrimarySpecialty = Column(String)
  SecondarySpecialty = Column(String) 

 


