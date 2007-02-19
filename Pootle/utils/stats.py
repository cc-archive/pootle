
from translate.tools import pocount
from Pootle.utils import flatten # FIXME pocount returns generators

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


