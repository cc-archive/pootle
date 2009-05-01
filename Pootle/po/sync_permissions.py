import os
import jToolkit
import glob

class Project:
    def __init__(self, basedir):
        self.basedir = basedir
        self.name = basedir
    @property
    def languages(self):
        return [k for k in os.listdir(self.basedir) if k != '.svn']

    
def prefs2user2rights(prefs_string):
    pootle_users_prefs = prefs_string
    pootle_users_prefs = unicode(pootle_users_prefs)
    pootle_users_prefs_as_utf8 = pootle_users_prefs.encode('utf-8')
    import jToolkit.prefs
    parser = jToolkit.prefs.PrefsParser()
    parser.parse(pootle_users_prefs_as_utf8)
    data = parser.__root__._assignments # This *can't* be the right way...

    user2rights = {}
    for key in data:
        rights_literally, username = key.split('.')
        assert rights_literally == 'rights'
        value = set(map(lambda s: s.strip(), data[key].split(',')))
        user2rights[username] = value

    return user2rights

def create_lang2perms_for_cc_org():
    cc_org = Project('cc_org')
    ret = {}
    for lang in cc_org.languages:
        # find prefs file
        prefs_files = glob.glob('cc_org/' + lang + '/pootle-cc_org-%s.prefs' % lang)
        if len(prefs_files) == 1:
            # great, that passes the sanity check.
            user2rights = prefs2user2rights(open(prefs_files[0]).read())
            print user2rights
        else:
            print "Something is weird with", lang, "in project cc_org."
    
def copy_perms_from_cc_org_to(project):
    for cc_org_lang in cc_org.languages:
        assert cc_org_lang.name in project.languages
        proj_lang = project.languages[cc_org_lang.name]
        # first of all, make it exist in project
        for user in cc_org_lang.users2permissions:
            perms = cc_org_lang.users2permissions[users]
            # make sure that user has the same permissions in the project
            #proj_lang.users2permissions[user].update(perms)
