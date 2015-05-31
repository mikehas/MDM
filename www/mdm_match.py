from pprint import pprint
from mdm_db import Session, safe_commit
from mdm_models import *
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, InvalidRequestError, DBAPIError
import time
from nltk.metrics.distance import edit_distance

@safe_commit
def match_mailing_address(app, masterid, sourceid):
  match_mailing_address = MatchedMailingAddress(sourceid=sourceid, masterid=masterid, addresstype='mailing')
  return match_mailing_address

@safe_commit
def match_practice_address(app, masterid, sourceid):
  match_practice_address = MatchedPracticeAddress(sourceid=sourceid, masterid=masterid, addresstype='practice')
  return match_practice_address

# val1, val2 are the values to compare
# mode is the matching mode (ignore, exact, fuzzy, do not differ)
def attributeMatches(val1, val2, mode="exact", threshold=0):
  if mode == "ignore":
    return True
  if mode == "exact" or mode == "fuzzy":
    return val1 is not None and val2 is not None and edit_distance(val1,val2) <= threshold
  if mode == "do not differ":
    return val1 is None or val2 is None or edit_distance(val1,val2) == 0
  return False

# s - SQLAlchemy session
# mp - Medical Provider
# mmp - Mastered Medical Provider
# rule - rule object
def matches_mastered_provider(s, mp, mmp, rule):
  mp_phone = s.query(Phone).filter_by(sourceid=mp.sourceid).all()
  mp_phone = mp_phone[0] if len(mp_phone) == 1 else None
  mp_paddress = s.query(Address).filter_by(sourceid=mp.sourceid, addresstype='practice').all()
  mp_paddress = mp_paddress[0] if len(mp_paddress) == 1 else None
  mp_maddress = s.query(Address).filter_by(sourceid=mp.sourceid, addresstype='mailing').all()
  mp_maddress = mp_maddress[0] if len(mp_maddress) == 1 else None

  mmp_phones = s.query(MatchedPhone, Phone).\
        filter(MatchedPhone.masterid == mmp.masterid,\
               Phone.sourceid == MatchedPhone.sourceid).all()
  mmp_paddresses = s.query(MatchedPracticeAddress, Address).\
        filter(MatchedPracticeAddress.masterid == mmp.masterid,\
               Address.sourceid == MatchedPracticeAddress.sourceid,\
               Address.addresstype == 'practice').all()
  mmp_maddresses = s.query(MatchedMailingAddress, Address).\
        filter(MatchedMailingAddress.masterid == mmp.masterid,\
               Address.sourceid == MatchedMailingAddress.sourceid,\
               Address.addresstype == 'mailing').all()
  mmp_pspecialties =  s.query(MatchedPrimarySpecialty).\
        filter(MatchedPrimarySpecialty.masterid == mmp.masterid).all()
  mmp_sspecialties =  s.query(MatchedSecondarySpecialty).\
        filter(MatchedSecondarySpecialty.masterid == mmp.masterid).all()

  p_prefix = "practice "
  m_prefix = "mailing "

  for col_match in rule["match_cols"]:
    col_name = col_match["match_col"]
    threshold = col_match["match_threshold"] if hasattr(col_match, "match_threshold") else 0

    if col_name.startswith(p_prefix):
      att_name = col_name[len(p_prefix):]
      valid = False
      for att in Address.__table__.columns:
        if att_name == str(att):
          valid = True
          break
      if not valid:
        return False
      if len(mmp_paddress) == 0:
        if not attributeMatches(None,\
              getattr(mp_paddress, att_name) if mp_paddress is not None else None,\
              col_match["match_type"], threshold):
          return False
      else:
        for m, paddr in mmp_paddresses:
          if not attributeMatches(getattr(paddr, att_name),\
                getattr(mp_paddress, att_name) if mp_paddress is not None else None,\
                col_match["match_type"], threshold):
            return False

    elif col_name.startswith(m_prefix):
      att_name = col_name[len(m_prefix):]
      valid = False
      for att in Address.__table__.columns:
        if att_name == str(att):
          valid = True
          break
      if not valid:
        return False
      if len(mmp_maddress) == 0:
        if not attributeMatches(None,\
              getattr(mp_maddress, att_name) if mp_maddress is not None else None,\
              col_match["match_type"], threshold):
          return False
      else:
        for m, maddr in mmp_maddresses:
          if not attributeMatches(getattr(maddr, att_name),\
                getattr(mp_maddress, att_name) if mp_maddress is not None else None,\
                col_match["match_type"], threshold):
            return False

    elif col_name == "phone":
      if len(mmp_phones) == 0:
        if not attributeMatches(None,\
              getattr(mp_phone, att_name) if mp_phone is not None else None,\
              col_match["match_type"], threshold):
          return False
      else:
        for m, phone in mmp_phones:
          if not attributeMatches(phone.cleanphone,\
                mp_phone.cleanphone if mp_phone is not None else None,\
                col_match["match_type"], threshold):
            return False

    elif col_name == "primaryspecialty":
      if len(mmp_pspecialties) == 0:
        if not attributeMatches(None, mp.primaryspecialty,\
              col_match["match_type"], threshold):
          return False
      else:
        for specialty_match in mmp_pspecialties:
          if not attributeMatches(specialty_match.specialty, mp.primaryspecialty,\
                col_match["match_type"], threshold):
            return False

    elif col_name == "secondaryspecialty":
      if len(mmp_sspecialties) == 0:
        if not attributeMatches(None, mp.secondaryspecialty,\
              col_match["match_type"], threshold):
          return False
      else:
        for specialty_match in mmp_sspecialties:
          if not attributeMatches(specialty_match.specialty, mp.secondaryspecialty,\
                col_match["match_type"], threshold):
            return False

    else:
      valid = False
      for att in MasteredProvider.__table__.columns:
        if att_name == str(col_name):
          valid = True
          break
      if not valid:
        return False
      if not attributeMatches(getattr(mmp, col_name), getattr(mp, col_name),\
            col_match["match_type"], threshold):
        return False

  return True

def match_to_mastered_providers(app, mp, rules, now):
  s = Session()

  masteredProviders = s.query(MasteredProvider).filter_by(providertype=mp.providertype).all()
  matchingRule = None
  m = None

  #if no rules or no masteredProviders, we just push all through
  for mmp in masteredProviders:
    for rule in rules:
      if matches_mastered_provider(s, mp, mmp, rule):
        matched = True
        matchingRule = rule
        m = mmp

  if m is not None:
    match = Matched(sourceid=mp.sourceid,masterid=m.masterid,timestamp=now,\
          matchrule=matchingRule.title,message='Applied rule!')
    s.add(match)

    #do survivorship here
    #need to figure out how to get back to original rawdata name...
    if (m.name is None and mp.name is not None) or\
          len(mp.name) > len(m.name):
      m.name = mp.name
    if m.gender is None:
      m.gender = mp.gender
    if (m.dateofbirth is None and mp.dateofbirth is not None) or\
          len(mp.dateofbirth) > len(m.dateofbirth):
      m.dateofbirth = mp.dateofbirth
    if m.issoleproprietor is None:
      m.issoleproprietor = mp.issoleproprietor

  else:
    #no matches found! Insert new mastered provider
    m = MasteredProvider(providertype=mp.providertype,name=mp.name,\
          gender=mp.gender,dateofbirth=mp.dateofbirth,\
          issoleproprietor=mp.issoleproprietor)
    s.add(m)
    s.flush()

    match = Matched(sourceid=mp.sourceid,masterid=m.masterid,timestamp=now,\
          matchrule='Transfer',message='First record of its kind so far...')
    s.add(match)

  #link phone, addrs, and specialties to matched* lookup tables
  if mp.primaryspecialty is not None:
    match_primary_specialty = MatchedPrimarySpecialty(masterid=m.masterid,\
          specialty=mp.primaryspecialty)
    s.add(match_primary_specialty)

  if mp.secondaryspecialty is not None:
    match_second_specialty = MatchedSecondarySpecialty(masterid=m.masterid,\
          specialty=mp.secondaryspecialty)
    s.add(match_second_specialty)

  match_mailing_address(app, m.masterid, mp.sourceid)
  match_practice_address(app, m.masterid, mp.sourceid)

  match_phone = MatchedPhone(sourceid=mp.sourceid, masterid=m.masterid)
  s.add(match_phone)

  s.commit()
  s.close()


def match_all(app):
  session = Session()

  #providers = session.query(MedicalProvider).limit(10)
  providers = session.query(MedicalProvider).limit(100)
  #providers = session.query(MedicalProvider).limit(1000)
  #providers = session.query(MedicalProvider).all()

  #load rules here
  rules = []

  matched = 0
  errors = []

  for i, row in enumerate(providers):
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    if i % 1000 == 0:
      app.logger.info("Sourceid: " + str(row.sourceid) + " Matching processing...")

    match_to_mastered_providers(app, row, rules, now)

    matched = matched + 1

  return matched, errors

