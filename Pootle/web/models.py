from django.db import models
from django.conf import settings
from translate.filters import checks
from Pootle.path import path
from django.contrib.auth.models import User
from Pootle import storage_client
from Pootle.utils.stats import SimpleStats
import Pootle.instance

CHECKSTYLES = [ (ch, ch) for ch in checks.projectcheckers.keys()]
FILETYPES = (   ('po', 'po'),  ('xliff','xliff'), )

class Project(models.Model):
    code = models.SlugField(maxlength=32,unique=True)
    name = models.CharField(maxlength=100)
    checkstyle = models.CharField(maxlength=20, choices=CHECKSTYLES, default='standard')
    description = models.TextField()
    filetype = models.CharField(maxlength=10, choices=FILETYPES)
    createmofiles = models.BooleanField()
    translatedwords = models.IntegerField(default=0)
    translatedstrings = models.IntegerField(default=0)
    fuzzywords = models.IntegerField(default=0)
    fuzzystrings = models.IntegerField(default=0)
    allwords = models.IntegerField(default=0)
    allstrings = models.IntegerField(default=0)
    
    icon = 'folder'
    _checker_cache = None
    
    def __str__(self):
        return self.name

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
            # fixme emit signal to indexer here
            return (0,0,0, 0,0,0, 0,0,0, 0,0)
    stats = property(_get_stats)

    def checker(self):
        "returns the checker this project uses"
        if not self._checker_cache:
            self._checker_cache = checks.projectcheckers[self.checkstyle]()
        return self._checker_cache

class AllowedLanguageManager(models.Manager):
    def get_query_set(self):
        return super(AllowedLanguageManager, self).get_query_set().filter(enabled=True)

class Language(models.Model):
    code = models.SlugField(maxlength=5,unique=True)
    name = models.CharField(maxlength=100)
    specialchars = models.CharField(maxlength=100)
    nplurals = models.IntegerField()
    plural_equation = models.CharField(maxlength=200)
    enabled = models.BooleanField()
    translatedwords = models.IntegerField(default=0)
    translatedstrings = models.IntegerField(default=0)
    fuzzywords = models.IntegerField(default=0)
    fuzzystrings = models.IntegerField(default=0)
    allwords = models.IntegerField(default=0)
    allstrings = models.IntegerField(default=0)

    objects = AllowedLanguageManager()
    unfiltered = models.Manager()

    icon = 'language'

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('code',)
    
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
            # fixme emit signal to indexer here
            return (0,0,0, 0,0,0, 0,0,0, 0,0)
    stats = property(_get_stats)

class TranslationProject(models.Model):
    language = models.ForeignKey(Language)
    project = models.ForeignKey(Project)
    translatedwords = models.IntegerField(default=0)
    translatedstrings = models.IntegerField(default=0)
    fuzzywords = models.IntegerField(default=0)
    fuzzystrings = models.IntegerField(default=0)
    allwords = models.IntegerField(default=0)
    allstrings = models.IntegerField(default=0)
    
    _podir = None
    _stats = None

    class Meta:
        unique_together = ( ('language','project'),) 

    def __repr__(self):
        return "<TranslationProject: /%s/%s/>" % (self.project.code, self.language.code)

    def _get_stats(self):
        if not self._stats:
            perc = self.allstrings/100.0
            untransw = self.allwords - self.translatedwords - self.fuzzywords
            untranss = self.allstrings - self.translatedstrings - self.fuzzystrings
            try:    
                self._stats = (self.translatedwords, self.translatedstrings, int(self.translatedstrings/perc), 
                            self.fuzzywords, self.fuzzystrings, int(self.fuzzystrings/perc),
                            untransw, untranss, int(untranss/perc), 
                            self.allwords, self.allstrings)
            except ZeroDivisionError:
                # refresh stats
                return SimpleStats( (0,0,0, 0,0,0, 0,0,0, 0,0) )
        return SimpleStats(self._stats)
    stats = property(_get_stats)

    def list_dir(self, subdir=None):
        listing = subdir and path(self.podir / subdir) or path(self.podir)
        return listing.listdir_remote()

    def _get_podir(self):
        if not self._podir:
            self._podir = path(storage_client.get_po_dir(self))
        return self._podir
    podir = property(_get_podir)
    
    def dir(self):
        return '/%s/%s/' % (self.language.code, self.project.code)

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

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)  
    uilanguage = models.ForeignKey(Language, blank=True, null=True)
    inputheight = models.SmallIntegerField(blank=True, null=True)
    inputwidth = models.SmallIntegerField(blank=True, null=True)
    viewrows = models.SmallIntegerField(blank=True, null=True)
    translaterows = models.SmallIntegerField(blank=True, null=True)
    languages = models.ManyToManyField(Language, related_name='joined_languages', blank=True, null=True)

