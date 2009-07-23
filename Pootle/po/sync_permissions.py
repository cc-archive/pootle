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
    def _prefs_filename(self, lang):
        return os.path.join(
            self.basedir, lang, 'pootle-%s-%s.prefs' % (self.name, lang))
    def prefs_file(self, lang):
        prefs_files = glob.glob(self._prefs_filename(lang))
        if len(prefs_files) == 1:
            # great, that passes the sanity check.
            return prefs_files[0]
        else:
            print "Something is weird with", lang, "in project", self.name
            return None
    def set_lang2perms(self, new_lang2perms):
        '''Input: A str2str2set mapping from lang2user2permissions
        Output: True or False, based on if we had to actually change the filesystem'''
        dirty = False
        for lang in new_lang2perms:
            new_langperms = new_lang2perms[lang]
            # Figure out the current ones; if there is no prefs filename, fake an empty dict
            if self.prefs_file(lang):
                current_langperms = prefs2user2rights(open(self.prefs_file(lang)))
            else:
                current_langperms = {}
            # Check if the current is the same as the "new"; if so, do nothing
            if current_langperms == new_langperms:
                pass
            else:
                # else, we have to actually save this lang's permissions
                dirty = True
                self.set_lang_perms(lang, new_langperms)
                
        return dirty

    def set_lang_perms(self, lang, perms):
        '''Input: a language and a mapping from usernames to rights.
        Side-effect: Modifies the prefs file on disk.'''
        prefs = jToolkit.prefs.PrefsParser()
        for username in perms:
            prefs.__root__._assignments['rights.' + username] = ','.join(
                sorted(perms[username]))
        # The following could fail if the language does not exist.
        # so mkdir() the directory (later, we will need to actually
        # create the PO file. But that can be done by a separate script).
        target_prefs_file = self._prefs_filename(lang)
        target_prefs_dir = os.path.dirname(target_prefs_file)
        if not os.path.exists(target_prefs_dir):
            print 'Creating dir:', target_prefs_dir
            os.mkdir(target_prefs_dir, 0755)
        prefs.savefile(target_prefs_file)
        return True
        
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
        prefs_file = project.prefs_file(lang)
        if prefs_file is not None:
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

def copy_cc_org_to_other_project(target_project_name):
    cc_org_data = create_lang2perms_for_project('cc_org')
    target_data = create_lang2perms_for_project(target_project_name)
    # do the merge
    target_data = copy_one_str2str2set_to_another(cc_org_data, target_data)
    # now apply it
    target_project = Project(target_project_name)
    target_project.set_lang2perms(target_data)

if __name__ == '__main__':
    import sys
    assert not sys.argv[1].endswith('/'), "No trailing slash!"
    copy_cc_org_to_other_project(sys.argv[1])

