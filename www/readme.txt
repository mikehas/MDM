http://stackoverflow.com/questions/22697440/cc-failed-with-exit-status-1-error-when-install-python-library


pip install Flask
pip install Flask-mysql
pip install SQLAlchemy

set env
FLASKR_SETTINGS=.../MDM/www/config.cfg

Set the configs under the configuration directory by copying the .dist files to new files without .dist.  Then fill out the appropriate settings.

http://docs.sqlalchemy.org/en/latest/core/connections.html
http://docs.sqlalchemy.org/en/improve_toc/orm/tutorial.html#declare-a-mapping
http://docs.sqlalchemy.org/en/improve_toc/orm/tutorial.html#creating-a-session
http://flask.pocoo.org/docs/0.10/patterns/sqlalchemy/

5/15/15 - Schema setup, cleanup, refresh, loading data, and mapping addresses and providers is working.
 
