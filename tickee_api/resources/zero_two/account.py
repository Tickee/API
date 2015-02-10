from celery.execute import send_task
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes
from tickee_api.core import validate_schema
from tickee_api.resources.zero_two import schema


###############################################################################
# /accounts
###############################################################################


@view_config(route_name='02-account-collection', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def account_list(request, oauth2_context):
    """ Returns a list of accounts. You will be able to query a list of organisers
    in your area.
    
    .. note::
       Will be available in future versions.
    """
    short_name = request.params.get('short_name') 
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
        include_inactive = request.params.get('include_inactive') in ['t', '1', 'true']
    else:
        client_id =  oauth2_context.client_id
        include_inactive = False
    
    if short_name is not None:
        account = send_task("accounts.exists", 
                         kwargs=dict(account_name=short_name,
                                     include_inactive=include_inactive)).get()
        if account is not False:
            return [account]
        
    return []


###############################################################################
# /accounts/:id
###############################################################################

@view_config(route_name='02-account-resource', 
             request_method='DELETE', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def account_delete(request, oauth2_context):
    """ Deactivates the account """
    # URL Parameters
    account_identifier = request.matchdict.get('account_id')
    
    result = send_task("accounts.deactivate", 
                       kwargs=dict(account_name=account_identifier)).get()


    if type(result) is dict and "error" in result:
        request.response.status_int = 404
        
    return result


@view_config(route_name='02-account-resource', 
             request_method='GET', renderer='json')
def account_details(request):
    """ Retrieves detailed information about an organizer """
    # URL Parameters
    account_identifier = request.matchdict.get('account_id')
    
    try:
        account_id = int(account_identifier)
        result = send_task("accounts.details", 
                       kwargs=dict(oauth_client_id=None, 
                                   account_id=account_id))
    except:
        result = send_task("accounts.details", 
                       kwargs=dict(oauth_client_id=None, 
                                   account_shortname=account_identifier))
    result = result.get()
    if "error" in result:
        request.response.status_int = 404
        
    return result



@view_config(route_name='02-account-resource', 
             request_method='PUT', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
@validate_schema(schema.Account)
def account_update(request, oauth2_context):
    """ Updates account details """
    account_id = request.matchdict.get('account_id')
    account_info = request.deserialized_body
    result = send_task("accounts.update", 
                       kwargs=dict(account_identifier=account_id,
                                   account_info=account_info)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    
    return result


###############################################################################
# /accounts/me
###############################################################################


@view_config(route_name='02-account-own-details', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT]) # TODO: all scopes
def account_own_details(request, oauth2_context):
    """Retrieves detailed information about an organizer"""
    
    result = send_task("accounts.details", 
                       kwargs=dict(oauth_client_id=oauth2_context.client_id, 
                                   account_id=None)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    
    return result




###############################################################################
# /accounts/:id/statistics
###############################################################################

@view_config(route_name='02-account-statistics', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL,
                        oauth_scopes.ACCOUNT_MGMT])
def account_statistics(request, oauth2_context):
    """Returns statistical information about the account."""
    account_id = request.matchdict.get('account_id')
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id =  oauth2_context.client_id
    
    result = send_task("statistics.account", 
                       kwargs=dict(client_id=client_id,
                                   account_id=account_id)).get()
    if "error" in result:
        request.response.status_int = 404                        
        
    return result


###############################################################################
# /accounts/:id/statistics/monthly
###############################################################################

@view_config(route_name='02-account-statistics-monthly',  request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL,
                        oauth_scopes.ACCOUNT_MGMT])
def account_statistics_monthly(request, oauth2_context):
    """Returns monthly statistical information about the account."""
    account_id = request.matchdict.get('account_id')
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id =  oauth2_context.client_id
    
    result = send_task("statistics.account.detailed", 
                       kwargs=dict(client_id=client_id,
                                   account_id=account_id,
                                   max_months_ago=12)).get()
    if "error" in result:
        request.response.status_int = 404                             
        
    return result

###############################################################################
# /accounts/:shortname/keys
###############################################################################

@view_config(route_name='02-account-keys',  request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def account_keys(request, oauth2_context):
    """Returns a list of all client key/secret combinations."""
    account_id = request.matchdict.get('account_id')
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id =  oauth2_context.client_id
    
    result = send_task("accounts.keys", 
                       kwargs=dict(client_id=client_id,
                                   account_short=account_id)).get()
                                   
    if "error" in result:
        request.response.status_int = 404                             
        
    return result



###############################################################################
# /users/{id}/accounts
###############################################################################

@view_config(route_name='02-user-accounts', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def user_account_list(request, oauth2_context):
    """ Lists all accounts connected to the user """
    user_id = request.matchdict.get('user_id')
    include_inactive = request.params.get('include_inactive') in ['t', '1', 'true']
    
    result = send_task("accounts.list_accounts", 
                       kwargs=dict(user_id=user_id,
                                   include_inactive=include_inactive)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
                 
    return result



@view_config(route_name='02-user-accounts', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
@validate_schema(schema.Account, 
                 required_nodes=['short_name', 'email'])
def user_account_create(request, oauth2_context):
    """ Creates an account for the user. """
    user_id = request.matchdict.get('user_id')
    account_info = request.deserialized_body
    
    result = send_task("accounts.create", 
                       kwargs=dict(account_info=account_info,
                                   user_id=user_id)).get()
                                   
    if type(result) is dict and "error" not in result:
        request.response.status_int = 201
    else:
        request.response.status_int = 403
        
    return result
