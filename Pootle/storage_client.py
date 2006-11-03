# This file is supposed to have all translation accessing functions in Pootle,
# at least the web portal part of it.

from Pootle.conf import instance, potree
from Pootle.utils import shortdescription
from gettext import gettext as _

def getstats(project, projectstats, numfiles):
    """returns a list with the data items to fill a statistics table
    Remember to update getstatsheadings() above as needed"""
    wanted = ["translated", "fuzzy", "untranslated", "total"]
    gotten = {}
    for key in wanted:
        gotten[key] = projectstats.get(key, [])
        wordkey = key + "words"
        if wordkey in projectstats:
            gotten[wordkey] = projectstats[wordkey]
        else:
            count = projectstats.get(key, [])
            gotten[wordkey] = project.countwords(count)
        if isinstance(gotten[key], list):
            #TODO: consider carefully:
            gotten[key] = len(gotten[key])
    gotten["untranslated"] = gotten["total"] - gotten["translated"] - gotten["fuzzy"]
    gotten["untranslatedwords"] = gotten["totalwords"] - gotten["translatedwords"] - gotten["fuzzywords"]

    for key in wanted[:-1]:
        percentkey = key + "percentage"
        wordkey = key + "words"
        gotten[percentkey] = gotten[wordkey]*100/max(gotten["totalwords"], 1)

    for key in gotten:
        if key.find("check-") == 0:
            value = gotten.pop(key)
            gotten[key[len("check-"):]] = value

    return gotten

## users.py
def getlanguageselector(languagenames, session):
    """returns the language selector..."""
    # TODO: work out how we handle localization of language names...
    languageoptions = [('', session.localize("Default"))]
    if isinstance(languagenames, dict):
        languageoptions += languagenames.items()
    else:
        languageoptions += languagenames
    return [{"code": key, "name": value, "selected": key==session.language or None} for key, value in languageoptions]

def getprojectoptions(session):
    """gets the options box to change the user's projects"""
    projectoptions = []
    userprojects = session.getprojects()
    for projectcode in potree().getprojectcodes():
      projectname = potree().getprojectname(projectcode)
      projectoptions.append({"code": projectcode, "name": projectname, "selected": projectcode
 in userprojects or None})
    return projectoptions

def getlanguageoptions(session):
    """returns options for languages"""
    userlanguages = session.getlanguages()
    languageoptions = potree().getlanguages()
    languages = []
    for language, name in languageoptions:
      languages.append({"code": language, "name": name, "selected": language in userlanguages
or None})
    return languages

def getotheroptions(session):
    uilanguage = getattr(session.prefs, "uilanguage", "")
    if not uilanguage:
      userlanguages = session.getlanguages()
      if userlanguages:
        uilanguage = userlanguages[0]
    languageoptions = [{"code": '', "name": ''}]
    for code, name in potree().getlanguages():
      languageoptions.append({"code": code, "name": name, "selected": uilanguage == code or None})
    options = {
        "inputheight": _("Input Height (in lines)"),
        "inputwidth": _("Input Width (in characters)"),
        "viewrows": _("Number of rows in view mode"),
        "translaterows": _("Number of rows in translate mode")}
    optionlist = []
    for option, description in options.items():
      optionvalue = getattr(session.prefs, option, "")
      optionlist.append({"code": option, "description": description, "value": optionvalue})
    return {"uilanguage": uilanguage, "uilanguage_options": languageoptions, "other_options": optionlist}

# indexpage.py
def getprojects():
    """gets the options for the projects"""
    projects = []
    for projectcode in potree().getprojectcodes():
      projectname = potree().getprojectname(projectcode)
      description = shortdescription(potree().getprojectdescription(projectcode))
      projects.append({"code": projectcode, "name": projectname, "description": description, "sep": ", "})
    if projects:
      projects[-1]["sep"] = ""
    return projects

def getprojectnames():
    return [potree().getprojectname(projectcode) for projectcode in potree().getprojectcodes()]

def getquicklinks(session):
    """gets a set of quick links to user's project-languages"""
    quicklinks = []
    for languagecode in session.getlanguages():
      if not potree().haslanguage(languagecode):
        continue
      languagename = potree().getlanguagename(languagecode)
      langlinks = []
      for projectcode in instance().session.getprojects():
        if potree().hasproject(languagecode, projectcode):
          projectname = potree().getprojectname(projectcode)
          projecttitle = projectname
          langlinks.append({"code": projectcode, "name": projecttitle, "sep": "<br />"})
      if langlinks:
        langlinks[-1]["sep"] = ""
      quicklinks.append({"code": languagecode, "name": languagename, "projects": langlinks})
    return quicklinks

def getprojects_languageindex(languagecode):
    """gets the info on the projects"""
    projectcodes = potree().getprojectcodes(languagecode)
    projectcount = len(projectcodes)
    projectitems = [getprojectitem(projectcode, languagecode) for projectcode in projectcodes]
    for n, item in enumerate(projectitems):
      item["parity"] = ["even", "odd"][n % 2]
    return projectitems

def getprojectcount(languagecode):
    return len(potree().getprojectcodes(languagecode))

def getlanguages(projectcode):
    """gets the stats etc of the languages"""
    languages = potree().getlanguages(projectcode)
    languagecount = len(languages)
    languageitems = [getlanguageitem(languagecode, languagename, projectcode) for languagecode, languagename in languages]
    for n, item in enumerate(languageitems):
      item["parity"] = ["even", "odd"][n % 2]
    return languageitems

def getlanguageinfo(languagecode):
    try:
        nplurals = potree().getlanguagenplurals(languagecode)
    except AttributeError:
        return ''
    pluralequation = potree().getlanguagepluralequation(languagecode)
    infoparts = [(_("Language Code"), languagecode),
                 (_("Language Name"), potree().getlanguagename(languagecode)),
                 # (_("Special Characters"), specialchars),
                 (_("Number of Plurals"), str(nplurals)),
                 (_("Plural Equation"), pluralequation),
                ]
    return [{"title": title, "value": value} for title, value in infoparts]

def getprojectitem(projectcode, languagecode):

    href = '%s/' % projectcode
    projectname = potree().getprojectname(projectcode)
    projectdescription = shortdescription(potree().getprojectdescription(projectcode))
    project = potree().getproject(languagecode, projectcode)
    pofilenames = project.browsefiles()
    projectstats = project.getquickstats()
    projectdata = getstats(project, projectstats, len(pofilenames))
    # updatepagestats(projectdata["translatedwords"], projectdata["totalwords"])
    return {
        'code': projectcode,
        'href': href,
        'icon': 'folder',
        'title': projectname,
        'description': projectdescription,
        'data': projectdata,
        'isproject': True,
        }

def getlanguageitem(languagecode, languagename, projectcode):
    language = potree().getproject(languagecode, projectcode)
    href = "../../%s/%s/" % (languagecode, projectcode)
    quickstats = language.getquickstats()
    data = getstats(language, quickstats, len(language.pofilenames))
    # boo
    #updatepagestats(data["translatedwords"], data["totalwords"])
    return {"code": languagecode, "icon": "language", "href": href, "title": languagename, "data": data}

