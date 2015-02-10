'''
Created on 9 jan. 2012

@author: kevin
'''
from celery.execute import send_task
from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import view_config
import hashlib



@view_config(route_name='saasy-subscriptions',
             request_method='POST', renderer='json')
def saasy_sub_activated(request):
    privatekey = "591bfff6c852de664c78be0f267d52a9"
    value = request.params.get('security_data','') + privatekey
    # perform security check   
    if hashlib.md5(value).hexdigest().strip() != request.params.get('security_hash').strip():      
        raise HTTPForbidden()
    
    subscription_ref = request.params.get('SubscriptionReference')
    
    result = send_task("subscriptions.notification",
                       kwargs=dict(subscription_ref=subscription_ref)).get()
    
    print result