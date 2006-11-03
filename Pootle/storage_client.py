# This file is supposed to have all translation accessing functions in Pootle,
# at least the web portal part of it.

from Pootle.conf import instance, potree
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


