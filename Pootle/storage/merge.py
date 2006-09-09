from Pootle.storage.api import IMerger


class SimpleMerger(object):
    """A naive merger.

    Simply takes the template and adds translations available in `translation`.

    The `translation` store is replaced.
    """
    _interface = IMerger

    def merge(self, translation, template):
        units = list(template)
        for unit in units:
            translist = []
            for i, plural in enumerate(unit.trans):
                msgid, translated = plural
                try:
                    updated = translation.translate(msgid, plural=i)
                except ValueError:
                    pass
                else:
                    if updated:
                        translated = updated
                translist.append((msgid, translated))
            unit.trans = translist
        translation.fill(units)
