from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String(50), nullable=False, index=True)
  name = Column(String(50), nullable=False)
  email = Column(String(40), nullable=False)
  activated = Column(Boolean, nullable=False, server_default="0")
  activationcode = Column(String(128))
  passwdhash = Column(String(128))
  logintype = Column(String(20))
  siteadmin = Column(Boolean, nullable=False, server_default="0")
  projects = Column(String(255), nullable=False, server_default="")
  languages = Column(String(255), nullable=False, server_default="")
  viewrows = Column(Integer, nullable=False, server_default="10")
  translaterows = Column(Integer, nullable=False, server_default="10")
  uilanguage = Column(String(20), nullable=False, server_default="en")
  suggestionsmade = Column(Integer, nullable=False, server_default="0")
  suggestionsused = Column(Integer, nullable=False, server_default="0")
  submissionsmade = Column(Integer, nullable=False, server_default="0")

  def __init__(self):
    self.username = ''
    self.name = ''
    self.email = ''
    self.activated = False
    self.activationcode = None
    self.passwdhash = None
    self.logintype = None
    self.siteadmin = False 
    self.projects = "" 
    self.languages = "" 
    self.viewrows = 10
    self.translaterows = 10
    self.uilanguage = 'en'
    self.suggestionsmade = 0
    self.suggestionsused = 0
    self.submissionsmade = 0

  def __repr__(self):
    return "<User %s (%s) <%s>>" % (self.username, self.name, self.email)

  def suggestionusepercentage(self):
    if self.suggestionsmade == 0:
      return 0
    return 100 * self.suggestionsused / self.suggestionsmade
