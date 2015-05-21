import subprocess
import ConfigParser
from mdm_db import engine
from flask import flash

config = ConfigParser.ConfigParser()
config.read('config/db_config.cfg')

def exec_sql(app, sql_file):
  proc = subprocess.Popen(['mysql', '-u', config.get('db', 'USER'), '-p'+config.get('db','PASSWORD'), config.get('db','DB')], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
  try:
    out, err = proc.communicate(file(sql_file).read())
  except subprocess.CalledProcessError, e:
    message = "command error, cmd=" + str(e.cmd) \
     + " returncode=" + str(e.returncode) \
     + " output=" + str(e.output)
    app.logger.error(message)
    out = message
    err = 1
  except IOError, e:
    message = str(e) + sql_file
    app.logger.error(message)
    out = str(message)
    err = 1

  if out != '':
    flash(out)
  return out, err

def exec_sqlfile(app, sql_file):
    with open (sql_file, "r") as f:
      sql=f.read()

      connection = engine.connect()
      result = connection.execute(sql)
      connection.close()

      app.logger.debug(sql)
      app.logger.debug(result)

    return result


