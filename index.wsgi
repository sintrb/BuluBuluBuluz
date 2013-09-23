# -*- coding: UTF-8 -*
'''
Created on 2013-8-31

@author: RobinTang
'''

from webpy import app
try:
    import sae
    # application = sae.create_wsgi_app(app)
    application = sae.create_wsgi_app(app.wsgifunc())
except:
    pass
