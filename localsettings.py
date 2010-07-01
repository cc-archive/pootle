# This file contains the configuration settings for the Pootle server.
#
# It is in Python sytax. Everything after '#' is ignored as comments.

# Import some helper functions:
from pootle.install_dirs import *

# Mail server settings
#Example for Google as an external SMPT server
#DEFAULT_FROM_EMAIL = 'DEFAULT_USER@YOUR_DOMAIN.com'
#EMAIL_HOST_USER = 'USER@YOUR_DOMAIN.com'
#EMAIL_HOST_PASSWORD = 'YOUR_PASSWORD'
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 587
#EMAIL_USE_TLS = True


# Database configuration
DATABASE_ENGINE = 'sqlite3'                 # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = working_path('dbs/pootle.db') # Or path to database file if using sqlite3.
DATABASE_USER = ''                          # Not used with sqlite3.
DATABASE_PASSWORD = ''                      # Not used with sqlite3.
DATABASE_HOST = ''                          # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''                          # Set to empty string for default. Not used with sqlite3.

STATS_DB_PATH = working_path('dbs/stats.db') # None means the default path


# The directory where the translation files are kept
PODIRECTORY = working_path('po')

# Live translation means that the project called "Pootle" is used to provide
# the localised versions of Pootle. Set this to True to enable live translation
# of pootle UI. This is a good way to learn how to use Pootle, but it has high
# impact on performance.
LIVE_TRANSLATION = False


# File parse pool settings
#
# To avoid rereading and reparsing translation files from disk on
# every request, Pootle keeps a pool of already parsed files in memory.
#
# Larger pools will offer better performance, but higher memory usage
# (per server process). When the pool fills up, 1/PARSE_POOL_CULL_FREQUENCY
# number of files will be removed from the pool.

# DEFAULT: 40
PARSE_POOL_SIZE = 40
# DEFAULT: 4
PARSE_POOL_CULL_FREQUENCY = 4


# Cache Backend settings
#
# By default we use Django's in memory cache which is only suitable
# for small deployments. memcached is prefered. For more info, check
# http://docs.djangoproject.com/en/dev/topics/cache/#setting-up-the-cache
CACHE_BACKEND = 'locmem:///?max_entries=4096&cull_frequency=5'

# Uncomment to use memcached for caching
#CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

# Using memcached to store sessions improves performance for anonymous
# users. For more info, check
# http://docs.djangoproject.com/en/dev/topics/http/sessions/#configuring-the-session-engine

# Uncomment this if you're using memcached as CACHE_BACKEND and running under Django 1.0
#SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# Uncomment this if you're using memcached as CACHE_BACKEND and running under Django 1.1
#SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# To improve performance, non-logged users get cached copies of most pages.
# This variable is the number of seconds for which a page will be reused from
# cache. If you have a small server where more real-time statistics is
# important, you can make this lower.
# DEFAULT: 600
CACHE_MIDDLEWARE_SECONDS = 600


# Set this to False. DEBUG mode is only needed when testing beta's or
# hacking pootle
DEBUG = False


# Use the commented definition to authenticate first with an LDAP system and
# then to fall back to Django's authentication system.
#AUTHENTICATION_BACKENDS = ('pootle.auth.ldap_backend.LdapBackend', 'django.contrib.auth.backends.ModelBackend',)
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

# LDAP Setup
# The LDAP server.  Format:  protocol://hostname:port
AUTH_LDAP_SERVER = ''
# Anonymous Credentials
AUTH_LDAP_ANON_DN = ''
AUTH_LDAP_ANON_PASS = ''
# Base DN to search
AUTH_LDAP_BASE_DN = ''
# What are we filtering on?  %s will be the username (must be in the string)
AUTH_LDAP_FILTER = ''
# This is a mapping of pootle field names to LDAP fields.  The key is pootle's name, the value should be your LDAP field name.  If you don't use the field
# or don't want to automatically retrieve these fields from LDAP comment them out.  The only required field is 'dn'.
AUTH_LDAP_FIELDS = {
        'dn':'dn',
        #'first_name':'',
        #'last_name':'',
        #'email':''
        }

# set this to False to disable user registration, admins will still be
# able to create user accounts
CAN_REGISTER = True
