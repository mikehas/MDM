import subprocess

def exec_sql(sql_file):
  proc = subprocess.Popen(['mysql', '-u', 'root', 'mhaskell'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
  try:
    out, err = proc.communicate(file(sql_file).read())
  except subprocess.CalledProcessError, e:
    return "command error, cmd=" + str(e.cmd) \
     + " returncode=" + str(e.returncode) \
     + " output=" + str(e.output)
  return out
