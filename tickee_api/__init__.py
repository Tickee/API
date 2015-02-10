'''
Created on 13-jun-2011

Python package containing API related logic and routing information for Pyramid.

@author: Kevin Van Wilder <kevin@tick.ee>
'''

from pyramid.configuration import Configurator
#from pyramid.config import Configurator
from pyramid_oauth2.routing import configure_oauth2_routing
from tickee_api.resources.zero_one.routes import v_0_1_routing
from tickee_api.resources.zero_two.routes import v_0_2_routing

def main( global_config, **settings ):
	config = Configurator(settings=settings)
	
	# Maintenance
	config.add_route('blitz-io-verification',    '/mu-1e32b3b5-6f6be39c-4bc74834-6b7586e8')
	config.add_route('maintenance-200',          '/maintenance/200')
	
	# Internal
	config.add_route('saasy-subscriptions',      '/services/saasy/subscriptions')
	
	# API routing
	config = v_0_1_routing(config)
	config = v_0_2_routing(config)
	config.scan('tickee_api.resources')
	
	# OAuth 2 routing
	configure_oauth2_routing(config)
	config.scan('pyramid_oauth2.views')
	return config.make_wsgi_app()