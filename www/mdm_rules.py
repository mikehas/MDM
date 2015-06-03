import yaml
import re
from collections import OrderedDict
import collections

def load_rules(f):
  rfile = open(f, 'r+')
  output =  yaml.load(rfile)
  rfile.close()
  return output

def strip_name(name):
  return re.sub(r'^[0-9]+_', '', name)

def dict_representer(dumper, data):
    return dumper.represent_dict(data.iteritems())

def dict_constructor(loader, node):
    return collections.OrderedDict(loader.construct_pairs(node))

def write_yaml(app, f, rules_form):
  yamlfile = open(f, 'w+')
  y = []
  rules = []

  for name, value in rules_form.items():
    if '_title' in name:
      rules.append(name)

  rules.sort()
  r = []
  for i, val in enumerate(rules):
    match_cols = []
    for col, mode in rules_form.items():
      if (str(i) + '_') in col[0:2] and '_title' not in col:
        app.logger.debug("column: " + col + " mode: " + mode)
        col_dict = {}
        col_dict['match_col'] = strip_name(col)
        col_dict['match_type'] = mode.encode('ascii')
        match_cols.append(col_dict)
    rule = OrderedDict()
    rule['title'] = strip_name(val)
    rule['match_cols'] = match_cols
    r.append(rule)

  rules_dict = {'Rules': r}

  # http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
  # Export odered dictionary properly in YAML
  _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
  yaml.add_representer(collections.OrderedDict, dict_representer)
  yaml.add_constructor(_mapping_tag, dict_constructor)

  output =  yaml.dump(rules_dict, default_flow_style=False, allow_unicode=False)
  yamlfile.write(output)
  yamlfile.close()

