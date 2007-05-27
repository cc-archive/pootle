
from translate.tools import pocount
from Pootle.utils import flatten

class SimpleStats(list):
    "This implements a new operation of adding stats together for easier calculation."
    def __repr__(self):
        return "stats t: %dw %ds %dp f: %dw %ds %dp u: %dw %ds %dp all: %dw %ds" % tuple(self)

    def __and__(self, other):
        "vector addition"
        assert len(self) == len(other)
        return SimpleStats([ self[i] + other[i] for i in xrange(len(self)) ])

    def recalculate(self):
        "racalculates percentage for stats"
        assert len(self) == 11
        perc = self[10]/100.0
        try:
            self[2] = int(self[1]/perc)
            self[5] = int(self[4]/perc)
            self[8] = int(self[7]/perc)
        except ZeroDivisionError:
            self[2], self[5], self[8] = 0, 0, 0

def classify_unit(checker, unit):
    '''classifies a translation unit according to translate checks
    
    return a dict with checks 
    '''

    result ={ 
        'total': None,
        'sourcewordcount': [pocount.wordcount(text) for text in unit.source.strings],
        'targetwordcount': [pocount.wordcount(text) for text in unit.target.strings],
        }
    if unit.isfuzzy():
        result['fuzzy'] = None
    if unit.gettargetlen() == 0:
        result['blank'] = None
    if unit.istranslated():
        result['translated'] = None

    if isinstance(unit.source, str) and isinstance(unit.target, unicode):
        source = unit.source.decode(getattr(unit, 'encoding', 'utf-8'))
    else: 
        source = unit.source
    for ch in checker.run_filters(source, unit.target):
        result["check-%s" % ch[0]] = None
    return result

def enumerating_classify(checker, transunits):
    """Analyzes TranslationStore and returns checks as are written in 
    
    returns a dict
    """

    keys = [ 'fuzzy', 'blank', 'translated', 'has-suggestions', 'total', 'sourcewordcount', 'targetwordcount' ]
    classify = dict([ (k, []) for k in keys + checker.getfilters().keys() ])
    
    for item, unit in enumerate(transunits):
        data = classify_unit(checker, unit)
        for key in data.iterkeys():
            c = classify.setdefault(key,[])
            if data[key] == None:
                c.append(item)
            else:
                c.append(data[key])
    classify['sourcewordcount'] = flatten(classify['sourcewordcount'])
    classify['targetwordcount'] = flatten(classify['targetwordcount'])
    return classify


