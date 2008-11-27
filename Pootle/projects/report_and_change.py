import glob
import os
import jToolkit.prefs

def project2lang2admin_and_committers(project):
    path = os.path.join('.', project, '*', '*.prefs')
    prefs = glob.glob(path)
    ret = {}
    lang2admin_and_committers = {}
    for pref in prefs:
        _pathprefix, _project, lang, filename = pref.split('/')

        if lang not in lang2admin_and_committers:
            lang2admin_and_committers[lang] = {}

        # Check that we have our heads screwed on straight
        assert _project == project
        assert _pathprefix == '.'
    
        # Parse that silly thing
        parsed = jToolkit.prefs.PrefsParser(pref)
        values = parsed.__root__._assignments
        for key in values.keys():
            _rights, username = key.split('.', 1)
            assert _rights == 'rights'
            
            value = values[key]
            rights = set(map(lambda s: s.strip(), value.split(',')))

            # Create a dictionariy indexed by these two important rights
            is_admin = ('admin' in rights)
            is_commit = ('commit' in rights)
            is_xlate = ('translate' in rights)

            add_rights = set()
            if project == 'cc_org':
                if is_xlate:
                    if not is_admin:
                        add_rights.add(u'admin')
                    if not is_commit:
                        add_rights.add(u'commit')

            else:
                if is_admin:
                    if not is_commit:
                        add_rights.add(u'commit')

            if add_rights:
                rights.update(add_rights)
                parsed.setvalue('rights.' + username, u', '.join(rights))
                parsed.savefile()
                # add some rights
                print 'just did add:', add_rights
                print 'to', username, 'for', project, 'in', lang

            if is_admin or is_commit:
                user2powers = {'admin': is_admin,
                               'commit': is_commit,
                               'xlate': is_xlate}
                lang2admin_and_committers[lang][username] = user2powers

        ret[project] = lang2admin_and_committers

    return ret
