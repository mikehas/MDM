import math
from pprint import pprint
from mdm_db import Session, safe_commit
from mdm_models import *
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, InvalidRequestError, DBAPIError
import time
from nltk.metrics.distance import edit_distance
from mdm_rules import load_rules
import pprint

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
def matches_mastered_provider(s, mp_obj, mmp_obj, rule):
  mp = mp_obj["mp"]
  mp_phone = mp_obj["mp_phone"]
  mp_paddress = mp_obj["mp_paddress"]
  mp_maddress = mp_obj["mp_maddress"]

  mmp = mmp_obj["mmp"]
  mmp_names = mmp_obj["mmp_names"]
  mmp_phones = mmp_obj["mmp_phones"]
  mmp_paddresses = mmp_obj["mmp_paddresses"]
  mmp_maddresses = mmp_obj["mmp_maddresses"]
  mmp_pspecialties = mmp_obj["mmp_pspecialties"]
  mmp_sspecialties = mmp_obj["mmp_sspecialties"]

  p_prefix = "practice "
  m_prefix = "mailing "

  for col_match in rule["match_cols"]:
    col_name = col_match["match_col"].lower()
    matchtype = col_match["match_type"].lower()
    threshold = 0 if matchtype == "exact" else col_match["match_threshold"]

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
              matchtype, threshold):
          return False
      else:
        for paddr in mmp_paddresses:
          if not attributeMatches(getattr(paddr, att_name),\
                getattr(mp_paddress, att_name) if mp_paddress is not None else None,\
                matchtype, threshold):
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
              matchtype, threshold):
          return False
      else:
        for maddr in mmp_maddresses:
          if not attributeMatches(getattr(maddr, att_name),\
                getattr(mp_maddress, att_name) if mp_maddress is not None else None,\
                matchtype, threshold):
            return False

    elif col_name == "name":
      if len(mmp_names) == 0:
        if not attributeMatches(None, mp.name, matchtype, threshold):
          return False
      else:
        for mmp_name in mmp_names:
          if not attributeMatches(mmp_name, mp.name, matchtype, threshold):
            return False

    elif col_name == "phone":
      if len(mmp_phones) == 0:
        if not attributeMatches(None, mp_phone, matchtype, threshold):
          return False
      else:
        for phone in mmp_phones:
          if not attributeMatches(phone, mp_phone, matchtype, threshold):
            return False

    elif col_name == "primaryspecialty":
      if len(mmp_pspecialties) == 0:
        if not attributeMatches(None, mp.primaryspecialty,\
              matchtype, threshold):
          return False
      else:
        for specialty in mmp_pspecialties:
          if not attributeMatches(specialty, mp.primaryspecialty,\
                matchtype, threshold):
            return False

    elif col_name == "secondaryspecialty":
      if len(mmp_sspecialties) == 0:
        if not attributeMatches(None, mp.secondaryspecialty,\
              matchtype, threshold):
          return False
      else:
        for specialty in mmp_sspecialties:
          if not attributeMatches(specialty, mp.secondaryspecialty,\
                matchtype, threshold):
            return False

    else:
      valid = False
      for att in MasteredProvider.__table__.columns:
        if col_name == str(att):
          valid = True
          break
      if not valid:
        return False
      if not attributeMatches(getattr(mmp, col_name), getattr(mp, col_name),\
            matchtype, threshold):
        return False

  return True

def get_mp_object(s, mp):
  mp_rawname = s.query(RawData.name).filter_by(sourceid=mp.sourceid).one()
  mp_rawname = mp_rawname[0]
  mp_phone = s.query(Phone.cleanphone).filter_by(sourceid=mp.sourceid).all()
  mp_phone = mp_phone[0] if len(mp_phone) == 1 else None
  mp_paddress = s.query(Address).filter_by(sourceid=mp.sourceid, addresstype="practice").all()
  mp_paddress = mp_paddress[0] if len(mp_paddress) == 1 else None
  mp_maddress = s.query(Address).filter_by(sourceid=mp.sourceid, addresstype="mailing").all()
  mp_maddress = mp_maddress[0] if len(mp_maddress) == 1 else None
  return {"mp": mp, "mp_rawname": mp_rawname, "mp_phone": mp_phone,\
        "mp_paddress": mp_paddress, "mp_maddress": mp_maddress}

def get_mmp_object(s, mmp):
  mmp_names = s.query(MedicalProvider.name).\
        filter(mmp.masterid == Matched.masterid,\
               Matched.sourceid == MedicalProvider.sourceid).all()
  mmp_phones = s.query(Phone.cleanphone).\
        filter(MatchedPhone.masterid == mmp.masterid,\
               Phone.sourceid == MatchedPhone.sourceid).all()
  mmp_paddresses = s.query(Address).\
        filter(MatchedPracticeAddress.masterid == mmp.masterid,\
               Address.sourceid == MatchedPracticeAddress.sourceid,\
               Address.addresstype == 'practice').all()
  mmp_maddresses = s.query(Address).\
        filter(MatchedMailingAddress.masterid == mmp.masterid,\
               Address.sourceid == MatchedMailingAddress.sourceid,\
               Address.addresstype == 'mailing').all()
  mmp_pspecialties =  s.query(MatchedPrimarySpecialty.specialty).\
        filter(MatchedPrimarySpecialty.masterid == mmp.masterid).all()
  mmp_sspecialties =  s.query(MatchedSecondarySpecialty.specialty).\
        filter(MatchedSecondarySpecialty.masterid == mmp.masterid).all()
  return {"mmp": mmp, "mmp_names": mmp_names, "mmp_phones": mmp_phones,\
        "mmp_paddresses": mmp_paddresses, "mmp_maddresses":mmp_maddresses,\
        "mmp_pspecialties": mmp_pspecialties, "mmp_sspecialties": mmp_sspecialties}

def match_to_mastered_providers(app, mp, rules, now):
  s = Session()

  mp_obj = get_mp_object(s, mp)
  masteredProviders = s.query(MasteredProvider).filter_by(providertype=mp.providertype).all()
  matchingRule = None
  m = None

  #if no rules or no masteredProviders, we just push all through
  for mmp in masteredProviders:
    mmp_obj = get_mmp_object(s, mmp)
    for rule in rules:
      has_type = rule.get("has_type", None)
      if has_type is None or has_type.lower() == mp.providertype:
        if matches_mastered_provider(s, mp_obj, mmp_obj, rule):
          matchingRule = rule
          m = mmp
          break
    if m is not None:
      break

  if m is not None:
    fieldsSurvived = None
    #do survivorship here
    if (m.name is None and mp.name is not None) or\
          len(mp.name) > len(m.name):
      m.name = mp_obj["mp_rawname"]
      if fieldsSurvived is None:
        fieldsSurvived = "Survived: name"
      else:
        fieldsSurvived = fieldsSurvived + ", name"
    if m.gender is None:
      m.gender = mp.gender
      if fieldsSurvived is None:
        fieldsSurvived = "Survived: gender"
      else:
        fieldsSurvived = fieldsSurvived + ", gender"
    if (m.dateofbirth is None and mp.dateofbirth is not None) or\
          len(mp.dateofbirth) > len(m.dateofbirth):
      m.dateofbirth = mp.dateofbirth
      if fieldsSurvived is None:
        fieldsSurvived = "Survived: dateofbirth"
      else:
        fieldsSurvived = fieldsSurvived + ", dateofbirth"
    if m.issoleproprietor is None:
      m.issoleproprietor = mp.issoleproprietor
      if fieldsSurvived is None:
        fieldsSurvived = "Survived: issoleproprietor"
      else:
        fieldsSurvived = fieldsSurvived + ", issoleproprietor"

    match = Matched(sourceid=mp.sourceid,masterid=m.masterid,timestamp=now,\
          matchrule=matchingRule["title"],message=fieldsSurvived)
    s.add(match)

  else:
    #no matches found! Insert new mastered provider
    m = MasteredProvider(providertype=mp.providertype,name=mp_obj["mp_rawname"],\
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

  if s.query(s.query(Address)\
        .filter_by(sourceid=mp.sourceid,addresstype="mailing").exists())\
        .scalar() == 1:
    match_mailing_address = MatchedMailingAddress(sourceid=mp.sourceid, masterid=m.masterid,\
          addresstype='mailing')
    s.add(match_mailing_address)

  if s.query(s.query(Address)\
        .filter_by(sourceid=mp.sourceid,addresstype="practice").exists())\
        .scalar() == 1:
    match_practice_address = MatchedPracticeAddress(sourceid=mp.sourceid, masterid=m.masterid,\
          addresstype='practice')
    s.add(match_practice_address)

  if s.query(s.query(Phone).filter_by(sourceid=mp.sourceid).exists())\
        .scalar() == 1:
    match_phone = MatchedPhone(sourceid=mp.sourceid, masterid=m.masterid)
    s.add(match_phone)

  s.commit()
  s.close()

def match_all(app):
  session = Session()

  #load rules here
  rules = load_rules("rules/example_rules.yaml")["Rules"]

  app.logger.debug("Matching: match rules loaded")
  pprint.pprint(rules)

  matched = 0
  errors = []

  #grab only providers not already matched
  providers = session.query(MedicalProvider)\
        .filter(~MedicalProvider.sourceid.in_(session.query(Matched.sourceid)))
  providers_count = providers.count()
  chunk_size = min(providers_count, 1000)

  if providers_count > 0:
    app.logger.info("Matching: starting on "+str(providers_count)+" providers in "+\
          str(providers_count/chunk_size +\
            (1 if providers_count % chunk_size != 0 else 0))+\
          " chunks of "+str(chunk_size))
    for start in xrange(0, providers_count, chunk_size):
      app.logger.info("Matching: processing chunk #"+str(start/chunk_size + 1))
      end = min(start + chunk_size, providers_count)
      providers_chunk = providers[start:end]
      for provider in providers_chunk:
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        match_to_mastered_providers(app, provider, rules, now)
        matched = matched + 1

  return matched, errors

