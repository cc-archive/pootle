
from translate.tools import pocount
from Pootle.utils import flatten # FIXME pocount returns generators

class SimpleStats(list):
    "This implements a new operation of adding stats together for easier calculation."
    def __repr__(self):
        return "stats: %s" % super(SimpleStats, self).__repr__()

    def __and__(self, other):
        "vector addition"
        assert len(self) == len(other)
        return SimpleStats([ self[i] + other[i] for i in xrange(len(self)) ])

    def recalculate(self):
        "racalculates percentage for stats"
        assert len(self) == 11
        perc = self[10]/100.0
        self[2] = int(self[1]/perc)
        self[5] = int(self[4]/perc)
        self[8] = int(self[7]/perc)

def enumerating_classify(checker, transunits):
    """Analyzes TranslationStore and returns checks as are written in 
    
    returns a dict
    """

    keys = [ 'fuzzy', 'blank', 'translated', 'has-suggestions', 'total', 'sourcewordcount', 'targetwordcount' ]
    classify = dict([ (k, []) for k in keys + checker.getfilters().keys() ])
    
    for item, unit in enumerate(transunits):
        classify['total'].append(item)
        unit.isfuzzy() and classify['fuzzy'].append(item)
        unit.gettargetlen() == 0 and classify['blank'].append(item)
        unit.istranslated() and classify['translated'].append(item)
        source = unit.source
        target = unit.target
        if isinstance(source, str) and isinstance(target, unicode):
            source = source.decode(getattr(unit, "encoding", "utf-8"))
        for result in checker.run_filters(source, target):
            key = "check-%s" % result[0]
            class_list = classify.get(key, [])
            class_list.append(item)
            classify[key] = class_list
        # FIXME pocount returns generators
        classify['sourcewordcount'].append([pocount.wordcount(text) for text in unit.source.strings]) 
        classify['targetwordcount'].append([pocount.wordcount(text) for text in unit.target.strings])
    classify['sourcewordcount'] = flatten(classify['sourcewordcount'])
    classify['targetwordcount']= flatten(classify['targetwordcount'])
    # end FIXME pocount returns generators
    
    return classify


