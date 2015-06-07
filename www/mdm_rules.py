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
    fuzzy_vals = []
    has_type = None
    title = None
    for col, mode in rules_form.items():
      mode = mode.encode('ascii')
      app.logger.debug(col + ", "  + mode)
      if (str(i) + '_') in col[0:2]:
        if ('match_threshold' in strip_name(col)):
          add_to_col = re.sub(r'.*match_threshold_[0-9]+_', '', col)
          app.logger.debug("fuzzy val colname: " + add_to_col)
          fuzzy_vals.append((add_to_col, mode))
        elif ('_has_type' in col):
          if mode != 'both':
            has_type = mode
        elif ('title' in col):
          app.logger.debug("found title: " + mode)
          title = mode
        elif mode != 'ignore':
          col_dict = OrderedDict()
          col_dict['match_col'] = strip_name(col)
          col_dict['match_type'] = mode
          match_cols.append(col_dict)

    # Append Fuzzy Vals to appropriate column
    for fcol, fval in fuzzy_vals:
      for coldict in match_cols:
        if coldict['match_col'] == fcol:
          coldict['match_threshold'] = fval


    rule = OrderedDict()
    rule['title'] = title
    if has_type is not None:
      rule['has_type'] = has_type
    rule['match_cols'] = match_cols
    if len(match_cols) > 0:
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

