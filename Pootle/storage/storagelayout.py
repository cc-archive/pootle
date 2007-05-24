from Pootle.path import path
from Pootle.utils.fstags import create_tag
from Pootle.utils.stats import enumerating_classify, classify_unit, SimpleStats
from translate.storage.po import pofile, pounit
import os

class gettext_path(path):
    def _get_current(self):
        current_id = (self / 'current').bytes()
        current_file = self / 'revisions' / current_id
        return current_file
    current = property(_get_current, None, None)

    def _get_index(self):
        return self / 'index'
    index = property(_get_index, None, None)

    def has_updates(self):
        updatelist = (self / 'pending').listdir() 
        return len(updatelist) > 0
    updated = property(has_updates, None, None)

    def lock(self):
        if self.locked:
            raise ValueError("file locked")
        (self / 'lock').touch()
        
    def unlock(self):
        (self / 'lock').remove()

    def is_locked(self):
        return (self / 'lock').exists()
    locked = property(is_locked, None, None)

    def merge(self):
        """ Merges pending units and current po file, resulting 
        in a new revision.
        """

        self.lock()
        pending = self / 'pending'
        updates = []
        pending_list = pending.listdir()

        if not pending_list:
            return 
        # calculate update ranges
        pending_num = [int(i.basename()) for i in pending_list]
        while pending_num:
            x = pending_num.pop(0)
            start = x 
            while len(pending_num) > 0 and  pending_num[0] == x+1:
                x += 1 
                pending_num.pop(0)
            end = x + 1
            updates.append((start, end))
            
        index = (self / 'index').open()
        num_units = int(index.readline())
        newpo = []
        current = self.current.open()
        cursor = 0
        for start, end in updates:
            index.seek(32*start)
            line = index.readline().split()
            newpo.append(current.read(int(line[0]) - cursor))
            
            for x in range(start, end):
                newpo.append((self / 'pending' / ('%.8d' % x)).bytes())
            
            index.seek(32*end)
            line = index.readline().split()
            current.seek(int(line[0]))
            cursor = current.tell()
        newpo.append(current.read())
        
        current = self / 'current'
        current_id = int(current.bytes()) + 1
        current.write_bytes("%.8d" % current_id)
        self.current.write_bytes("".join(newpo))
        self.update_index()
        for f in pending_list:
            f.remove()
        self.unlock()

    def update_index(self, indexfile=None):
        """Updates the index file, where file offset and checks are stored"""

        if indexfile == None:
            indexfile = 'index'
        index_file = os.open(self / indexfile, os.O_TRUNC | os.O_CREAT, 0666)
        os.close(index_file)
        current_po = pofile(self.current.open())
        stats = []
        seek = 0
        # FIXME add packed stats
        for unit in current_po.units:
            stats.append("%.10d %.20d\n" % (seek + 1, 0))
            seek += len(str(unit)) + 1
        stats.append("%.10d %.20d\n" % (seek, 0))
        stats.insert(0, "%.10d                     \n" % len(stats))
        index_file = (self / indexfile).open("w")
        index_file.write("".join(stats))
        index_file.close()

    def indexed(self, key):
        """return an offset from start of file and length of unit in bytes"""
        index_file = self.index
        if not index_file.exists():
            self.update_index()
        index_file = index_file.open()
        key = int(key)
        if key <= 0:
            raise IndexError("key must be positive integer")
        
        index_file.seek(32*(key)) # records are 32 chars wide
        line1 = [int(i) for i in index_file.readline().split()]
        line2 = [int(i) for i in index_file.readline().split()]
        if not line1 or not line2:
            # if index is invalid, rebuild it and rerun indexed
            self.update_index()
            return self.indexed(key)
        return (line1[0], line2[0] - line1[0], line1[1])
        
    def __setitem__(self, key, value):
        key = int(key)
        if key <= 0:
            raise IndexError("key must be positive integer")
        unit = pounit()
        unit.parse(value)
    
        if value != str(unit):
            # if parsing fails, don't do it
            raise ValueError("unit was not parsed correctly")

        pending = self / 'pending' / ('%.8d' % key)
        if pending.exists():
            # already exists, merge first
            self.merge()
        pending.write_bytes(str(unit))       

    def __getitem__(self, key):
        key = int(key)
        if key <= 0:
            raise IndexError("key must be positive integer")
        pending = self / 'pending' / ('%.8d' % key)
        
        offset, numread, stats = self.indexed(key)
        if pending.exists():
            data = pending.bytes()
        else:
            # read pounit
            current_file = self.current.open()
            current_file.seek(offset)
            data = current_file.read(numread)
        unit = pounit()
        unit.parse(data)
        return unit, stats

    def _get_version(self):
        return int((self / 'version').bytes())
    version = property(_get_version, None, None)

    def getpo(self, nonblocking=False):
        if self.updated:
            if  nonblocking:
                raise IOError("getpo would block")
            self.merge()
        return self.current.open()
    
    def is_po_file(self):
        return self.ext == ".po"

    def list_trans(self):
        "lists files pootle storage can understand"
        return self.dirs("[!.]*") + [ i for i in self.files() if translatable_file_re.match(i)]

    def _get_classify(self): # FIXME this should probably go to TranslationStore object
        if not hasattr(self,'_classify'):
            if self.is_po_file():
                self._classify = enumerating_classify( self.checker , [u for u in self.translationstore.units if not u.isheader() and not u.isobsolete()] )
            else:
                self._classify = None
        return self._classify
    classify = property(_get_classify)

    def _get_translation_store(self):
        if not hasattr(self, '_translation_store'):
            newpo = pofile()
            newpo.parse(self.current.bytes())
            self._translation_store = newpo
        return self._translation_store
    translationstore = property(_get_translation_store)

    def _get_stats(self):
        """_get_stats is a method that retrieves statistics for a file
        that get displayed when browsing files that are part of
        TranslationProject.

        It returns a list with following indexes:
            0   translated words
            1   translated strings
            2   translated percentage
            3   fuzzy words
            4   fuzzy strings
            5   fuzzy percentage
            6   untranslated words
            7   untranslated strings
            8   untranslated percentage
            9   all words
            10  all strings
        """
        if not self._stats:
            if self.classify:
                c = self.classify
                transs = len(c['translated'])
                fuzzys = len(c['fuzzy'])
                totals = len(c['total'])
                untras = totals - transs - fuzzys
                perc = totals/100.0
                # sum number of words
                transw = sum([c['sourcewordcount'][x] for x in c['translated']])
                fuzzyw = sum([c['sourcewordcount'][x] for x in c['fuzzy']])
                untraw = sum([c['sourcewordcount'][x] for x in [
                    i for i in c['total'] if i not in c['translated'] and i not in c['fuzzy']]])
                data = [transw,transs,transs/perc,
                        fuzzyw,fuzzys,fuzzys/perc,
                        untraw,untras,untras/perc,
                        sum(c['sourcewordcount']), totals]
                data = SimpleStats([int(x) for x in data])
                self._stats = ",".join([str(x) for x in data])
            else:
                data = SimpleStats( (0,0,0, 0,0,0, 0,0,0, 0,0) )
                for s in [ i.stats for i in self.list_trans()]:
                    data = data & s
                data.recalculate()
                self._stats = ",".join([str(x) for x in data])
        else:
            data = SimpleStats([int(x) for x in self._stats.split(",")])
        return data
    stats = property(_get_stats)

    # xattr filesystem tags
    _stats = property(*create_tag('stats'))

    
if __name__ == '__main__':
    po_file = gettext_path('test.po')

    if po_file.exists():
        print 'current:', po_file.current
        print 'updated:', po_file.updated
        po_file.update_index()
        #print str(po_file[1])
        po_file.merge()
        print 'end'

