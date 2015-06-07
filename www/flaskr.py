from flaskext.mysql import MySQL
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import logging
from logging.handlers import RotatingFileHandler

import mdm_schema
import mdm_map
import mdm_match
from mdm_db import engine
import json
from mdm_models import *
import re
from pprint import pprint, pformat
import mdm_rules
import yaml
import time

import cProfile

# create application
app = Flask(__name__)

# load configurations from os env variable
app.config.from_envvar("FLASKR_SETTINGS", silent=False)

@app.teardown_appcontext
def shutdown_session(exception=None):
  try:
      Session.remove()
  except NameError, e:
      app.logger.info(e)

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

@app.route("/view/record")
def show_record():
    table = request.args.get('table')
    sourceid = request.args.get('sourceid')
    if table == None:
      table = 'RawData'
    if sourceid == None:
      sourceid = 1

    connection = engine.connect()
    data = connection.execute("SELECT * from " + table + " where sourceid = " + str(sourceid))
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
      connection = engine.connect()
      data = connection.execute("SELECT COUNT(*) FROM " + table[0])
      count = data.fetchall()
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
    mdm_schema.exec_sqlfile(app, 'scripts/DB-setup.sql')
    tables_data = get_all_tables()
    flash('All tables created')
    return render_template('show_tables.html', tables_data=tables_data)

@app.route("/schema/cleanup")
def schema_cleanup():
    mdm_schema.exec_sqlfile(app, 'scripts/DB-cleanup.sql')
    tables_data = get_all_tables()
    flash('All tables deleted.')
    return render_template('show_tables.html', tables_data=tables_data)

@app.route("/schema/refresh")
def schema_refresh():
    mdm_schema.exec_sqlfile(app, 'scripts/DB-cleanup.sql')
    mdm_schema.exec_sqlfile(app, 'scripts/DB-setup.sql')
    tables_data = get_all_tables()
    flash('All tables recreated.')
    return render_template('show_tables.html', tables_data=tables_data)

@app.route("/data/load")
def data_load():
    mdm_schema.exec_sqlfile(app, 'scripts/Specialties.sql')
    mdm_schema.exec_sqlfile(app, 'scripts/SpecialtiesNUCC.sql')
    mdm_schema.exec_sqlfile(app, 'scripts/RawData.sql')
    tables_data = get_all_tables()
    flash("Specialty and RawData tables loaded with rawdata.")
    return render_template('show_tables.html', tables_data=tables_data)

@app.route("/data/map")
def data_map():
    mapped, errors = mdm_map.map_all()
    flash(str(mapped - len(errors)) + " records mapped to MDM tables")
    return render_template('mapping_results.html', errors=errors)

def getAttributesToMatch(columns, ignore_columns, prefix):
    cols = []
    for item in columns:
      col = str(item).split('.')[1]
      if col not in ignore_columns:
        cols.append(col if prefix is None else (prefix + col))
    return cols

@app.route("/data/match_rules")
def data_match_rules():
    #MedicalProviders, Address, Phone

    ignore_cols = ['sourceid', 'addresstype', 'providertype', 'timestamp', 'message']
    cols = []

    cols.extend(getAttributesToMatch(MedicalProvider.__table__.columns, ignore_cols, None))
    cols.extend(getAttributesToMatch(Address.__table__.columns, ignore_cols, 'Practice '))
    cols.extend(getAttributesToMatch(Address.__table__.columns, ignore_cols, 'Mailing '))
    cols.append('Phone');

    flash("Select and modify the matching rules you would like to be executed.")
    return render_template('match_rules.html', columns=cols)

@app.route("/data/match_rules/save", methods = ['POST'])
def data_match_rules_save():
  app.logger.info(pformat(request.form))
  rules_form = request.form

  timestamp = time.strftime("%Y%m%d-%H%M%S")
  filename = "rules/ruleset_" + timestamp + ".yaml"
  mdm_rules.write_yaml(app, filename, rules_form)

  f = open(filename, 'r+')
  lines = f.readlines()
  for i, l in enumerate(lines):
    lines[i] = re.sub(' ', '&nbsp;', l)

  return render_template('show_rules.html', rules_file = filename, rules_lines = lines)

@app.route("/data/match")
def data_match():
    tables_data = get_all_tables()
    #matched, errors = mdm_match.match_all(app)
    cProfile.runctx('mdm_match.match_all(app)', {"mdm_match": mdm_match}, {"app": app})
    return render_template('matching_results.html', tables_data=tables_data)

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
            return redirect(url_for('show_tables'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_tables'))

if __name__ == "__main__":
  handler = RotatingFileHandler('logs/mdm.log', maxBytes=10000, backupCount=1)
  handler.setLevel(logging.DEBUG)
  app.logger.addHandler(handler)

  app.run()

