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

def create_dict_from_file(file_name):
  f = open(file_name)
  d = {}
  for w in f.readlines():
    w = w.strip('-.,;:\r\n').upper()
    d[w] = w
  f.close()
  return d

def split_names(app):
  cred_d = create_dict_from_file("name_terms/credentials.txt")
  prefix_d = create_dict_from_file("name_terms/prefixes.txt")
  first_d = create_dict_from_file("name_terms/first.txt")
  last_d = create_dict_from_file("name_terms/last.txt")
  suffix_d = create_dict_from_file("name_terms/suffixes.txt")

  # Credential Regex to match consonants strings of 3 or more
  cred_r = re.compile(r'[^ ]([B-DF-HJ-NP-TVXZ]{3,})[ $]')

  session = Session()
  data = session.query(MasteredProvider.name).limit(1000)
  session.close()
  
  output = []

  for r in data:
    name = r[0]
    credential = cred_r.match(name)
    if credential is not None:
      row[6] = None
    
    s = name.split()
    credentials = []
    suffixes = []

    to_del = []
    
    # Find credentials, suffix
    for i, w in enumerate(s):
      w = w.strip('-.,;:/\r\n').upper()
      credential = cred_r.match(w)
      if credential is not None:
        app.logger.debug(credential.group())
        credentials.append(credential.group())
        to_del.append(i)
      elif cred_d.get(w) is not None:
        credentials.append(w)
        to_del.append(i)
      elif suffix_d.get(w) is not None:
        suffixes.append(w)
        to_del.append(i)

    # delete creds from word
    to_del = sorted(to_del, reverse=True)
    for i in to_del:
      del s[i]

    row = [''] * 7
    row[0] = r[0]
    #row[1] = None
    row[2] = ' '.join(s)
    #row[3] = None
    row[4] = ' '.join(suffixes)
    row[5] = ' '.join(credentials)
    output.append(row)

  return output


