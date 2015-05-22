from flaskext.mysql import MySQL
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

import logging.handlers

app = None

class App():
  def __init__(self):
    # create application
    global app
    self.app = Flask(__name__)
    # load configurations from os env variable
    self.app.config.from_envvar("FLASKR_SETTINGS", silent=False)

    handler = logging.handlers.RotatingFileHandler('logs/mdm.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)

    self.app.logger.addHandler(handler)

  def get(self):
    return self.app



