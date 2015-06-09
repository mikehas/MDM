import re
from mdm_models import *
from mdm_db import Session, safe_commit
import collections

'''
First Name, Last Name
First Name, Last Name, Middle Intial
First Name, Last Name, Middle Name
First Name, Last Name, Medical Cred
First Name, Middle Initial, Last Name, 
First Name, Middle Initial, Last Name, Last Name
First Name, Middle Name, Last Name, 
First Name, Last Name, Last Name
First Name, Last Name - Last Name
First Name, Middle Initial, Last Name, 
First Initial, Middle Name, Last Name, Medical Cred (D Joanne Lynne MD)
Medical Cred+, First Initial, Last Name
Medical Cred, First Name, Last Name
Medical Cred, First Name, Middle Initial, Last Name
Medical Cred, First Name, Middle Name, Last Name
Medical Cred, Medical Cred, First Name
Medical Cred, First Name, Middle Initial, Medical Cred, Last Name
Medical Cred, First Name, Middle Initial, Last Name, Name Suffix (Jr)
Ivonne De L Fraga Berrios
FirstName, First Name, Middle Initial, Last Name, Lastname
'''

class OrderedSet(collections.MutableSet):
    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

BAD_CHARS = '[- .,;:/\r\n>]'

def create_dict_from_file(file_name):
  f = open(file_name)
  d = {}
  clean_rgx = re.compile(BAD_CHARS)
  for w in f.readlines():
    w = clean_rgx.sub('', w).upper()
    d[w] = w
  f.close()
  return d

def delete_used(to_del, s):
    to_del = sorted(to_del, reverse=True)
    for i in to_del:
      del s[i]
    to_del = []
    return to_del, s

def clean(obj):
  return '' if obj is None else str(obj)

def get_phone(app, session, m_id):
  phone = session.query(Phone.cleanphone).join(MatchedPhone, MatchedPhone.sourceid == Phone.sourceid).filter(MatchedPhone.masterid == m_id).first()
  if phone is None:
    phone = ['']
  return phone

def get_primary_specialty(app, session, m_id):
  result = session.query(MatchedPrimarySpecialty.specialty).filter(MatchedPrimarySpecialty.masterid == m_id).first()
  if result is None:
    result = ['']
  return result

def get_secondary_specialty(app, session, m_id):
  result = session.query(MatchedSecondarySpecialty.specialty).filter(MatchedSecondarySpecialty.masterid == m_id).first()
  if result is None:
    result = ['']
  return result

def save_names(app, f_name):
  f = open(f_name, 'w+')
  session = Session()
  m_ids = session.query(MasteredProvider.masterid).order_by(MasteredProvider.masterid).all()
  types = session.query(MasteredProvider.providertype).order_by(MasteredProvider.masterid).all()
  names = split_names(app)
  genders = session.query(MasteredProvider.gender).order_by(MasteredProvider.masterid).all()
  dobs = session.query(MasteredProvider.dateofbirth).order_by(MasteredProvider.masterid).all()
  proprietors = session.query(MasteredProvider.issoleproprietor).order_by(MasteredProvider.masterid).all()

  columns = ['Master ID', 'Provider Type', 'Name Prefix', 'First Name', 'Middle Name', 'Last Name', 'Name Suffix', 'Medical Credential', 'Gender', 'Date of Birth', 'Is Sole Proprietor', 'Primary Phone', 'Primary Specialty', 'Secondary Specialty']

  f.write('\t'.join(columns)+'\n')
  for m_id, m_type, name, gender, dob, proprietor  in \
   zip(m_ids, types, names, genders, dobs, proprietors):

    phone = get_phone(app, session, clean(m_id[0]))
    p_special = get_primary_specialty(app, session, clean(m_id[0]))
    s_special = get_secondary_specialty(app, session, clean(m_id[0]))

    f.write(clean(m_id[0]) + '\t' + clean(m_type[0]) + '\t' + name[1] +\
      '\t' + name[2] + '\t' + name[3] + '\t' + name[4] + '\t' + name[5] +\
      '\t' + name[6] + '\t' + clean(gender[0]) + '\t' + clean(dob[0]) +\
      '\t' + clean(proprietor[0]) + '\t' + clean(phone[0]) + '\t' + clean(p_special[0]) +\
      '\t' + clean(s_special[0]) + '\n' )
  f.close()

  return names

def split_names(app):
  cred_d = create_dict_from_file("name_terms/credentials.txt")
  prefix_d = create_dict_from_file("name_terms/prefixes.txt")
  first_d = create_dict_from_file("name_terms/first.txt")
  last_d = create_dict_from_file("name_terms/last.txt")
  suffix_d = create_dict_from_file("name_terms/suffixes.txt")

  # Credential Regex to match consonants strings of 3 or more
  cred_r = re.compile(r'(^[B-DF-HJ-NP-TV-XZ]{3,}$)')
  cred_r2 = re.compile(r'(?:.*\s|^)(PA- C|MSN F|P A|R EEG\/EP|APN C|F N P|P C|A M D|D P M|M D|D D S|PHARM D|PSY D|O D|D O|C N P|AT C|P L|L M S W|L AC|M ED|PA C|P A C|M DIV|R PH|R N N P|COTA \/L|PA -C|RN C|O\. D\.|D C|R EP T|M\. D\.|NCAC I|M S|M OF ED|M B B S|PH D)(?:\s.*|$)')

  session = Session()
  data = session.query(MasteredProvider.name).order_by(MasteredProvider.masterid).all()
  m_ids = session.query(MasteredProvider.masterid).order_by(MasteredProvider.masterid).all()

  session.close()
  
  output = []
  clean_rgx = re.compile(BAD_CHARS)

  for m_id, r in zip(m_ids, data):
    name = r[0].strip()
    name = re.sub(' - ', '-', name)
    credentials = []
    prefixes = []
    suffixes = []
    to_del = []
    last = []
    first = []
    middle = []

    # Merge N E L S O N
    name = re.sub('N E L S O N', 'NELSON',name)
    name = re.sub('N E A L O N', 'NEALON',name)

    # Deal with M D, D D S
    name = re.sub(r'[><]', '', name)
    credential = cred_r2.match(name.upper())
    while credential != None:
      c = credential.group(1)
      name = re.sub(c.upper(), '', name.upper())
      credentials.append(re.sub(' ','', c))
      credential = cred_r2.match(name)

    s = name.split()
    
    # Find credentials, suffix
    for i, w in enumerate(s):
      w = clean_rgx.sub('', w).upper()
      credential = cred_r.match(w)
      if credential is not None:
        credentials.append(credential.group())
        to_del.append(i)
      elif cred_d.get(w) is not None:
        credentials.append(w)
        to_del.append(i)
      elif suffix_d.get(w) is not None:
        suffixes.append(w)
        to_del.append(i)
      elif prefix_d.get(w) is not None:
        prefixes.append(w)
        to_del.append(i)
   
    # delete used words
    to_del, s = delete_used(to_del, s)

    # only name sequences remaining
    for i, w in enumerate(s):
      w = clean_rgx.sub('', w).upper()

      # I is a suffix if it as the end of a name sequence
      if w == 'I' and i == len(s) - 1:
        suffixes.append(w)
        to_del.append(i)

    # delete used words
    to_del, s = delete_used(to_del, s)

    # Remove tokens with numbers or non-names
    for i, w in enumerate(s):
      w = clean_rgx.sub('', w).upper()
      if bool(re.search(r'\d', w)) or bool(re.search(r'ADDRESS|LOCATION', w)):
        to_del.append(i)
    to_del, s = delete_used(to_del, s)
    
    # Deal with 2 word names
    if len(s) == 1:
      last.append(s[0])
      to_del.append(0)
    # Deal with 2 word names
    elif len(s) == 2:
      if len(s[0]) == 1:
        first.append(s[0])
        last.append(s[1])
      elif len(s[1]) == 1:
        middle.append(s[1])
        last.append(s[0])
      else:
        first.append(s[0])
        last.append(s[1])
      to_del.extend([0,1])

    # Deal with 3 word names
    elif len(s) == 3:
      first.append(s[0])
      middle.append(s[1])
      last.append(s[2])
      to_del.extend([0,1,2])

    # Deal with 4 word names
    elif len(s) == 4:
      if len(s[2]) == 1:
        first.extend([s[0], s[1]])
        middle.append(s[2])
        last.append(s[3])
        to_del.extend([0,1,2,3])
      elif len(s[1]) == 1:
        first.append(s[0])
        middle.append(s[1])
        last.extend([s[2],s[3]])
        to_del.extend([0,1,2,3])

    to_del, s = delete_used(to_del, s)

    # Default behavior for long names
    if len(s) > 0:
      first.append(s[0])
      last.extend(s[1:-1])
      to_del.extend(range(0,len(s)))

    to_del, s = delete_used(to_del, s)

    row = [''] * 7
    row[0] = str(m_id[0])
    row[1] = ' '.join(prefixes)
    row[2] = ' '.join(first)
    row[3] = ' '.join(middle)
    row[4] = ' '.join(last)
    row[5] = ' '.join(suffixes)
    row[6] = ' '.join(OrderedSet(credentials))

    output.append(row)

  return output

