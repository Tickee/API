from celery.execute import send_task
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes
from tickee_api.core import validate_schema
import schema



@view_config(route_name='02-account-visitors', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def account_visitors(request, oauth2_context):
    """ Returns a list of users who have attended your events """
    account_name = request.matchdict.get('account_id')
    
    result = send_task("tickets.visitors_of_account", 
                       kwargs=dict(account_short=account_name)).get()
        
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
        
    return result


@view_config(route_name='02-event-visitors', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def event_visitors(request, oauth2_context):
    """ Returns a list of users who have attended the event """
    event_id = request.matchdict.get('event_id')
    
    result = send_task("tickets.visitors_of_event", 
                       kwargs=dict(event_id=event_id)).get()
        
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
        
    return result


###############################################################################
# /users
###############################################################################

@view_config(route_name='02-user-collection', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def user_collection(request, oauth2_context):
    """ Returns a list of users
    
    ============  ============================================================ 
    Scope         Description                 
    ============  ============================================================
    internal      lists all users.
    account_mgmt  n/a
    none          n/a
    ============  ============================================================   
    """  
    # Parameters
    email = request.params.get('email') 
    
    if email is not None:
        user = send_task("tickee.users.entrypoints.user_exists", 
                         kwargs=dict(email=email)).get()
        if user is not False:
            return [user]
        
    return []


@view_config(route_name='02-user-collection', request_method='POST', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL,
                        oauth_scopes.ACCOUNT_MGMT])
@validate_schema(schema.User, required_nodes=["email"])
def user_create(request, oauth2_context):
    """Creates a user and returns his id.
    
    Request::
    
        POST /users/create
    
    Parameters:
        email (mandatory)
            Specifies the email of the user to create
        password (optional)
            Specifies the password of the newly created user.
        
    """
    user_info = request.json_body
    result = send_task("tickee.users.entrypoints.user_create", 
                       kwargs=dict(client_id=oauth2_context.client_id,
                                   email=user_info.get('email'),
                                   password=user_info.get('password'),
                                   last_name=user_info.get('last_name'),
                                   first_name=user_info.get('first_name'),
                                   user_info=user_info)).get()
                                   
    if isinstance(result, dict) and "error" in result:
        request.response.status_int = 403
    else:
        request.response.status_int = 201
        
    return result
    

###############################################################################
# /users/{id}
###############################################################################

@view_config(route_name='02-user-details', request_method='DELETE', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def user_delete(request, oauth2_context):
    """ Deactivates a user """
    # URL parameters
    user_id = request.matchdict.get('user_id')
    
    result = send_task("users.deactivate", 
                       kwargs=dict(user_id=user_id)).get()
                                       
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
        
    return result


@view_config(route_name='02-user-details', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL,
                        oauth_scopes.ACCOUNT_MGMT])
def user_details(request, oauth2_context):
    """Returns user details"""
    # URL parameters
    user_id = request.matchdict.get('user_id')
    activation_token = request.params.get('token')
    # Parameters
    
    result = send_task("tickee.users.entrypoints.user_details", 
                       kwargs=dict(user_id=user_id,
                                   activation_token=activation_token)).get()
                                       
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
        
    return result


@view_config(route_name='02-user-details', request_method='PUT', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
@validate_schema(schema.User)
def user_update(request, oauth2_context):
    """Updates user information"""
    user_id = int(request.matchdict.get('user_id'))
    user_info = request.json_body
    result = send_task("users.update", 
                       kwargs=dict(user_id=user_id,
                                   user_info=user_info)).get()
                                   
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
        
    return result

###############################################################################
# /users/{id}/mails/activation
###############################################################################

@view_config(route_name='02-user-mails-activation', request_method='POST', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def user_mail_activation(request, oauth2_context):
    """Sends a mail to activate the user"""
    user_id = int(request.matchdict.get('user_id'))
    result = send_task("users.update", 
                       kwargs=dict(user_id=user_id,
                                   user_info=dict(active=False))).get()
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
    return result
    

###############################################################################
# /users/{id}/mails/recovery
###############################################################################

@view_config(route_name='02-user-mails-recovery', request_method='POST', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def user_mail_recovery(request, oauth2_context):
    """Sends a mail to change password"""
    user_id = int(request.matchdict.get('user_id'))
    
    result = send_task("users.recover_password", 
                       kwargs=dict(user_id=user_id)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
    return result


###############################################################################
# /users/{id}/password/{password}
###############################################################################

@view_config(route_name='02-user-password', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def user_validate_password(request, oauth2_context):
    """Updates user information"""
    
    user_id = int(request.matchdict.get('user_id'))
    password = request.matchdict.get('password')
    
    result = send_task("users.validate_password", 
                       kwargs=dict(user_id=user_id,
                                   password=password)).get()
        
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
        
    return result

