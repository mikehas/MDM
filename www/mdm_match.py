from pprint import pprint
from mdm_db import Session, safe_commit
from mdm_models import *
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, InvalidRequestError, DBAPIError
import time

@safe_commit
def match_mailing_address(app, masterid, sourceid):
  match_mailing_address = MatchedMailingAddress(sourceid=sourceid, masterid=masterid, addresstype='mailing')
  return match_mailing_address
 
@safe_commit
def match_practice_address(app, masterid, sourceid):
  match_practice_address = MatchedPracticeAddress(sourceid=sourceid, masterid=masterid, addresstype='practice')
  return match_practice_address
 
def match_mastered_provider(app, row, now):
  s = Session()
  
  m = MasteredProvider(providertype=row.providertype,name=row.name,gender=row.gender,dateofbirth=row.dateofbirth,issoleproprietor=row.issoleproprietor) 

  s.add(m)
  s.flush()
  
  match = Matched(sourceid=row.sourceid,masterid=m.masterid,timestamp=now,matchrule='transfer',message='<insert message here>')
  s.add(match)
  s.flush()

  source_master = s.query(Matched).filter_by(masterid=m.masterid).one()
  sourceid = source_master.sourceid
  source_provider = s.query(MedicalProvider).filter_by(sourceid=sourceid).one()

  if source_provider.primaryspecialty is not None:
    match_primary_specialty = MatchedPrimarySpecialty(masterid=m.masterid, specialty=source_provider.primaryspecialty)
    s.add(match_primary_specialty)

  if source_provider.secondaryspecialty is not None:
    match_second_specialty = MatchedSecondarySpecialty(masterid=m.masterid, specialty=source_provider.secondaryspecialty)
    s.add(match_second_specialty)

  match_mailing_address(app, m.masterid, sourceid)
  match_practice_address(app, m.masterid, sourceid)

  match_phone = MatchedPhone(sourceid=sourceid, masterid=m.masterid)
  s.add(match_phone)

  s.commit()
  s.close()

def match_all(app):
  session = Session()

  #providers = session.query(MedicalProvider).limit(10)
  providers = session.query(MedicalProvider).limit(100)
  #providers = session.query(MedicalProvider).limit(1000)
  #providers = session.query(MedicalProvider).all()

  matched = 0
  errors = []

  for i, row in enumerate(providers):
    now = time.strftime('%Y-%m-%d %H:%M:%S') 
    if i % 1000 == 0:
      app.logger.info("Sourceid: " + str(row.sourceid) + " Matching rocessing...")
   
    match_mastered_provider(app, row, now)

    matched = matched + 1

  return matched, errors

