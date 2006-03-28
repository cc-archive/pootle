#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jToolkit.widgets import widgets
from jToolkit.widgets import table

class Contents(widgets.Division):
  def __init__(self, contents):
    widgets.Division.__init__(self, contents, cls="contents")

class ContentsItem(widgets.Division):
  def __init__(self, contents):
    widgets.Division.__init__(self, contents, cls="contentsitem")

class IntroText(widgets.Division):
  def __init__(self, contents):
    widgets.Division.__init__(self, contents, cls="intro")

class Item(widgets.Division):
  def __init__(self, contents, polarity=False):
    widgets.Division.__init__(self, contents)
    self.setpolarity(polarity)

  def setpolarity(self, polarity):
    cls = "item "
    if polarity:
      cls += "item-even"
    else:
      cls += "item-odd"
    self.attribs['class'] = cls

class Navbar(widgets.Division):
  def __init__(self, contents):
    widgets.Division.__init__(self, contents, cls="navbar")

class GoalItem(widgets.Division):
  def __init__(self, contents):
    widgets.Division.__init__(self, contents, cls="goalitem")

class ItemDescription(widgets.Division):
  def __init__(self, contents):
    widgets.Division.__init__(self, contents, cls="item-description")

class ItemStatistics(widgets.Division):
  def __init__(self, contents):
    widgets.Division.__init__(self, contents, cls="item-statistics")

class Title(widgets.ContentWidget):
  def __init__(self, contents):
    widgets.ContentWidget.__init__(self, "h3", contents, {"class": "title"})

class SidebarTitle(widgets.Division):
  def __init__(self, contents):
    widgets.Division.__init__(self, contents, cls="sidetitle")

class SidebarText(widgets.Division):
  def __init__(self, contents):
    widgets.Division.__init__(self, contents, cls="side")

class TranslateForm(widgets.Division):
  def __init__(self, contents):
    widgets.Division.__init__(self, contents, cls="translate-form")

class ActionLinks(widgets.Division):
  def __init__(self, contents):
    linkedcontents = widgets.SeparatedList(contents, " | ")
    widgets.Division.__init__(self, linkedcontents, cls="item-description")

class TranslationText(widgets.Span):
  def __init__(self, contents):
    widgets.Span.__init__(self, contents, cls="translation-text")

class TranslateActionLink(widgets.Span):
  def __init__(self, href, contents, id=None):
    link = widgets.Link(href, contents)
    widgets.Span.__init__(self, link, id=id, cls="translation-action")

class TranslationHeaders(widgets.Span):
  def __init__(self, contents):
    widgets.Span.__init__(self, contents, cls="translation-text-headers")

class PootleSidebar(widgets.Division):
  """the bar at the side describing current login details etc"""
  def __init__(self, session, returnurl=""):
    baseurl = session.instance.baseurl
    title = SidebarTitle(getattr(session.instance, "title", session.localize("Pootle Demo")))
    doclink = widgets.Link(baseurl+"doc/index.html", session.localize("Docs & Help"))
    projectslink = [" | ", widgets.Link(baseurl+"projects/", session.localize("All Projects"))]
    languageslink = [" | ", widgets.Link(baseurl+"languages/", session.localize("All Languages"))]
    if session.status:
      loginstatus = session.status
    else:
      loginstatus = session.localize("not logged in")
    adminlink = []
    if session.isopen:
      loginlinks = widgets.Link(baseurl+"?islogout=1", session.localize("Log Out"))
      homelink = [" | ", widgets.Link(baseurl+"home/", session.localize("Home"))]
      if session.issiteadmin():
        adminlink = [" | ", widgets.Link(baseurl+"admin/", session.localize("Admin"))]
    else:
      loginlinks = [widgets.Link(baseurl+"login.html?returnurl="+returnurl, session.localize("Log In")), " / ", widgets.Link(baseurl+"register.html", session.localize("Register")), " / ", widgets.Link(baseurl+"activate.html", session.localize("Activate"))]
      homelink = []
    loginimage = Icon("person.png")
    loginstatus = SidebarText([loginimage, loginstatus])
    quicklinks = SidebarText([doclink, projectslink, languageslink, homelink, adminlink])
    loginlink = SidebarText(loginlinks)
    widgets.Division.__init__(self, [title, quicklinks, loginstatus, loginlink], "links")

class Icon(widgets.Image):
  """an icon image"""
  def __init__(self, imagename, newattribs={}):
    # TODO: work out the baseurl properly
    widgets.Image.__init__(self, "/images/" + imagename, {"class": "icon"})
    self.overrideattribs(newattribs)

def layout_banner(maxheight):
  """calculates dimensions, image name for banner"""
  banner_width, banner_height = min((180*maxheight/135, maxheight), (180, 135))
  logo_width, logo_height = min((238*maxheight/81, 81), (238, 81))
  if banner_width <= 108:
    banner_image = "pootle-small.jpg"
  elif banner_width <= 180:
    banner_image = "pootle-medium.jpg"
  else:
    banner_image = "pootle.jpg"
  return {"banner_width": banner_width, "banner_height": banner_height,
    "logo_width": logo_width, "logo_height": logo_height, "banner_image": banner_image}

class PootleBanner(widgets.Division):
  """the banner at the top"""
  def __init__(self, instance, maxheight=135):
    baseurl = instance.baseurl
    bannertable = table.TableLayout({"width":"100%", "cellpadding":0, "cellspacing":0, "border":0})
    layout = layout_banner(maxheight)
    banner_width, banner_height = layout["banner_width"], layout["banner_height"]
    logo_width, logo_height = layout["logo_width"], layout["logo_height"]
    banner_image = layout["banner_image"]
    imagename = baseurl + "images/" + banner_image
    pootleimage = widgets.Image(imagename, {"width": banner_width, "height": banner_height})
    pootlecell = table.TableCell(pootleimage, {"width": banner_width, "align":"left", "valign":"top"})
    gapimage = widgets.Image(baseurl+"images/gap.png", {"width":5, "height":5})
    gapcell = table.TableCell(gapimage, {"width":5})
    width, height = min((238*maxheight/81, 81), (238, 81))
    logoimage = widgets.Image(baseurl+"images/top.png", {"width": logo_width, "height": logo_height})
    logocell = table.TableCell(logoimage, {"align":"center", "valign":"middle"})
    bordercell = table.TableCell([], {"class":"border_top", "align":"right", "valign":"middle"})
    toptable = table.TableLayout({"class":"header", "width":"100%", "style": "height: %spx" % maxheight, "cellpadding":0, "cellspacing":0, "border":0})
    toptable.setcell(0, 0, logocell)
    toptable.setcell(1, 0, bordercell)
    topcell = table.TableCell(toptable, {"width":"100%"})
    bannertable.setcell(0, 0, pootlecell)
    bannertable.setcell(0, 1, gapcell)
    bannertable.setcell(0, 2, topcell)
    widgets.Division.__init__(self, bannertable, id="banner")

class PootlePage(widgets.Page):
  """the main page"""
  def __init__(self, title, contents, session, bannerheight=135, returnurl=""):
    if not hasattr(session.instance, "baseurl"):
      session.instance.baseurl = "/"
    self.localize = session.localize
    stylesheets = [session.instance.baseurl + "pootle.css"]
    if hasattr(session.instance, "stylesheet"):
      stylesheets.append(session.instance.baseurl + session.instance.stylesheet)
    favicon = widgets.PlainContents('<link rel="shortcut icon" href="' + session.instance.baseurl + 'favicon.ico">')
      
    self.banner = PootleBanner(session.instance, bannerheight)
    self.links = PootleSidebar(session, returnurl)
    widgets.Page.__init__(self, title, contents, {"includeheading":False}, stylesheets=stylesheets, headerwidgets=[favicon])
    banner_layout = layout_banner(bannerheight)
    if hasattr(self, "templatevars"):
      self.templatevars.update(banner_layout)
    if "search" not in self.templatevars:
      self.templatevars["search"] = None

  def addsearchbox(self, searchtext, contextinfo="", action=""):
    """adds a simple search box"""
    self.links.addcontents(SidebarTitle(self.localize("Search")))
    searchbox = widgets.Input({"name": "searchtext", "value": searchtext})
    searchform = widgets.Form([contextinfo, searchbox], {"action": action, "name":"searchform"})
    self.links.addcontents(searchform)

  def geticon(self, type=None):
    """create the correct icon for the type sypplied"""
    if type is None:
      return []
    if type == "folder":
      icon = "folder.png"
    elif type == "file":
      icon = "file.png"
    elif type == "language":
      icon = "language.png"
    elif type == "edit":
      icon = "edit.png"
    elif type == "project":
      icon = "folder.png"
    return Icon(icon)

  def getcontents(self):
    """returns the actual contents of the page, wrapped appropriately"""
    contents = widgets.Division(self.contents, "content")
    return self.getcontentshtml([self.banner, contents, self.links])

  def polarizeitems(self, itemlist):
    """take an item list and alternate the background colour"""
    polarity = False
    for n, item in enumerate(itemlist):
      if isinstance(item, dict):
        item["parity"] = ["even", "odd"][n % 2]
      else:
        item.setpolarity(polarity)
      polarity = not polarity
    return itemlist

class PootleNavPage(PootlePage):
  def makenavbarpath(self, project=None, session=None, currentfolder=None, language=None, goal=None):
    """create the navbar location line"""
    links = self.makenavbarpath_dict(project, session, currentfolder, language, goal)
    pathlinks = links["pathlinks"] and widgets.SeparatedList([widgets.Link(pathlink["href"], pathlink["text"]) for pathlink in links["pathlinks"]], " / ")
    goallinks = links["goal"] and ["<i>", widgets.Link(links["goal"]["href"], links["goal"]["text"]), "</i>"]
    projectlink = links["project"] and widgets.Link(links["project"]["href"], links["project"]["text"])
    languagelink = links["language"] and widgets.Link(links["language"]["href"], links["language"]["text"])
    adminlink = links["admin"] and widgets.Link(links["admin"]["href"], links["admin"]["text"])
    if adminlink:
      projectlink = [projectlink, ": ", adminlink]
    if languagelink:
      languagelink = ["[", languagelink, "]"]
    if projectlink:
      projectlink = ["[", projectlink, "]"]
    return Title([widgets.SeparatedList(languagelink + projectlink, " "), " ", pathlinks, goallinks])

  def makenavbarpath_dict(self, project=None, session=None, currentfolder=None, language=None, goal=None):
    """create the navbar location line"""
    rootlink = ""
    links = {"admin": None, "project": [], "language": [], "goal": [], "pathlinks": []}
    if currentfolder:
      pathlinks = []
      dirs = currentfolder.split("/")
      depth = len(dirs)
      if currentfolder.endswith(".po"):
        depth = depth - 1
      rootlink = "/".join([".."] * depth)
      if rootlink:
        rootlink += "/"
      for backlinkdir in dirs:
        if backlinkdir.endswith(".po"):
          backlinks = "../" * depth + backlinkdir
        else:
          backlinks = "../" * depth + backlinkdir + "/"
        depth = depth - 1
        pathlinks.append({"href": self.getbrowseurl(backlinks), "text": backlinkdir, "sep": " / "})
      if pathlinks:
        pathlinks[-1]["sep"] = ""
      links["pathlinks"] = pathlinks
    if goal is not None:
      # goallink = {"href": self.getbrowseurl("", goal=goal), "text": goal}
      links["goal"] = {"href": self.getbrowseurl(""), "text": self.localize("All goals")}
    if project:
      if isinstance(project, tuple):
        projectcode, projectname = project
        links["project"] = {"href": "/projects/%s/" % projectcode, "text": projectname}
      else:
        links["language"] = {"href": rootlink + "../index.html", "text": project.languagename}
        # don't getbrowseurl on the project link, so sticky options won't apply here
        links["project"] = {"href": rootlink or "index.html", "text": project.projectname}
        if session:
          if "admin" in project.getrights(session) or session.issiteadmin():
            links["admin"] = {"href": rootlink + "admin.html", "text": self.localize("Admin")}
    elif language:
      languagecode, languagename = language
      links["language"] = {"href": "/%s/" % languagecode, "text": languagename}
    return links

  def makenavbar(self, icon=None, path=[], actions=[], stats=[], pagelinks=[]):
    """create a navbar"""
    icon = self.geticon(icon)
    actions = ActionLinks(actions)
    stats = ItemStatistics(stats)
    return Navbar([icon, path, actions, stats, pagelinks])

  def getbrowseurl(self, basename, **newargs):
    """gets the link to browse the item"""
    if not basename or basename.endswith("/"):
      return self.makelink(basename or "index.html", **newargs)
    else:
      return self.makelink(basename, translate=1, view=1, **newargs)

  def makelink(self, link, **newargs):
    """constructs a link that keeps sticky arguments e.g. showchecks"""
    combinedargs = self.argdict.copy()
    combinedargs.update(newargs)
    if '?' in link:
      if not (link.endswith("&") or link.endswith("?")):
        link += "&"
    else:
      link += '?'
    # TODO: check escaping
    link += "&".join(["%s=%s" % (arg, value) for arg, value in combinedargs.iteritems() if arg != "allowmultikey"])
    return link

  def initpagestats(self):
    """initialise the top level (language/project) stats"""
    self.alltranslated = 0
    self.grandtotal = 0
    
  def getpagestats(self):
    """return the top level stats"""
    return (self.alltranslated*100/max(self.grandtotal, 1))

  def updatepagestats(self, translated, total):
    """updates the top level stats"""
    self.alltranslated += translated
    self.grandtotal += total

  def describestats(self, project, projectstats, numfiles):
    """returns a sentence summarizing item statistics"""
    translated = projectstats.get("translated", [])
    total = projectstats.get("total", [])
    if "translatedwords" in projectstats:
      translatedwords = projectstats["translatedwords"]
    else:
      translatedwords = project.countwords(translated)
    if "totalwords" in projectstats:
      totalwords = projectstats["totalwords"]
    else:
      totalwords = project.countwords(total)
    if isinstance(translated, list):
      translated = len(translated)
    if isinstance(total, list):
      total = len(total)
    percentfinished = (translatedwords*100/max(totalwords, 1))
    if numfiles is None:
      filestats = ""
    elif isinstance(numfiles, tuple):
      filestats = self.localize("%d/%d files", numfiles + ", ")
    else:
      filestats = self.nlocalize("%d file", "%d files", numfiles, numfiles + ", ")
    wordstats = self.localize("%d/%d words (%d%%) translated", (translatedwords, totalwords, percentfinished))
    stringstats = ' <span cls="string-statistics">[%d/%d strings]</span>' % (translated, total)
    return filestats + wordstats + stringstats


