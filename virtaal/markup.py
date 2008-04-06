import re

xml_re = re.compile("&lt;[^>]+>")

def fancyspaces(string):
    """Returns the fancy spaces that are easily visible."""
    spaces = string.group()
#    while spaces[0] in "\t\n\r":
#        spaces = spaces[1:]
    return '<span underline="low" foreground="grey"> </span>' * len(spaces)

def markuptext(text, fancyspaces=False, stripescapes=False):
    """Replace special characters &, <, >, add and handle escapes if asked."""
    if not text:
        return ""
    text = text.replace("&", "&amp;") # Must be done first!
    text = text.replace("<", "&lt;")
    fancy_xml = lambda escape: \
            '<span foreground="darkred">%s</span>' % escape.group()
    text = xml_re.sub(fancy_xml, text)
    
    if stripescapes:
        text = text.replace("\n", '<br />')
        text = text.replace("\r", '<br />')
    else:
        fancyescape = lambda escape: \
                '<span foreground="purple">%s</span>' % escape

        text = text.replace("\r\n", fancyescape('\\r\\n') + '\n')
        text = text.replace("\n", fancyescape('\\n') + '\n')
        text = text.replace("\r", fancyescape('\\r') + '\n')
        text = text.replace("\t", fancyescape('\\t'))
    # we don't need it at the end of the string
    if text.endswith("\n"):
        text = text[:-len("\n")]

    if fancyspaces:
        text = addfancyspaces(text)
    return text

def addfancyspaces(text):
    """Insert fancy spaces"""
    #More than two consecutive:
    text = re.sub("[ ]{2,}", fancyspaces, text)
    #At start of string
    text = re.sub("^[ ]+", fancyspaces, text)
    #After newline
    text = re.sub("(?m)\n([ ]+)", fancyspaces, text)
    #At end of string
    text = re.sub("[ ]+$", fancyspaces, text)
    return text

def escape(text):
    if not text:
        return ""
    text = text.replace("\\", '\\\\')
    text = text.replace("\n", '\\n\n')
    text = text.replace("\r", '\\r\n')
    text = text.replace("\\r\n\\n",'\\r\\n')
    text = text.replace("\t", '\\t')
    if text.endswith("\n"):
        text = text[:-len("\n")]
    return text

def unescape(text):
    if not text:
        return ""
    text = text.replace("\t", "")
    text = text.replace("\n", "")
    text = text.replace("\r", "")
    text = text.replace("\\t", "\t")
    text = text.replace("\\n", "\n")
    text = text.replace("\\r", "\r")
    text = text.replace("\\\\", "\\")
    return text
