import subprocess
import ConfigParser
config = ConfigParser.ConfigParser()
config.read('config/db_config.cfg')

def exec_sql(sql_file):
  proc = subprocess.Popen(['mysql', '-u', config.get('db', 'USER'), '-p'+config.get('db','PASSWORD'), config.get('db','DB')], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
  try:
    out, err = proc.communicate(file(sql_file).read())
  except subprocess.CalledProcessError, e:
    return "command error, cmd=" + str(e.cmd) \
     + " returncode=" + str(e.returncode) \
     + " output=" + str(e.output)
  return out

