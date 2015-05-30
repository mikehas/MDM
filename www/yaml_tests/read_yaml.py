import yaml
import pprint

rfile = open("example_rules.yaml", 'r+')
pprint.pprint(yaml.load(rfile))
