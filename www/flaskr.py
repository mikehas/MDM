import ConfigParser
from flaskext.mysql import MySQL
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

import mdm_schema

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
def home():
    return render_template('home.html')
 
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

def get_all_tables():
    cursor = mysql.connect().cursor()
    cursor.execute("SHOW TABLES;")
    data = cursor.fetchall()

    table_totals = []
    for i, table in enumerate(data):
      cursor = mysql.connect().cursor()
      cursor.execute("SELECT COUNT(*) FROM " + table[0])
      total = cursor.fetchone()
      table_totals.append(total)

    return zip(data, table_totals)

@app.route("/tables")
def show_tables():
    tables_data = get_all_tables()
    if tables_data is None:
      return "Unable to show tables..."
    else:
      return render_template('show_tables.html', tables_data=tables_data)

@app.route("/schema/setup")
def schema_setup():
    mdm_schema.exec_sql('scripts/DB-setup.sql')
    tables_data = get_all_tables()
    return render_template('show_tables.html', tables_data=tables_data)

@app.route("/schema/cleanup")
def schema_cleanup():
    mdm_schema.exec_sql('scripts/DB-cleanup.sql')
    tables_data = get_all_tables()
    return render_template('show_tables.html', tables_data=tables_data)

@app.route("/schema/refresh")
def schema_refresh():
    mdm_schema.exec_sql('scripts/DB-cleanup.sql')
    mdm_schema.exec_sql('scripts/DB-setup.sql')
    tables_data = get_all_tables()
    return render_template('show_tables.html', tables_data=tables_data)

@app.route("/data/load")
def data_load():
    mdm_schema.exec_sql('scripts/Specialties.sql')
    mdm_schema.exec_sql('scripts/RawData.sql')
    tables_data = get_all_tables()
    return render_template('show_tables.html', tables_data=tables_data)



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

