"""
MySQL database & settings for server
"""
from .settings import *

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.postgresql_psycopg2',
        'NAME'    : 'd8e03fh4npq33h',
        'USER'    : 'csfhhsgmfatlyh',
        'PASSWORD': '8b05701836b0a11992277062dfe37a03d9e3437bdf029573f5972f2939fd76d8',
        'HOST'    : 'ec2-184-73-199-189.compute-1.amazonaws.com',
        'URI'     : 'postgres://csfhhsgmfatlyh:8b05701836b0a11992277062dfe37a03d9e3437bdf029573f5972f2939fd76d8@ec2-184-73-199-189.compute-1.amazonaws.com:5432/d8e03fh4npq33h',
        'PORT'    : '5432',
    }
}
