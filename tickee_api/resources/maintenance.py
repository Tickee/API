'''
Created on 27 dec. 2011

@author: kevin
'''
from pyramid.view import view_config
import logging



@view_config(route_name='blitz-io-verification', renderer="string")
def blitzio(request):
    return "42"

@view_config(route_name='maintenance-200', renderer="string")
def always_good(request):
    logging.debug(request.params.get('serial-number'))
    return """<notification-acknowledgment xmlns="http://checkout.google.com/schema/2" 
    serial-number="%s" />""" % request.params.get('serial-number')