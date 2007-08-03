from django.db import models, transaction
from django.conf import settings
from translate.filters import checks
from Pootle.path import path
from django.contrib.auth.models import User
from Pootle import storage_client
from Pootle.utils.stats import SimpleStats
import Pootle.instance
from translate.storage import po

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

class Folder(models.Model):
    parent = models.ForeignKey("self", null=True)
    name = models.SlugField(maxlength=200, unique=True)
    translatedwords = models.IntegerField(default=0)
    translatedstrings = models.IntegerField(default=0)
    fuzzywords = models.IntegerField(default=0)
    fuzzystrings = models.IntegerField(default=0)
    allwords = models.IntegerField(default=0)
    allstrings = models.IntegerField(default=0)

    isdir = True
    icon = 'folder'

    class Admin:
        pass

    def __str__(self):
        return "Folder: %s" % self.name

    def __repr__(self):
        return "<Folder: %s>" % self.name

    def _get_untrans_strings(self):
        return self.allstrings - self.translatedstrings - self.fuzzystrings

    def _get_untrans_words(self):
        return self.allwords - self.translatedwords - self.fuzzywords

    untranslatedstrings = property(_get_untrans_strings)
    untranslatedwords = property(_get_untrans_words)

    def _get_stats(self):
        # t: %dw %ds %dp f:%dw %ds %dp u: %dw %ds %dp all: %dw %ds
        untranslatedstrings = self.allstrings - self.translatedstrings - self.fuzzystrings
        try:
            return (
                self.translatedwords, 
                self.translatedstrings,
                int(float(self.translatedstrings / self.allstrings)),
                self.fuzzywords,
                self.fuzzystrings,
                int(float(self.fuzzystrings / self.allstrings)),
                self.allwords - self.translatedwords - self.fuzzywords,
                untranslatedstrings,
                int(float(untranslatedstrings / self.allstrings)),
                self.allwords,
                self.allstrings)
        except ZeroDivisionError:
            # FIXME: fill stats here
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
    root = models.ForeignKey(Folder)
    
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
        if not subdir:
            parent = self.root
        else:
            subdir2 = subdir.split("/")[-2]
            parent = Folder.objects.get(name=subdir2)
        return list(Folder.objects.filter(parent=parent)) + list(Store.objects.filter(parent=parent))

    def _get_podir(self):
        return "/%s/%s/" % (self.language.code, self.project.code)
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



class Module(models.Model):
    name = models.CharField(maxlength=200, unique=True)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey(Folder)
    translatedwords = models.IntegerField(default=0)
    translatedstrings = models.IntegerField(default=0)
    fuzzywords = models.IntegerField(default=0)
    fuzzystrings = models.IntegerField(default=0)
    allwords = models.IntegerField(default=0)
    allstrings = models.IntegerField(default=0)

class Store(models.Model):
    parent = models.ForeignKey(Folder)
    name = models.CharField(maxlength=512, unique=True)
    translatedwords = models.IntegerField(default=0)
    translatedstrings = models.IntegerField(default=0)
    fuzzywords = models.IntegerField(default=0)
    fuzzystrings = models.IntegerField(default=0)
    allwords = models.IntegerField(default=0)
    allstrings = models.IntegerField(default=0)

    isfile = True
    icon = 'file'

    class Admin:    
        pass

    def __repr__(self):
        return "<Store: %s>" % self.name

    def __str__(self):
        return "Store: %s" % self.name

    def _get_untrans_strings(self):
        return self.allstrings - self.translatedstrings - self.fuzzystrings

    def _get_untrans_words(self):
        return self.allwords - self.translatedwords - self.fuzzywords

    untranslatedstrings = property(_get_untrans_strings)
    untranslatedwords = property(_get_untrans_words)

    @transaction.commit_on_success
    def load_from_pofile(self, infile):
        c = po.pofile(inputfile=infile)

        # FIXME add header, language
        lang = Language.objects.get(code='sl')
        for num, x in enumerate(c.units):
            if x.isobsolete():
                continue
            u = Unit(store=self, index=num, state=0)
            u.save()
            def addcomments(commtype):
                for comm_string in [b[2:].rstrip() for b in getattr(x, commtype + "comments")]:
                    comm = Comment(value=comm_string, type=COMMENT_TYPES[commtype], unit=u)
                    comm.save()
            for comtyp in ['automatic', 'source', 'type', 'visible']:
                addcomments(comtyp)
            aa = x.getsource()
            for mmm in range(len(aa.strings)):
                ss = SourceString(source=unicode(aa.strings[mmm]), plural_id=mmm, unit=u)
                ss.save()
            aa = x.gettarget()
            for mmm in range(len(aa.strings)):
                ts = TargetString(sourcestring=ss, target=unicode(aa.strings[mmm]), plural_id=mmm, lang=lang)
                ts.save()


    def dump_to_postring(self):
        # quoting shortcut
        def quotedunit(x):
            y = "\n".join(po.quoteforpo(x))
            if y == '':
                return unicode('""')
            else:
                return y
        dumped = []
        units = Unit.objects.filter(store=self)
        for u in units:
            for c in u.comment_set.all():
                dumped.append(str(c))
            for ss in u.sourcestring_set.all():
                if not ss.plural_id:
                    dumped.append(u'msgid %s\n' % quotedunit(ss.source))
                    for ts in ss.targetstring_set.all():
                        dumped.append(u"msgstr %s\n" % quotedunit(ts.target))
                else:
                    dumped.append(u'msgid_plural %s\n' % quotedunit(ss.source))
                    for ts in ss.targetstring_set.all():
                        dumped.append(u"msgstr[%d] %s\n" % (ts.plural_id, quotedunit(ts.target)))
            dumped.append(u'\n')
        return "".join(dumped)

class Header(models.Model):
    store = models.ForeignKey(Store)
    key = models.CharField(maxlength=512)
    value = models.TextField()

UNIT_STATES = (
    (1, "Untranslated"),
    (1<<1, "Fuzzy"),
    (1<<2, "Translated"),
    )

class Unit(models.Model):
    store = models.ForeignKey(Store)
    index = models.IntegerField()
    state = models.IntegerField()

    def __repr__(self):
        return "<Unit %d of %s>" % (self.index, self.store.name)

    def __str__(self):
        return "%s\n%s" % (self.index, self.store.name)

    def tostring(self):
        print self.sourcestring_set.all

    class Admin:
        pass

    class Meta:
        ordering = ('index',)

class StoreAnnotation(models.Model):
    store = models.ForeignKey(Store)
    key = models.CharField(maxlength=500)
    value = models.CharField(maxlength=500)

class UnitAnnotation(models.Model):
    unit = models.ForeignKey(Unit)
    key = models.TextField()
    value = models.TextField()

class SourceString(models.Model):
    plural_id = models.IntegerField()
    source = models.TextField()
    unit = models.ForeignKey(Unit)

class TargetString(models.Model):
    plural_id = models.IntegerField()
    sourcestring = models.ForeignKey(SourceString)
    target = models.TextField()
    lang = models.ForeignKey(Language)


COMMENT_DEFINITION = (
    (0, 'Automatic',    '#.'),
    (1, 'Source',       '#:'),
    (2, 'Type',         '#,'),
    (3, 'Visible',      '#_'),
    )

# choices values for forms
COMMENT_CHOICES = tuple([(x[0], x[1]) for x in COMMENT_DEFINITION])
# dict of types, lowercase
COMMENT_TYPES = dict([(x[1].lower(), x[0]) for x in COMMENT_DEFINITION])
# used for converting comment type to eg. #.
COMMENT_MAPPING = dict([(x[0], x[2]) for x in COMMENT_DEFINITION])


class Comment(models.Model):
    type = models.IntegerField()
    unit = models.ForeignKey(Unit)
    value = models.CharField(maxlength=512)

    class Meta:
        # comment type definitions define ordering
        ordering = ('type',)

    def __str__(self):
        return "%s%s\n" % (COMMENT_MAPPING[self.type], self.value)
