class Project:
	name = ''
	lang2permissions = None # dict

class Permissions(dict):
	pass # just a type of dict
# ...

def copy_perms_from_cc_org_to(project):
	for cc_org_lang in cc_org.languages:
		assert cc_org_lang.name in project.languages
		proj_lang = project.languages[cc_org_lang.name]
		# first of all, make it exist in project
		for user in cc_org_lang.users2permissions:
			perms = cc_org_lang.users2permissions[users
			# make sure that user has the same permissions in the project
			proj_lang.users2permissions[user].update(perms)
