
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


#for configuration
from sqlalchemy import create_engine


Base = declarative_base()

class Log_table(Base):
   __tablename__ = 'payments'

   id = Column(Integer, primary_key=True)
   amount = Column(String(20))
   currency = Column(String(3))
   send_time = Column(String(25))
   payment_id = Column(String(25))
   description = Column(String(250))

#creates a create_engine instance at the bottom of the file
engine = create_engine('sqlite:///database.db')

Base.metadata.create_all(engine)