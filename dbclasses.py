# coding: utf-8

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

user_languages = Table('user_languages', Base.metadata,
  Column('user_id', Integer, ForeignKey('users.id')),
  Column('language_id', Integer, ForeignKey('languages.id'))
)

user_projects = Table('user_projects', Base.metadata,
  Column('user_id', Integer, ForeignKey('users.id')),
  Column('project_id', Integer, ForeignKey('projects.id'))
)

class User(Base):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String(50), nullable=False, index=True, unique=True)
  name = Column(String(50), nullable=False)
  email = Column(String(40), nullable=False)
  activated = Column(Boolean, nullable=False, server_default="0")
  activationcode = Column(String(128))
  passwdhash = Column(String(128))
  logintype = Column(String(20))
  siteadmin = Column(Boolean, nullable=False, server_default="0")
  viewrows = Column(Integer, nullable=False, server_default="10")
  translaterows = Column(Integer, nullable=False, server_default="10")
  uilanguage = Column(String(10), ForeignKey('languages.code'))
  altsrclanguage = Column(String(10), ForeignKey('languages.code'))

  projects = relation('Project', secondary=user_projects, backref='users')
  languages = relation('Language', secondary=user_languages, backref='users')

  def __init__(self, username=''):
    self.username = username 
    self.name = ''
    self.email = ''
    self.activated = False
    self.activationcode = None
    self.passwdhash = None
    self.logintype = None
    self.siteadmin = False 
    self.viewrows = 10
    self.translaterows = 10
    self.uilanguage = 'en'
    self.altsrclanguage = 'en'

  def __repr__(self):
    return "<User %s (%s) <%s>>" % (self.username, self.name, self.email)

  def suggestionsMadeCount(self):
    return len(self.suggestionsMade)

  def suggestionsAcceptedCount(self):
    return len(self.suggestionsAccepted)

  def suggestionsPendingCount(self):
    return len(self.suggestionsPending)

  def suggestionsRejectedCount(self):
    return len(self.suggestionsRejected)

  def suggestionsReviewedCount(self):
    return len(self.suggestionsReviewed)

  def submissionsCount(self):
    return len(self.submissions)

  def suggestionUsePercentage(self):
    accepted = self.suggestionsAcceptedCount()
    rejected = self.suggestionsRejectedCount()
    beenreviewed = accepted+rejected
    if beenreviewed == 0:
      return 0
    return 100 * accepted / beenreviewed 

class Language(Base):
  __tablename__ = 'languages'

  id = Column(Integer, primary_key=True)
  code = Column(String(10), nullable=False, unique=True)
  fullname = Column(String(50), nullable=False)
  nplurals = Column(Integer)
  pluralequation = Column(String(100))
  specialchars = Column(Unicode(100), server_default="")

  def __init__(self, code, fullname = "", nplurals = 1, pluralequation = "", specialchars=u""):
    self.code = code
    self.fullname = fullname 
    self.nplurals = nplurals 
    self.pluralequation = pluralequation 
    self.specialchars = specialchars

  def __repr__(self):
    return "<Language %s: %s>" % (self.code, self.fullname)

class Project(Base):
  __tablename__ = 'projects'

  id = Column(Integer, primary_key=True)
  code = Column(String(50), nullable=False, unique=True)
  fullname = Column(String(100), nullable=False)
  description = Column(Text)
  checkstyle = Column(String(50), nullable=False)
  localfiletype = Column(String(50), server_default="")
  createmofiles = Column(Boolean, server_default="0")
  treestyle = Column(String(20))
  ignoredfiles = Column(String(255), nullable=False)

  def __init__(self, code, fullname = "", description = "", checkstyle = "", localfiletype = "", createmofiles=False, treestyle="", ignoredfiles=""):
    self.code = code
    self.fullname = fullname 
    self.description = description 
    self.checkstyle = checkstyle 
    self.localfiletype = localfiletype 
    self.createmofiles = createmofiles
    self.treestyle = treestyle
    self.ignoredfiles = ignoredfiles

  def __repr__(self):
    return "<Project %s: %s>" % (self.code, self.fullname)

class Submission(Base):
  __tablename__ = 'submissions'

  # TODO The shared data (this through project) should be in its own parent
  # "Contribution" class
  id = Column(Integer, primary_key=True)
  creationTime = Column(DateTime)

  languageID = Column(Integer, ForeignKey('languages.id'))
  projectID = Column(Integer, ForeignKey('projects.id'))
  filename = Column(String(255))
  source = Column(UnicodeText)
  trans = Column(UnicodeText)

  language = relation(Language, backref='submissions')
  project = relation(Project, backref='submissions')

  submitterID = Column(Integer, ForeignKey('users.id'))
  submitter = relation(User, backref='submissions')

class Suggestion(Base):
  __tablename__ = 'suggestions'

  # TODO The shared data (this through project) should be in its own parent
  # "Contribution" class
  id = Column(Integer, primary_key=True)
  creationTime = Column(DateTime)

  languageID = Column(Integer, ForeignKey('languages.id'))
  projectID = Column(Integer, ForeignKey('projects.id'))
  filename = Column(String(255))
  source = Column(UnicodeText)
  trans = Column(UnicodeText)

  language = relation(Language, backref='suggestions')
  project = relation(Project, backref='suggestions')

  suggesterID = Column(Integer, ForeignKey('users.id'))
  
  reviewerID = Column(Integer, ForeignKey('users.id'))
  reviewStatus = Column(String(30), server_default="pending")
  reviewTime = Column(DateTime)
  reviewSubmissionID = Column(Integer, ForeignKey('submissions.id'))

  reviewSubmission = relation(Submission, backref=backref('fromsuggestion', uselist=False))

class Quickstat(Base):
  __tablename__ = 'quickstats'

  id = Column(Integer, primary_key=True, autoincrement=True)
  projectid = Column(String(100), ForeignKey('projects.id'))
  languageid = Column(String(100), ForeignKey('languages.id'))
  
  language = relation(Language, backref='quickstats')
  project = relation(Project, backref='quickstats')

  subdir = Column(String(100), nullable=False)
  filename = Column(String(100), nullable=False)
  
  translatedwords = Column(Integer)
  translated = Column(Integer)
  fuzzywords = Column(Integer)
  fuzzy = Column(Integer)
  totalwords = Column(Integer)
  total = Column(Integer)
 
User.uilanguageobj = relation(Language, primaryjoin=User.uilanguage==Language.code, backref='uiusers')
User.altsrclanguageobj = relation(Language, primaryjoin=User.altsrclanguage==Language.code, backref='altsrcusers')

Suggestion.suggester = relation(User, primaryjoin=Suggestion.suggesterID==User.id, backref='suggestionsMade')
Suggestion.reviewer = relation(User, primaryjoin=Suggestion.reviewerID==User.id, backref='suggestionsReviewed')

User.suggestionsAccepted = relation(Suggestion, primaryjoin=and_(Suggestion.suggesterID==User.id, Suggestion.reviewStatus=="accepted"))
User.suggestionsRejected = relation(Suggestion, primaryjoin=and_(Suggestion.suggesterID==User.id, Suggestion.reviewStatus=="rejected"))
User.suggestionsPending = relation(Suggestion, primaryjoin=and_(Suggestion.suggesterID==User.id, Suggestion.reviewStatus=="pending"))
