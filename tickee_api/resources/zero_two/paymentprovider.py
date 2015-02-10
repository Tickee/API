from celery.execute import send_task
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes
from tickee_api.core import validate_schema
from tickee_api.resources.zero_two import schema

###############################################################################
# /accounts/:shortname/psp
###############################################################################

@view_config(route_name='02-account-psp', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def psp_details(request, oauth2_context):
    """ Returns psp information for the account """
    account_shortname = request.matchdict.get('account_id')
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
        
    result = send_task("psp.details", 
                       kwargs=dict(client_id=client_id,
                                   account_shortname=account_shortname)).get()
                                   
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200 
        result['notification_url'] = 'https://api.tick.ee/0.2/psp/%s/notify' % result['id']
        
    return result


@view_config(route_name='02-account-psp', request_method='PUT', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
@validate_schema(schema.PaymentProvider)
def psp_update(request, oauth2_context):
    """ updates psp information for the account """
    account_shortname = request.matchdict.get('account_id')
    psp_information = request.deserialized_body
    print psp_information
    psp_name = psp_information.get('provider')
    psp_data = psp_information.get('data', {})
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
        
    result = send_task("psp.update", 
                       kwargs=dict(client_id=client_id,
                                   account_shortname=account_shortname,
                                   psp_name=psp_name,
                                   psp_data=psp_data)).get()
                                   
    if type(result) is dict and "error" in result:
        request.response.status_int = 403
    else:
        request.response.status_int = 200 
        result['notification_url'] = 'https://api.tick.ee/0.2/psp/%s/notify' % result['id']
        
    return result


###############################################################################
# /payments/:id/notify
###############################################################################

@view_config(route_name='02-psp-notify', 
             renderer='string')
def psp_notify(request):
    """Handles notifications received from the payment service providers.
    
    Request::
    
        [GET,POST] /psp/{id}/notify
    
    Parameters:
        Anything
            
    Returns:
        Each payment service provider requires a different response.
        The creation of the response information is handled by the provider class 
        of the payment service provider. 
        
    """
    # URL Parameters
    psp_id = int(request.matchdict.get('psp_id'))
    
    context = dict(message = request.body,
                   params = request.params.dict_of_lists())
    
    result = send_task("tickee.paymentproviders.entrypoints.notification", 
                       kwargs=dict(psp_id=psp_id,
                                   context=context))
    return result.get()