from celery.execute import send_task
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes

@view_config(route_name='01-account-collection', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def account_list(request):
    """ Returns a list of accounts. You will be able to query a list of organisers
    in your area.
    
    .. note::
       Will be available in future versions.
    """
    return list()



@view_config(route_name='01-account-events', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL,
                        oauth_scopes.ACCOUNT_MGMT],
        optional=True)
def account_events_list(request, oauth2_context):
    """ Returns a list of the events of the account.
    
    ============  ============================================================ 
    Scope         Description                 
    ============  ============================================================
    internal      Shows both public and private events of the account
    account_mgmt  Shows both public and private events of the account
    none          Shows only public events of the account
    ============  ============================================================
    
    Request::
    
        GET /0.1/accounts/{id}/events
    
    Parameters:
    
        None
            
    Returns::
    
        [
            {
                "id": 1,
                "dates": [
                    "2011-10-01T23:00:00",
                    ...
                ],
                "name": "eventname",
                "url": null,
                "image_url": null,
                "email": null,
                "description": "This is an event description"
                "account": {
                    "email": "account@example.be",
                    "id": 1,
                    "name": "Organiser"
                }
            },
            ...
        ]
        
    """
    # URL Parameters
    account_id = int(request.matchdict.get('account_id'))
        
    
    # client_id setting
    
    if oauth2_context is not None:
        if oauth_scopes.INTERNAL in oauth2_context.scopes:
            result = send_task("tickee.events.entrypoints.event_list", 
                               kwargs=dict(client_id=None,
                                           account_id=account_id,
                                           active_only=False))
        elif oauth_scopes.ACCOUNT_MGMT in oauth2_context.scopes:
            result = send_task("tickee.events.entrypoints.event_list", 
                               kwargs=dict(client_id=oauth2_context.client_id,
                                           account_id=account_id))
    else:
        result = send_task("tickee.events.entrypoints.event_list", 
                           kwargs=dict(client_id=None,
                                       account_id=account_id,
                                       active_only=True))
        
    
    # call entrypoint

    return result.get()




@view_config(route_name='01-account-collection', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def account_create(request, oauth2_context):
    """Creates an account connected to a user. If anything fails the 
    error key will be available in the response.
    
    Request::
    
        POST /0.1/account/create
    
    
    Parameters:
        user_id (mandatory)
            User id of the tickee user that will manage the account 
        account_name (mandatory)
            Name of the organization. May only contain alphanumerical
            characters. ([a-zA-Z0-9])
        email (mandatory)
            General email address to contact the organization
    
    Returns::
    
        {
            "email": "info@tick.ee",
            "id": 2,
            "name": "TickeeBVBA"
        }
        
    """
    # Mandatory parameter check
    if not set(['email', 'account_name', 'user_id']).issubset(set(request.params)):
        raise HTTPBadRequest()
    # Parameters
    account_name = request.params.get('account_name')
    email = request.params.get('email')
    user_id = request.params.get('user_id')
    
    result = send_task("accounts.create", 
                       kwargs=dict(account_name=account_name, 
                                   email=email, 
                                   user_id=user_id))
    return result.get()




@view_config(route_name='01-account-resource', 
             request_method='GET', renderer='json')
def account_details(request):
    """Retrieves detailed information about an organizer::
    
    Request::
    
        GET /0.1/account/{id}
    
    Parameters:
        None
            
    Returns::
    
        {
            "email": "info@tick.ee",
            "name": "TickeeBVBA",
            "id": 2
        }
        
    """
    # URL Parameters
    account_id = request.matchdict.get('account_id')
    
    result = send_task("accounts.details", 
                       kwargs=dict(oauth_client_id=None, 
                                   account_id=account_id))
    return result.get()




@view_config(route_name='01-account-own-details', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT]) # TODO: all scopes
def account_own_details(request, oauth2_context):
    """Retrieves detailed information about an organizer
    
    Request::
    
        GET /0.1/account/me
    
    Parameters:
        None
            
    Returns::
    
        {
            "email": "info@tick.ee",
            "name": "TickeeBVBA",
            "id": 2
        }
        
    """
    
    result = send_task("accounts.details", 
                       kwargs=dict(oauth_client_id=oauth2_context.client_id, 
                                   account_id=None))
    return result.get()