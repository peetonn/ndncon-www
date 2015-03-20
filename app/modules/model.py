
import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr

class classproperty(object):
	def __init__(self, f):
		self.f = f
	def __get__(self, obj, owner):
		return self.f(owner)

class Base(object):
	@declared_attr
	def __tablename__(cls):
		return cls.__name__.lower()

	id =  Column(Integer, primary_key=True)

	@classproperty
	def query(self):
		return session.query(Session)

engine = create_engine('sqlite:///db/main.db')
Base = declarative_base(cls=Base)

class Report(Base):
	# __tablename__ = 'reports'

	user = Column(String(120))
	stream = Column(String(120))
	summary = Column(String(4096))
	logPath = Column(String(1024))
	reportType = Column(String)
	session_id = Column(Integer, ForeignKey('session.id'))

	def __repr__(self):
		return "<Report %r (user %r stream %r)>" % (self.id, self.user, self.stream)

class Session(Base):
	# __tablename__ = 'sessions'

	timestamp = Column(Integer)
	user = Column(String(120))
	folderPath = Column(String(1024))
	reports = relationship("Report", order_by="Report.id", backref="session")
	lastSeen = Column(DateTime)

	def time(self):
		return datetime.datetime.fromtimestamp(self.timestamp)

	def consumerReports(self):
		return [r for r in self.reports if r.reportType == 'consumer']

	def producerReports(self):
		return [r for r in self.reports if r.reportType == 'producer']

	def __repr__(self):
		return "<Session %r (user %r timestamp %r (%r))>" % (self.id, self.user, self.timestamp, datetime.datetime.fromtimestamp(self.timestamp))

Base.metadata.create_all(engine)
DbSession = sessionmaker(bind=engine)
session = DbSession()
db = session