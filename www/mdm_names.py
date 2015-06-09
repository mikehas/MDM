import re
from mdm_models import *
from mdm_db import Session, safe_commit

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
  data = session.query(MasteredProvider.name).all()
  session.close()
  
  output = []
  clean_rgx = re.compile(BAD_CHARS)

  for r in data:
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
      app.logger.debug("Cleaning up long names..." + s[0])
      first.append(s[0])
      last.extend(s[1:-1])
      to_del.extend(range(0,len(s)))

    to_del, s = delete_used(to_del, s)

    row = [''] * 8
    row[0] = r[0]
    row[1] = ' '.join(prefixes)
    row[2] = ' '.join(first)
    row[3] = ' '.join(middle)
    row[4] = ' '.join(last)
    row[5] = ' '.join(suffixes)
    row[6] = ' '.join(credentials)
    row[7] = ' '.join(s) #unknowns

    output.append(row)

  return output

