import ConfigParser
from flaskext.mysql import MySQL
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

# create application
app = Flask(__name__)

# load configurations from os env variable
app.config.from_envvar("FLASKR_SETTINGS", silent=False)

mysql = MySQL()
mysql.init_app(app)

# app urls

def get_columns(table):
    cursor = mysql.connect().cursor()
    cursor.execute("SHOW COLUMNS FROM " + table )
    data = cursor.fetchall()
    return data

@app.route("/")
def hello():
    return "Welcome to Python Flask App!"
 
@app.route("/view")
def show_entries():
    table = request.args.get('table')
    limit = request.args.get('limit')
    if table == None:
      table = 'RawData'
    if limit == None:
      limit = '1000'
 
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from " + table + " limit " + limit )
    data = cursor.fetchall()
    if data is None:
      return "Table ", table, "does not exist."
    else:
      return render_template('show_rows.html', entries=data, \
        columns=get_columns(table))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == "__main__":
  app.run()

