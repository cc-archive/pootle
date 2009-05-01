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
    @property
    def prefs_file(self, lang):
        prefs_files = glob.glob(os.path.join(
            self.basedir, lang, 'pootle-cc_org-%s.prefs' % lang))
        if len(prefs_files) == 1:
            # great, that passes the sanity check.
            return prefs_files[0]
        else:
            print "Something is weird with", lang, "in project", self.name
            return None
    
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

def create_lang2perms_for_project(project_name):
    project = Project(project_name)
    ret = {}
    for lang in project.languages:
        # find prefs file
        prefs_file = project.prefs_files()
        if prefs_files is not None:
            user2rights = prefs2user2rights(open(prefs_file).read())
            ret[lang] = user2rights
    return ret

def copy_one_str2str2set_to_another(src, dst):
    '''
    >>> copy_one_str2str2set_to_another({'a': {'b': set(['c'])}}, {'b': {'b': set(['c'])}})
    {'a': {'b': set(['c'])}, 'b': {'b': set(['c'])}}
    >>> copy_one_str2str2set_to_another({'a': {'b': set(['c'])}}, {'a': {'b': set(['e'])}})
    {'a': {'b': set(['c', 'e'])}}
    '''
    # NOTE: Mutates dst :-(
    for lang in src:
        if lang not in dst:
            # if the target project has no permissions for this language, copy them straight in
            dst[lang] = src[lang]
        else:
            # if the target project has some permissions for this, update it with the cc_org info
            for user in src[lang]:
                if user not in dst[lang]:
                    dst[lang][user] = src[lang][user]
                else:
                    dst[lang][user].update(src[lang][user])
    return dst

                                           

    
    for cc_org_lang in cc_org.languages:
        assert cc_org_lang.name in project.languages
        proj_lang = project.languages[cc_org_lang.name]
        # first of all, make it exist in project
        for user in cc_org_lang.users2permissions:
            perms = cc_org_lang.users2permissions[users]
            # make sure that user has the same permissions in the project
            #proj_lang.users2permissions[user].update(perms)
