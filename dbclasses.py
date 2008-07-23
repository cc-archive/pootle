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
  username = Column(String(50), nullable=False, index=True)
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

  def __init__(self):
    self.username = ''
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
  specialcharacters = Column(Unicode(100), server_default="")

  def __init__(self, code, fullname = "", nplurals = 1, pluralequation = "", specialcharacters=""):
    self.code = code
    self.fullname = fullname 
    self.nplurals = nplurals 
    self.pluralequation = pluralequation 
    self.specialcharacters = specialcharacters

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

  def __init__(self, code, fullname = "", description = "", checkstyle = "", localfiletype = "", createmofiles=False, treestyle=""):
    self.code = code
    self.fullname = fullname 
    self.description = description 
    self.checkstyle = checkstyle 
    self.localfiletype = localfiletype 
    self.createmofiles = createmofiles
    self.treestyle = treestyle

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

User.uilanguageobj = relation(Language, primaryjoin=User.uilanguage==Language.code, backref='uiusers')
User.altsrclanguageobj = relation(Language, primaryjoin=User.altsrclanguage==Language.code, backref='altsrcusers')

Suggestion.suggester = relation(User, primaryjoin=Suggestion.suggesterID==User.id, backref='suggestionsMade')
Suggestion.reviewer = relation(User, primaryjoin=Suggestion.reviewerID==User.id, backref='suggestionsReviewed')

User.suggestionsAccepted = relation(Suggestion, primaryjoin=and_(Suggestion.suggesterID==User.id, Suggestion.reviewStatus=="accepted"))
User.suggestionsRejected = relation(Suggestion, primaryjoin=and_(Suggestion.suggesterID==User.id, Suggestion.reviewStatus=="rejected"))
User.suggestionsPending = relation(Suggestion, primaryjoin=and_(Suggestion.suggesterID==User.id, Suggestion.reviewStatus=="pending"))

def create_default_projects(s):
     
      pootle = Project(code = "pootle", fullname = "Pootle", description = "<div dir='ltr' lang='en'>Interface translations for Pootle. <br /> See the <a href='http://pootle.locamotion.org'>official Pootle server</a> for the translations of Pootle.</div>", checkstyle = "standard", localfiletype = "po")
      s.add(pootle)

      terminology = Project(code = "terminology", fullname = "Terminology", description = "<div dir='ltr' lang='en'>Terminology project that Pootle should use to suggest terms.<br />There might be useful terminology files on the <a href='http://pootle.locamotion.org/projects/terminology/'>official Pootle server</a>.</div>", checkstyle = "standard", localfiletype = "po")
      s.add(terminology)
    
def create_default_languages(s):
    af = Language("af")
    af.fullname = "Afrikaans"
    af.specialcharacters = "ëïêôûáéíóúý"
    af.nplurals = 2
    af.pluralequation = "(n != 1)"
    s.add(af)

# Akan
#    ak.fullname = u'Akan'
#    ak.pluralequation = u'(n > 1)'
#    ak.specialcharacters = "ɛɔƐƆ"
#    ak.nplurals = u'2'

# العربية
# Arabic
    ar = Language("ar")
    ar.fullname = u'Arabic'
    ar.nplurals = '6'
    ar.pluralequation ='n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5'
    s.add(ar)

# Azərbaycan
# Azerbaijani
#    az.fullname = u'Azerbaijani'
#    az.nplurals = '2'
#    az.pluralequation ='(n != 1)'

# Беларуская
# Belarusian
#    be.fullname = u'Belarusian'
#    be.nplurals = '3'
#    be.pluralequation ='(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'

# Български
# Bulgarian
#    bg.fullname = u'Bulgarian'
#    bg.nplurals = '2'
#    bg.pluralequation ='(n != 1)'

# বাংলা
# Bengali
#    bn.fullname = u'Bengali'
#    bn.nplurals = '2'
#    bn.pluralequation ='(n != 1)'

# Tibetan
#    bo.fullname = u'Tibetan'
#    bo.nplurals = '1'
#    bo.pluralequation ='0'

# Bosanski
# Bosnian
#    bs.fullname = u'Bosnian'
#    bs.nplurals = '3'
#    bs.pluralequation ='(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'

# Català
# Catalan
    ca = Language("ca")
    ca.fullname = u'Catalan; Valencian'
    ca.nplurals = '2'
    ca.pluralequation ='(n != 1)'
    s.add(ca)

# Česky
# Czech
    cs = Language("cs")
    cs.fullname = u'Czech'
    cs.nplurals = '3'
    cs.pluralequation ='(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2'
    s.add(cs)

# Cymraeg
# Welsh
#    cy.fullname = u'Welsh'
#    cy.nplurals = '2'
#    cy.pluralequation ='(n==2) ? 1 : 0'

# Dansk
# Danish
    da = Language("da")
    da.fullname = u'Danish'
    da.nplurals = '2'
    da.pluralequation ='(n != 1)'
    s.add(da)

# Deutsch
# German
    de = Language("de")
    de.fullname = u'German'
    de.nplurals = '2'
    de.pluralequation ='(n != 1)'
    s.add(de)

# ང་ཁ
# Dzongkha
#    dz.fullname = u'Dzongkha'
#    dz.nplurals = '1'
#    dz.pluralequation ='0'

# Ελληνικά
# Greek
#    el.fullname = u'Greek'
#    el.nplurals = '2'
#    el.pluralequation ='(n != 1)'

# English
    en = Language("en")
    en.fullname = u'English'
    en.nplurals = '2'
    en.pluralequation ='(n != 1)'
    s.add(en)

# English (United Kingdom)
#    en_GB.fullname = u'English (United Kingdom)'
#    en_GB.nplurals = '2'
#    en_GB.pluralequation ='(n != 1)'

# English (South Africa)
    en_ZA = Language("en_ZA")
    en_ZA.fullname = u'English (South Africa)'
    en_ZA.nplurals = '2'
    en_ZA.pluralequation ='(n != 1)'
    s.add(en_ZA)

# Esperanto
#    eo.fullname = u'Esperanto'
#    eo.nplurals = '2'
#    eo.pluralequation ='(n != 1)'

# Español
# Spanish
    es = Language("es")
    es.fullname = u'Spanish; Castilian'
    es.nplurals = '2'
    es.pluralequation ='(n != 1)'
    s.add(es)

# Eesti
# Estonian
#    et.fullname = u'Estonian'
#    et.nplurals = '2'
#    et.pluralequation ='(n != 1)'

# Euskara
# Basque
    eu = Language("eu")
    eu.fullname = u'Basque'
    eu.nplurals = '2'
    eu.pluralequation ='(n != 1)'
    s.add(eu)

# فارسی
# Persian
    fa = Language("fa")
    fa.fullname = u'Persian'
    fa.nplurals = '1'
    fa.pluralequation ='0'
    s.add(fa)

# Suomi
# Finnish
    fi = Language("fi")
    fi.fullname = u'Finnish'
    fi.nplurals = '2'
    fi.pluralequation ='(n != 1)'
    s.add(fi)

# Føroyskt
# Faroese
#    fo.fullname = u'Faroese'
#    fo.nplurals = '2'
#    fo.pluralequation ='(n != 1)'

# Français
# French
    fr = Language("fr")
    fr.fullname = u'French'
    fr.nplurals = '2'
    fr.pluralequation ='(n > 1)'
    s.add(fr)

# Furlan
# Friulian
    fur = Language("fur")
    fur.fullname = u'Friulian'
    fur.nplurals = '2'
    fur.pluralequation ='(n != 1)'
    s.add(fur)

# Frysk
# Frisian
#    fy.fullname = u'Western Frisian'
#    fy.nplurals = '2'
#    fy.pluralequation ='(n != 1)'

# Gaeilge
# Irish
#    ga.fullname = u'Irish'
#    ga.nplurals = '3'
#    ga.pluralequation ='n==1 ? 0 : n==2 ? 1 : 2'

# Galego
# Galician
    gl = Language("gl")
    gl.fullname = u'Galician'
    gl.nplurals = '2'
    gl.pluralequation ='(n != 1)'
    s.add(gl)

# ગુજરાતી
# Gujarati
#    gu.fullname = u'Gujarati'
#    gu.nplurals = '2'
#    gu.pluralequation ='(n != 1)'

# עברית
# Hebrew
#    he.fullname = u'Hebrew'
#    he.nplurals = '2'
#    he.pluralequation ='(n != 1)'

# हिन्दी
# Hindi
#    hi.fullname = u'Hindi'
#    hi.nplurals = '2'
#    hi.pluralequation ='(n != 1)'

# Hrvatski
# Croatian
#    hr.fullname = u'Croatian'
#    hr.nplurals = '3'
#    hr.pluralequation ='(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'

# Magyar
# Hungarian
    hu = Language("hu")
    hu.fullname = u'Hungarian'
    hu.nplurals = '2'
    hu.pluralequation ='(n !=1)'
    s.add(hu)

# Bahasa Indonesia
# Indonesian
    id = Language("id")
    id.fullname = u'Indonesian'
    id.nplurals = '1'
    id.pluralequation ='0'
    s.add(id)

# Icelandic
    islang = Language("is")
    islang.fullname = u'Icelandic'
    islang.nplurals = '2'
    islang.pluralequation = '(n != 1)'
    s.add(islang)

# Italiano
# Italian
    it = Language("it")
    it.fullname = u'Italian'
    it.nplurals = '2'
    it.pluralequation ='(n != 1)'
    s.add(it)

# 日本語 
# Japanese
    ja = Language("ja")
    ja.fullname = u'Japanese'
    ja.nplurals = '1'
    ja.pluralequation ='0'
    s.add(ja)

# ქართული
# Georgian
    ka = Language("ka")
    ka.fullname = u'Georgian'
    ka.nplurals = '1'
    ka.pluralequation ='0'
    s.add(ka)

# ភាសា
# Khmer
#    km.fullname = u'Khmer'
#    km.nplurals = '1'
#    km.pluralequation ='0'

# 한국어
# Korean
    ko = Language("ko")
    ko.fullname = u'Korean'
    ko.nplurals = '1'
    ko.pluralequation ='0'
    s.add(ko)

# Kurdî / كوردي
# Kurdish
#    ku.fullname = u'Kurdish'
#    ku.nplurals = '2'
#    ku.pluralequation ='(n!= 1)'

# Lëtzebuergesch
# Letzeburgesch
#    lb.fullname = u'Letzeburgesch'
#    lb.nplurals = '2'
#    lb.pluralequation ='(n != 1)'

# Lietuvių
# Lithuanian
    lt = Language("lt")
    lt.fullname = u'Lithuanian'
    lt.nplurals = '3'
    lt.pluralequation ='(n%10==1 && n%100!=11 ? 0 : n%10>=2 && (n%100<10 || n%100>=20) ? 1 : 2)'
    s.add(lt)

# Latviešu
# Latvian
#    lv.fullname = u'Latvian'
#    lv.nplurals = '3'
#    lv.pluralequation ='(n%10==1 && n%100!=11 ? 0 : n != 0 ? 1 : 2)'

# Malayalam
    ml = Language("ml")
    ml.fullname = u'Malayalam'
    ml.nplurals = '2'
    ml.pluralequation = '(n != 1)'
    s.add(ml)

# Malagasy
#    mg.fullname = u'Malagasy'
#    mg.nplurals = '2'
#    mg.pluralequation ='(n > 1)'

# Монгол
# Mongolian
#    mn.fullname = u'Mongolian'
#    mn.nplurals = '2'
#    mn.pluralequation ='(n != 1)'

# Marathi
#    mr.fullname = u'Marathi'
#    mr.nplurals = u'2'
#    mr.pluralequation = u'(n != 1)'

# Malay
#    ms.fullname = u'Malay'
#    ms.nplurals = u'1'
#    ms.pluralequation = u'0'

# Malti
# Maltese
    mt = Language("mt")
    mt.fullname = u'Maltese'
    mt.nplurals = '4'
    mt.pluralequation ='(n==1 ? 0 : n==0 || ( n%100>1 && n%100<11) ? 1 : (n%100>10 && n%100<20 ) ? 2 : 3)'
    s.add(mt)

# Nahuatl
#    nah.fullname = u'Nahuatl'
#    nah.nplurals = '2'
#    nah.pluralequation ='(n != 1)'

# Bokmål
# Norwegian Bokmal
#    nb.fullname = u'Norwegian Bokmal'
#    nb.nplurals = '2'
#    nb.pluralequation ='(n != 1)'

# Nepali
#    ne.fullname = u'Nepali'
#    ne.nplurals = u'2'
#    ne.pluralequation = u'(n != 1)'

# Nederlands
# Dutch
    nl = Language("nl")
    nl.fullname = u'Dutch; Flemish'
    nl.nplurals = '2'
    nl.pluralequation ='(n != 1)'
    s.add(nl)

# Nynorsk
# Norwegian Nynorsk
#    nn.fullname = u'Norwegian Nynorsk'
#    nn.nplurals = '2'
#    nn.pluralequation ='(n != 1)'

# Sesotho sa Leboa
# Northern Sotho
#    nso.fullname = u'Northern Sotho'
#    nso.nplurals = '2'
#    nso.pluralequation ='(n > 1)'
#    nso.specialcharacters = "šŠ"

# Oriya
#    or.fullname = u'Oriya'
#    or.nplurals = '2'
#    or.pluralequation ='(n != 1)'

# Punjabi
#    pa.fullname = u'Panjabi; Punjabi'
#    pa.nplurals = '2'
#    pa.pluralequation ='(n != 1)'

# Papiamento
#    pap.fullname = u'Papiamento'
#    pap.nplurals = '2'
#    pap.pluralequation ='(n != 1)'

# Polski
# Polish
    pl = Language("pl")
    pl.fullname = u'Polish'
    pl.nplurals = '3'
    pl.pluralequation ='(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
    s.add(pl)

# Português
# Portuguese
    pt = Language("pt")
    pt.fullname = u'Portuguese'
    pt.nplurals = '2'
    pt.pluralequation ='(n != 1)'
    s.add(pt)

# Português do Brasil
# Brazilian Portuguese
    pt_BR = Language("pt_BR")
    pt_BR.fullname = u'Portuguese (Brazil)'
    pt_BR.nplurals = '2'
    pt_BR.pluralequation ='(n > 1)'
    s.add(pt_BR)

# Română
# Romanian
    ro = Language("ro")
    ro.fullname = u'Romanian'
    ro.nplurals = '3'
    ro.pluralequation ='(n==1 ? 0 : (n==0 || (n%100 > 0 && n%100 < 20)) ? 1 : 2);'
    s.add(ro)

# Русский
# Russian
    ru = Language("ru")
    ru.fullname = u'Russian'
    ru.nplurals = '3'
    ru.pluralequation ='(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
    s.add(ru)

# Slovenčina
# Slovak
    sk = Language("sk")
    sk.fullname = u'Slovak'
    sk.nplurals = '3'
    sk.pluralequation ='(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2'
    s.add(sk)

# Slovenščina
# Slovenian
    sl = Language("sl")
    sl.fullname = u'Slovenian'
    sl.nplurals = '4'
    sl.pluralequation ='(n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || n%100==4 ? 2 : 3)'
    s.add(sl)

# Shqip
# Albanian
#    sq.fullname = u'Albanian'
#    sq.nplurals = '2'
#    sq.pluralequation ='(n != 1)'

# Српски / Srpski
# Serbian
    sr = Language("sr")
    sr.fullname = u'Serbian'
    sr.nplurals = '3'
    sr.pluralequation ='(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
    s.add(sr)

# Sesotho
# Sotho
    st = Language("st")
    st.fullname = u'Sotho, Southern'
    st.nplurals = '2'
    st.pluralequation ='(n != 1)'
    s.add(st)

# Svenska
# Swedish
    sv = Language("sv")
    sv.fullname = u'Swedish'
    sv.nplurals = '2'
    sv.pluralequation ='(n != 1)'
    s.add(sv)

# தமிழ்
# Tamil
#    ta.fullname = u'Tamil'
#    ta.nplurals = '2'
#    ta.pluralequation ='(n != 1)'

# Туркмен / تركمن
# Turkmen
#    tk.fullname = u'Turkmen'
#    tk.nplurals = '2'
#    tk.pluralequation ='(n != 1)'

# Türkçe
# Turkish
    tr = Language("tr")
    tr.fullname = u'Turkish'
    tr.nplurals = '1'
    tr.pluralequation ='0'
    s.add(tr)

# Українська
# Ukrainian
    uk = Language("uk")
    uk.fullname = u'Ukrainian'
    uk.nplurals = '3'
    uk.pluralequation ='(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
    s.add(uk)
 
# Tshivenḓa
# Venda
#    ve.fullname = u'Venda'
#    ve.nplurals = '2'
#    ve.pluralequation ='(n != 1)'
#    ve.specialcharacters = "ḓṋḽṱ ḒṊḼṰ ṅṄ"

# Vietnamese
    vi = Language("vi")
    vi.fullname = u'Vietnamese'
    vi.nplurals = '1'
    vi.pluralequation ='0'
    s.add(vi)

# Wolof
    wo = Language("wo")
    wo.fullname = u'Wolof'
    wo.nplurals = '2'
    wo.pluralequation ='(n != 1)'
    s.add(wo)

# Walon
# Walloon
#    wa.fullname = u'Waloon'
#    wa.nplurals = '2'
#    wa.pluralequation ='(n > 1)'

# 简体中文
# Simplified Chinese (China mainland used below, but also used in Singapore and Malaysia)
    zh_CN = Language("zh_CN")
    zh_CN.fullname = u'Chinese (China)'
    zh_CN.nplurals = '1'
    zh_CN.pluralequation ='0'
    zh_CN.specialcharacters = "←→↔×÷©…—‘’“”【】《》"
    s.add(zh_CN)

# 繁體中文
# Traditional Chinese (Hong Kong used below, but also used in Taiwan and Macau)
    zh_HK = Language("zh_HK")
    zh_HK.fullname = u'Chinese (Hong Kong)'
    zh_HK.nplurals = '1'
    zh_HK.pluralequation ='0'
    zh_HK.specialcharacters = "←→↔×÷©…—‘’“”「」『』【】《》"
    s.add(zh_HK)

# 繁體中文
# Traditional Chinese (Taiwan used below, but also used in Hong Kong and Macau)
    zh_TW = Language("zh_TW")
    zh_TW.fullname = u'Chinese (Taiwan)'
    zh_TW.nplurals = '1'
    zh_TW.pluralequation ='0'
    zh_TW.specialcharacters = "←→↔×÷©…—‘’“”「」『』【】《》"
    s.add(zh_TW)

# This is a "language" that gives people access to the (untranslated) template files
    templates = Language("templates")
    templates.fullname = u'Templates'
    s.add(templates)
