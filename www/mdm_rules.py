import yaml

def load_rules(f):
  rfile = open(f, 'r+')
  output =  yaml.load(rfile)
  rfile.close()
  return output

