#!/usr/bin/env python

from jToolkit.widgets import widgets
from jToolkit.widgets import table
from translate.pootle import pagelayout
from translate.pootle import projects

class TranslatePage(pagelayout.PootlePage):
  """the main page"""
  def __init__(self, project, subproject, session, argdict):
    self.project = project
    self.subproject = subproject
    self.translationproject = projects.getproject(self.project, self.subproject)
    for key, value in argdict.iteritems():
      if key.startswith("trans"):
        try:
          item = int(key.replace("trans",""))
        except:
          continue
        self.translationproject.receivetranslation(item, value)
    self.instance = session.instance
    title = "Pootle: translating %s into %s" % (self.subproject.fullname, self.project.fullname)
    translateform = widgets.Form(self.gettranslations(), {"name": "translate", "action":""})
    divstyle = {"font-family": "verdana, arial, sans-serif", "font-size": "small", "line-height": "100%"}
    translatediv = widgets.Division(translateform, None, {"style": divstyle})
    contents = widgets.Division([translatediv], "content")
    pagelayout.PootlePage.__init__(self, title, contents, session, bannerheight=81)
    autoexpandscript = widgets.Script('text/javascript', '', newattribs={'src': self.instance.baseurl + 'js/autoexpand.js'})
    self.headerwidgets.append(autoexpandscript)

  def addtransrow(self, rownum, origcell, transcell):
    self.transtable.setcell(rownum, 0, origcell)
    self.transtable.setcell(rownum, 1, transcell)

  def gettranslations(self):
    self.transtable = table.TableLayout({"width":"100%", "cellpadding":10, "cellspacing":1, "border":0})
    origtitle = table.TableCell("<b>original</b>")
    transtitle = table.TableCell("<b>translation</b>")
    self.addtransrow(-1, origtitle, transtitle)
    translationsbefore, currenttranslation, translationsafter = self.translationproject.gettranslations()
    self.textcolors = ["#000000", "#000060"]
    rowoffset = self.translationproject.item
    for row, (orig, trans) in enumerate(translationsbefore):
      self.addtranslationrow(rowoffset - len(translationsbefore) + row, orig, trans)
    orig, trans = currenttranslation
    self.addtranslationrow(rowoffset, orig, trans, True)
    for row, (orig, trans) in enumerate(translationsafter):
      self.addtranslationrow(rowoffset + 1 + row, orig, trans)
    self.transtable.shrinkrange()
    return self.transtable

  def getorigcell(self, row, orig, editable):
    origdiv = widgets.Division([], "orig%d" % row)
    if editable:
      orig = "<b>%s</b>" % orig
    else:
      origdiv.attribs["class"] = "autoexpand"
    origtext = widgets.Font(orig, {"color":self.textcolors[row % 2]})
    origdiv.addcontents(origtext)
    return table.TableCell(origdiv, {"bgcolor":"#e0e0e0", "width":"50%"})

  def gettranscell(self, row, trans, editable):
    transdiv = widgets.Division([], "trans%d" % row)
    if editable:
      textarea = widgets.TextArea({"name":"trans%d" % row, "rows":3, "cols":40}, contents=trans)
      submitbutton = widgets.Input({"type":"submit", "name":"submit", "value":"submit"}, "submit")
      contents = [textarea, submitbutton]
    else:
      contents = widgets.Font(trans, {"color":self.textcolors[row % 2]})
      transdiv.attribs["class"] = "autoexpand"
    transdiv.addcontents(contents)
    return table.TableCell(transdiv, {"width":"50%"})

  def addtranslationrow(self, row, orig, trans, editable=False):
    """returns an origcell and a transcell for displaying a translation"""
    origcell = self.getorigcell(row, orig, editable)
    transcell = self.gettranscell(row, trans, editable)
    self.addtransrow(row, origcell, transcell)

