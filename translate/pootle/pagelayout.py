#!/usr/bin/env python

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
  def __init__(self, contents):
    widgets.Division.__init__(self, contents, cls="item")

class ItemDescription(widgets.Division):
  def __init__(self, contents):
    widgets.Division.__init__(self, contents, cls="item-description")

class ItemStatistics(widgets.Division):
  def __init__(self, contents):
    widgets.Division.__init__(self, contents, cls="item-statistics")

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
    widgets.Division.__init__(self, [], cls="item-description")
    for num, item in enumerate(contents):
      self.addcontents(item)
      if num < len(contents)-1:
        self.addcontents("| ")

class TranslationText(widgets.Span):
  def __init__(self, contents):
    widgets.Span.__init__(self, contents, cls="translation-text")

class TranslateActionLink(widgets.Span):
  def __init__(self, href, contents, id=None):
    link = widgets.Link(href, contents)
    widgets.Span.__init__(self, link, id=id, cls="translation-action")

class PootleSidebar(widgets.Division):
  """the bar at the side describing current login details etc"""
  def __init__(self, session):
    baseurl = session.instance.baseurl
    title = SidebarTitle(getattr(session.instance, "title", "pootle"))
    description = SidebarText(getattr(session.instance, "description", "translation web server"))
    logintitle = SidebarTitle("login status")
    if session.status:
      loginstatus = session.status
    else:
      loginstatus = "not logged in"
    if session.isopen:
      loginlink = widgets.Link(baseurl+"?islogout=1", "Log Out")
    else:
      loginlink = [widgets.Link(baseurl+"login.html", "Log In"), " / ", widgets.Link(baseurl+"register.html", "Register")]
    loginstatus = SidebarText(loginstatus)
    loginlink = SidebarText(loginlink)
    widgets.Division.__init__(self, [title, description, logintitle, loginstatus, loginlink], "links")

class PootleBanner(widgets.Division):
  """the banner at the top"""
  def __init__(self, instance, maxheight=135):
    baseurl = instance.baseurl
    bannertable = table.TableLayout({"width":"100%", "cellpadding":0, "cellspacing":0, "border":0})
    width, height = min((180*maxheight/135, maxheight), (180, 135))
    pootleimage = widgets.Image(baseurl+"images/pootle.jpg", {"width":width, "height":height})
    pootlecell = table.TableCell(pootleimage, {"width": width, "align":"left", "valign":"top"})
    gapimage = widgets.Image(baseurl+"images/gap.png", {"width":5, "height":5})
    gapcell = table.TableCell(gapimage, {"width":5})
    width, height = min((238*maxheight/81, 81), (238, 81))
    logoimage = widgets.Image(baseurl+"images/top.png", {"width":width, "height":height})
    logocell = table.TableCell(logoimage, {"align":"center", "valign":"middle"})
    bordercell = table.TableCell([], {"class":"border_top", "align":"right", "valign":"middle"})
    toptable = table.TableLayout({"class":"header", "width":"100%", "height":maxheight, "cellpadding":0, "cellspacing":0, "border":0})
    toptable.setcell(0, 0, logocell)
    toptable.setcell(1, 0, bordercell)
    topcell = table.TableCell(toptable, {"width":"100%"})
    bannertable.setcell(0, 0, pootlecell)
    bannertable.setcell(0, 1, gapcell)
    bannertable.setcell(0, 2, topcell)
    widgets.Division.__init__(self, bannertable, id="banner")

class PootlePage(widgets.Page):
  """the main page"""
  def __init__(self, title, contents, session, bannerheight=135):
    if not hasattr(session.instance, "baseurl"):
      session.instance.baseurl = "/"
    stylesheets = [session.instance.baseurl + "pootle.css"]
    if hasattr(session.instance, "stylesheet"):
      stylesheets.append(session.instance.baseurl + session.instance.stylesheet)
      
    self.banner = PootleBanner(session.instance, bannerheight)
    self.links = PootleSidebar(session)
    widgets.Page.__init__(self, title, contents, {"includeheading":False}, stylesheets=stylesheets)

  def addsearchbox(self, searchtext, contextinfo="", action=""):
    """adds a simple search box"""
    self.links.addcontents(SidebarTitle("Search"))
    searchbox = widgets.Input({"name": "searchtext", "value": searchtext})
    searchform = widgets.Form([contextinfo, searchbox], {"action": action, "name":"searchform"})
    self.links.addcontents(searchform)

  def addfolderlinks(self, title, foldername, folderlink):
    """adds a section on the current folder"""
    self.links.addcontents(SidebarTitle(title))
    currentfolderlink = widgets.Link(folderlink, foldername or "/")
    self.links.addcontents(SidebarText(currentfolderlink))

  def getcontents(self):
    """returns the actual contents of the page, wrapped appropriately"""
    contents = widgets.Division(self.contents, "content")
    return self.getcontentshtml([self.banner, contents, self.links])

