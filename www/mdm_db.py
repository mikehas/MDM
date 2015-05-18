from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import ConfigParser
config = ConfigParser.ConfigParser()
config.read('config/db_config.cfg')


engine = create_engine('mysql://'+config.get('db', 'USER')+':'+config.get('db','PASSWORD')+'@'+config.get('db','HOST')+':3306/'+config.get('db','DB'), convert_unicode=True)

#engine = create_engine('mysql://root:@localhost:3306/mhaskell', convert_unicode=True)

Session = sessionmaker(autocommit=False,
                       autoflush=False,
                       bind=engine)

Base = declarative_base()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import mdm_models
    Base.metadata.create_all(bind=engine)
