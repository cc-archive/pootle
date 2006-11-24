from Pootle.conf import instance
from Pootle.utils import shortdescription

def global_template_vars(request):
    description = getattr(instance(), "description")

    return {
        'description' : description,
        'meta_description' : shortdescription(description),
        'pagetitle' : 'Pootle',
        'keywords' : ["Pootle", "WordForge", "translate", "translation", "localisation", "localization", "l10n", "traduction", "traduire"],
        }
