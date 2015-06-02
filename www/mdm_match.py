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
def matches_mastered_provider(app, s, mp_obj, mmp_obj, rule):
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
    threshold = 0 if matchtype == "exact" or matchtype == "do not differ"\
          else col_match["match_threshold"]

    if col_name.startswith(p_prefix):
      att_name = col_name[len(p_prefix):]
      if len(mmp_paddresses) == 0:
        if not attributeMatches(None,\
              getattr(mp_paddress, att_name) if mp_paddress is not None else None,\
              matchtype, threshold):
          return False
      else:
        foundMatch = False
        for paddr in mmp_paddresses:
          if attributeMatches(getattr(paddr, att_name),\
                getattr(mp_paddress, att_name) if mp_paddress is not None else None,\
                matchtype, threshold):
            foundMatch = True
            break
        if not foundMatch:
          return False

    elif col_name.startswith(m_prefix):
      att_name = col_name[len(m_prefix):]
      if len(mmp_maddresses) == 0:
        if not attributeMatches(None,\
              getattr(mp_maddress, att_name) if mp_maddress is not None else None,\
              matchtype, threshold):
          return False
      else:
        foundMatch = False
        for maddr in mmp_maddresses:
          if attributeMatches(getattr(maddr, att_name),\
                getattr(mp_maddress, att_name) if mp_maddress is not None else None,\
                matchtype, threshold):
            foundMatch = True
            break
        if not foundMatch:
          return False

    elif col_name == "name":
      if len(mmp_names) == 0:
        if not attributeMatches(None, mp.name, matchtype, threshold):
          return False
      else:
        foundMatch = False
        for mmp_name in mmp_names:
          if attributeMatches(mmp_name, mp.name, matchtype, threshold):
            foundMatch = True
            break
        if not foundMatch:
          return False

    elif col_name == "phone":
      if len(mmp_phones) == 0:
        if not attributeMatches(None, mp_phone, matchtype, threshold):
          return False
      else:
        foundMatch = False
        for phone in mmp_phones:
          if attributeMatches(phone, mp_phone, matchtype, threshold):
            foundMatch = True
            break
        if not foundMatch:
          return False

    elif col_name == "primaryspecialty":
      if len(mmp_pspecialties) == 0:
        if not attributeMatches(None, mp.primaryspecialty,\
              matchtype, threshold):
          return False
      else:
        foundMatch = False
        for specialty in mmp_pspecialties:
          if attributeMatches(specialty, mp.primaryspecialty,\
                matchtype, threshold):
            foundMatch = True
            break
        if not foundMatch:
          return False

    elif col_name == "secondaryspecialty":
      if len(mmp_sspecialties) == 0:
        if not attributeMatches(None, mp.secondaryspecialty,\
              matchtype, threshold):
          return False
      else:
        foundMatch = False
        for specialty in mmp_sspecialties:
          if attributeMatches(specialty, mp.secondaryspecialty,\
                matchtype, threshold):
            foundMatch = True
            break
        if not foundMatch:
          return False

    elif not attributeMatches(getattr(mmp, col_name), getattr(mp, col_name),\
        matchtype, threshold):
      return False

  return True

def get_applicable_rules(rules, mp_obj):
  newrules = []

  mp = mp_obj["mp"]
  mp_phone = mp_obj["mp_phone"]
  mp_paddress = mp_obj["mp_paddress"]
  mp_maddress = mp_obj["mp_maddress"]

  p_prefix = "practice "
  m_prefix = "mailing "

  for rule in rules:
    applicable = True

    has_type = rule.get("has_type", None)
    if has_type is None or has_type.lower() == mp.providertype.lower():
      for col_match in rule["match_cols"]:
        col_name = col_match["match_col"].lower()
        matchtype = col_match["match_type"].lower()
        if matchtype == "do not differ":
          continue

        if (col_name.startswith(p_prefix) and (mp_paddress is None or\
              getattr(mp_paddress, col_name[len(p_prefix):]) is None)) or\
           (col_name.startswith(m_prefix) and (mp_maddress is None or\
              getattr(mp_maddress, col_name[len(m_prefix):]) is None)) or\
           (col_name == "phone" and mp_phone is None) or\
           (not col_name.startswith(p_prefix) and\
            not col_name.startswith(m_prefix) and\
            col_name != "phone" and getattr(mp, col_name) is None):
             applicable = False
             break
    else:
      applicable = False

    if applicable:
      newrules.append(rule)

  return newrules

def match_to_mastered_providers(app, s, mp_obj, mmp_objs, rules, now):
  mp = mp_obj["mp"]
  matchingRule = None
  m_obj = None
  m = None

  applicable_rules = get_applicable_rules(rules, mp_obj)

  #if no rules or no masteredProviders, we just push all through
  for mmp_obj in mmp_objs:
    for rule in applicable_rules:
      if matches_mastered_provider(app, s, mp_obj, mmp_obj, rule):
        matchingRule = rule
        m_obj = mmp_obj
        m = mmp_obj["mmp"]
        break
    if m is not None:
      break

  if m is not None:
    fieldsSurvived = None
    #do survivorship here
    if mp.name is not None and (m.name is None or\
          len(mp.name) > len(m.name)):
      m.name = mp_obj["mp_rawname"]
      if fieldsSurvived is None:
        fieldsSurvived = "Survived: name"
      else:
        fieldsSurvived = fieldsSurvived + ", name"
    if m.gender is None and mp.gender is not None:
      m.gender = mp.gender
      if fieldsSurvived is None:
        fieldsSurvived = "Survived: gender"
      else:
        fieldsSurvived = fieldsSurvived + ", gender"
    if mp.dateofbirth is not None and (m.dateofbirth is None or\
          len(mp.dateofbirth) > len(m.dateofbirth)):
      m.dateofbirth = mp.dateofbirth
      if fieldsSurvived is None:
        fieldsSurvived = "Survived: dateofbirth"
      else:
        fieldsSurvived = fieldsSurvived + ", dateofbirth"
    if m.issoleproprietor is None and mp.issoleproprietor is not None:
      m.issoleproprietor = mp.issoleproprietor
      if fieldsSurvived is None:
        fieldsSurvived = "Survived: issoleproprietor"
      else:
        fieldsSurvived = fieldsSurvived + ", issoleproprietor"

    if fieldsSurvived is None:
      fieldsSurvived = "Survived: none"

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

    #add our new mmp_obj to our cached collection
    m_obj = {"mmp": m, "mmp_names": [mp.name], "mmp_phones": [],\
        "mmp_paddresses": [], "mmp_maddresses": [],\
        "mmp_pspecialties": [], "mmp_sspecialties": []}
    mmp_objs.append(m_obj)

    match = Matched(sourceid=mp.sourceid,masterid=m.masterid,timestamp=now,\
          matchrule='Transfer',message='First record of its kind so far...')
    s.add(match)

  #link phone, addrs, and specialties to matched* lookup tables and cached data
  if mp.primaryspecialty is not None:
    found = False
    for specialty in m_obj["mmp_pspecialties"]:
      if mp.primaryspecialty == specialty:
        found = True
        break
    if not found:
      match_primary_specialty = MatchedPrimarySpecialty(masterid=m.masterid,\
            specialty=mp.primaryspecialty)
      s.add(match_primary_specialty)
      m_obj["mmp_pspecialties"].append(mp.primaryspecialty)

  if mp.secondaryspecialty is not None:
    found = False
    for specialty in m_obj["mmp_sspecialties"]:
      if mp.secondaryspecialty == specialty:
        found = True
        break
    if not found:
      match_second_specialty = MatchedSecondarySpecialty(masterid=m.masterid,\
            specialty=mp.secondaryspecialty)
      s.add(match_second_specialty)
      m_obj["mmp_sspecialties"].append(mp.secondaryspecialty)

  if mp_obj["mp_maddress"] is not None:
    match_mailing_address = MatchedMailingAddress(sourceid=mp.sourceid, masterid=m.masterid,\
          addresstype='mailing')
    s.add(match_mailing_address)
    m_obj["mmp_maddresses"].append(mp_obj["mp_maddress"])

  if mp_obj["mp_paddress"] is not None:
    match_practice_address = MatchedPracticeAddress(sourceid=mp.sourceid, masterid=m.masterid,\
          addresstype='practice')
    s.add(match_practice_address)
    m_obj["mmp_paddresses"].append(mp_obj["mp_paddress"])

  if mp_obj["mp_phone"] is not None:
    match_phone = MatchedPhone(sourceid=mp.sourceid, masterid=m.masterid)
    s.add(match_phone)
    m_obj["mmp_phones"].append(mp_obj["mp_phone"])

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

def get_mp_objects(s, mps):
  mp_objs = []
  for mp in mps:
    mp_objs.append(get_mp_object(s, mp))
  return mp_objs

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
        "mmp_paddresses": mmp_paddresses, "mmp_maddresses": mmp_maddresses,\
        "mmp_pspecialties": mmp_pspecialties, "mmp_sspecialties": mmp_sspecialties}

def get_mmp_objects(s, mmps):
  mmp_objs = []
  for mmp in mmps:
    mmp_objs.append(get_mmp_object(s, mmp))
  return mmp_objs

def check_rules(app, rules):
  p_prefix = "practice "
  m_prefix = "mailing "

  for rule in rules:
    for col_match in rule["match_cols"]:
      col_name = col_match["match_col"].lower()

      if col_name == "name" or col_name == "phone" or\
          col_name == "primaryspecialty" or col_name == "secondaryspecialty":
        continue

      if col_name.startswith(p_prefix):
        att_name = col_name[len(p_prefix):]
        valid = False
        for att in Address.__table__.columns:
          if att_name == str(att).split(".")[1]:
            valid = True
            break
        if not valid:
          app.logger.debug(col_name+" is not a valid attribute")
          return False

      elif col_name.startswith(m_prefix):
        att_name = col_name[len(m_prefix):]
        valid = False
        for att in Address.__table__.columns:
          if att_name == str(att).split(".")[1]:
            valid = True
            break
        if not valid:
          app.logger.debug(col_name+" is not a valid attribute")
          return False

      else:
        valid = False
        for att in MasteredProvider.__table__.columns:
          if col_name == str(att).split(".")[1]:
            valid = True
            break
        if not valid:
          app.logger.debug(col_name+" is not a valid attribute")
          return False

  return True

def match_all(app):
  session = Session()

  matched = 0
  errors = []

  #load rules here
  rules = load_rules("rules/example_rules.yaml")["Rules"]

  app.logger.debug("Matching: match rules loaded")
  pprint.pprint(rules)
  if not check_rules(app, rules):
    errors.append("Invalid rules")
    return matched, errors

  #grab only providers not already matched
  providers = session.query(MedicalProvider)
  providers_count = providers.count()
  chunk_size = min(providers_count, 1000)

  if providers_count > 0:
    app.logger.info("Matching: starting on "+str(providers_count)+" providers in "+\
          str(providers_count/chunk_size +\
            (1 if providers_count % chunk_size != 0 else 0))+\
          " chunks of "+str(chunk_size))

    individualMMP_objects = get_mmp_objects(session,\
          session.query(MasteredProvider)\
          .filter_by(providertype='Individual').all())
    organizationMMP_objects = get_mmp_objects(session,\
          session.query(MasteredProvider)\
          .filter_by(providertype='Organization').all())
    for start in xrange(0, providers_count, chunk_size):
      app.logger.info("Matching: processing chunk #"+str(start/chunk_size + 1))
      end = min(start + chunk_size, providers_count)
      providers_chunk = providers[start:end]
      mp_objs = get_mp_objects(session, providers_chunk)
      for mp_obj in mp_objs:
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        if session.query(session.query(Matched).\
              filter_by(sourceid=mp_obj["mp"].sourceid).exists()).scalar() == 1:
          continue
        mmp_objs = None
        if mp_obj["mp"].providertype == 'Individual':
          mmp_objs = individualMMP_objects
        elif mp_obj["mp"].providertype == 'Organization':
          mmp_objs = organizationMMP_objects
        else:
          raise Exception("Medical provider not individual or organization: "+\
                mp_obj["mp"].providertype)

        match_to_mastered_providers(app, session, mp_obj, mmp_objs, rules, now)
        matched = matched + 1

  session.commit()
  session.close()
  return matched, errors

