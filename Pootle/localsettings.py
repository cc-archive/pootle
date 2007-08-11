# Django settings for Pootle project.
import os

def next_to_this_file(this_file, additional_path):
    return os.path.join(os.path.dirname(os.path.abspath(this_file)), additional_path)


DEBUG = True

DATABASE_ENGINE = 'sqlite3'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = next_to_this_file(__file__,'db')             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"

MEDIA_ROOT = next_to_this_file(__file__,'html')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/static/'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    next_to_this_file(__file__,'templates/'),
)

# Set this to a valid email host and port, otherwise users will not be able to 
# register at this server.
EMAIL_HOST="localhost"
EMAIL_PORT=25

POOTLE_INSTANCE = 'Pootle'

# If you have old Pootle installation, this setting will keep using 
# Pootle's prefs files for metadata storage instead of databases.
POOTLE_BACKWARDS_COMPATIBILITY = False

# If the site admin wants to approve new projects (advised), set this 
# option to True.
REQUIRE_NEW_PROJECT_APPROVAL = True

# Set this to root url for storage daemon. This is where Pootle web 
# interface will fetch translatable strings from and submit back 
# the translated ones.
STORAGE_ROOT_URL = "http://127.0.0.1:8080/"

