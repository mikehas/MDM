from flaskext.mysql import MySQL
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import logging
from logging.handlers import RotatingFileHandler 

import mdm_schema
import mdm_map
from mdm_db import engine

# create application
app = Flask(__name__)

# load configurations from os env variable
app.config.from_envvar("FLASKR_SETTINGS", silent=False)

@app.teardown_appcontext
def shutdown_session(exception=None):
      Session.remove()

# app urls

def get_columns(table):
    connection = engine.connect()
    result = connection.execute("show columns from " + table)
    connection.close()
    return result

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
 
    connection = engine.connect()
    data = connection.execute("SELECT * from " + table + " limit " + limit )
    connection.close()

    if data is None:
      return "Table ", table, "does not exist."
    else:
      return render_template('show_rows.html', entries=data, \
        columns=get_columns(table))

def get_all_tables():
    connection = engine.connect()
    data = connection.execute("SHOW TABLES;")
    connection.close()
    app.logger.debug(data)
    tables = data.fetchall()
    app.logger.debug(tables)

    table_totals = []
    for i, table in enumerate(tables):
      app.logger.debug('Table: ' + table[0])
      connection = engine.connect()
      data = connection.execute("SELECT COUNT(*) FROM " + table[0])
      count = data.fetchall()
      app.logger.debug(count)
      table_totals.append(count[0])
      connection.close()

    return zip(tables, table_totals)

@app.route("/tables")
def show_tables():
    tables_data = get_all_tables()
    if tables_data is None:
      return "Unable to show tables..."
    else:
      return render_template('show_tables.html', tables_data=tables_data)

@app.route("/table/truncate")
def truncate_table():
    table = request.args.get('table')
    
    if table is not None:
      connection = engine.connect()
      result = connection.execute("delete from " + table)
      connection.close()

      flash("Truncated table: " + table)
    else:
      flash("No table selected for truncation")

    tables_data = get_all_tables()
    if tables_data is None:
      return "Unable to show tables..."
    else:
      return render_template('show_tables.html', tables_data=tables_data)

@app.route("/schema/setup")
def schema_setup():
    mdm_schema.exec_sql('scripts/DB-setup.sql')
    tables_data = get_all_tables()
    flash('All tables created')
    return render_template('show_tables.html', tables_data=tables_data)

@app.route("/schema/cleanup")
def schema_cleanup():
    mdm_schema.exec_sql('scripts/DB-cleanup.sql')
    tables_data = get_all_tables()
    flash('All tables deleted.')
    return render_template('show_tables.html', tables_data=tables_data)

@app.route("/schema/refresh")
def schema_refresh():
    mdm_schema.exec_sql('scripts/DB-cleanup.sql')
    mdm_schema.exec_sql('scripts/DB-setup.sql')
    tables_data = get_all_tables()
    flash('All tables recreated.')
    return render_template('show_tables.html', tables_data=tables_data)

@app.route("/data/load")
def data_load():
    mdm_schema.exec_sql('scripts/Specialties.sql')
    mdm_schema.exec_sql('scripts/RawData.sql')
    tables_data = get_all_tables()
    flash("Specialty and RawData tables loaded with rawdata.")
    return render_template('show_tables.html', tables_data=tables_data)

@app.route("/data/map")
def data_map():
    mdm_map.map_all()

    return render_template('mapping_results.html')
'''
@app.route("/test/alchemy")
def test_alchemy():
    session = Session()
    rows = session.query(RawData).filter(RawData.sourceid.in_([1,2,3])).all()
    for row in rows:
      app.logger.debug(row.sourceid)
'''

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
  handler = RotatingFileHandler('logs/mdm.log', maxBytes=10000, backupCount=1)
  handler.setLevel(logging.INFO)
  app.logger.addHandler(handler)

  app.run()

