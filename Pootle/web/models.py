from django.db import models
from translate.filters import checks
from Pootle.path import path
from django.contrib.auth.models import User

CHECKSTYLES = [ ('Standard', 'Standard')] + [ (ch, ch) for ch in checks.projectcheckers.keys()]
FILETYPES = (   ('po', 'po'),  ('xliff','xliff'), )

class Project(models.Model):
    code = models.SlugField(maxlength=32)
    name = models.CharField(maxlength=100)
    checkstyle = models.CharField(maxlength=20, choices=CHECKSTYLES)
    description = models.TextField()
    filetype = models.CharField(maxlength=10, choices=FILETYPES)
    createmofiles = models.BooleanField()

class Language(models.Model):
    code = models.SlugField(maxlength=5)
    name = models.CharField(maxlength=100)
    specialchars = models.CharField(maxlength=100)
    nplurals = models.IntegerField()
    plural_equation = models.CharField(maxlength=200)
    
class TranslationProject(models.Model):
    language = models.ForeignKey(Language)
    project = models.ForeignKey(Project)
    translatedwords = models.IntegerField()
    translatedstrings = models.IntegerField()
    fuzzywords = models.IntegerField()
    fuzzystrings = models.IntegerField()
    allwords = models.IntegerField()
    allstrings = models.IntegerField()

    def _get_stats(self):
        perc = self.allstrings/100.0
        untransw = self.allwords - self.translatedwords - self.fuzzywords
        untranss = self.allstrings - self.translatedstrings - self.fuzzystrings
        try:    
            return (self.translatedwords, self.translatedstrings, int(self.translatedstrings/perc), 
                    self.fuzzywords, self.fuzzystrings, int(self.fuzzystrings/perc),
                    untransw, untranss, int(untranss/perc), 
                    self.allwords, self.allstrings)
        except ZeroDivisionError:
            return (0,0,0, 0,0,0, 0,0,0, 0,0)
    stats = property(_get_stats)

    def list_dir(self, subdir=None):
        listing = subdir and path(self.podir / subdir) or path(self.podir)
        return listing.dirs("[!.]*") + listing.listpo()

    def _get_podir(self):
        if not hasattr(self, "_podir"):
            self._podir = path(potree().getpodir(self.language.code, self.project.code))
        return self._podir
    podir = property(_get_podir)

class PootlePermission(models.Model):
    tproject = models.ForeignKey(TranslationProject)
    user = models.ForeignKey(User)
    rights = models.IntegerField()

    # there are 31 possible rights
    RIGHTS = {
        'view': 0,
        'suggest': 1,
        'translate': 2,
        'overwrite': 3,
        'review': 4,
        'archive': 5,
        'pocompile': 6,
        'assign': 7,
        'admin': 8,
        'commit': 9,
        }

    def __str__(self):
        return "Permissions for %s for project /%s/%s/" % (self.user, self.project.code, self.language.code)

    def __repr__(self):
        return "<PootlePermissions: %s>" % ",".join(self.get_rights())

    def has_right(self, right):
        if right in self.RIGHTS:
            # perform a bitwise AND with appropriate bit set and return True if set, False otherwise
            return self.rights & 2**self.RIGHTS[right] and True or False
        else:
            return False

    def get_rights(self):
        rights = []
        ra = rights.append
        for r in self.RIGHTS.iterkeys():
           if self.has_right(r):
                ra(r)
        return rights

    def set_right(self, right):
        if right in self.RIGHTS:
            # bitwise OR sets the right
            self.rights = self.rights | 2**self.RIGHTS[right]

    def del_right(self, right):
        if right in self.RIGHTS:
            # bitwise AND with bit negative right clears the right
            self.rights = self.rights & ~ 2**self.RIGHTS[right]

