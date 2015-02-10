from celery.execute import send_task
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes

#    config.add_route('01-user-collection',              '/0.1/users')
#    config.add_route('01-user-tickets',                 '/0.1/users/{user_id:\d+}/tickets')
#    config.add_route('01-user-orders',                  '/0.1/users/{user_id:\d+}/orders')
#    config.add_route('01-user-authenticate',            '/0.1/users/authenticate')

@view_config(route_name='01-user-collection', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL,
                        oauth_scopes.ACCOUNT_MGMT])
def user_collection(request, oauth2_context):
    """ Returns a list of users
    
    ============  ============================================================ 
    Scope         Description                 
    ============  ============================================================
    internal      lists all users.
    account_mgmt  n/a
    none          n/a
    ============  ============================================================
    
    Request::
    
        POST /0.1/users/authenticate
    
    Parameters:
    
        email (mandatory)
            The email address of the user
        password (mandatory)
            The password of the user
        
    Returns:
        
        Returns False if the credentials don't match or the user id in a 
        dictionary if they do. 
        
        {
            "id": 5
        }
    
    """
    




@view_config(route_name='01-user-authenticate', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL,
                        oauth_scopes.ACCOUNT_MGMT])
def user_authenticate(request, oauth2_context):
    """ Validates the user credentials
    
    ============  ============================================================ 
    Scope         Description                 
    ============  ============================================================
    internal      Checks if the username and password match.
    account_mgmt  n/a
    none          n/a
    ============  ============================================================
    
    Request::
    
        POST /0.1/users/authenticate
    
    Parameters:
    
        email (mandatory)
            The email address of the user
        password (mandatory)
            The password of the user
        
    Returns:
        
        Returns False if the credentials don't match or the user id in a 
        dictionary if they do. 
        
        {
            "id": 5
        }
    
    """
    # Mandatory parameter check
    if not set(['email', 'password']).issubset(set(request.params)):
        raise HTTPBadRequest()
    # Parameters
    email = request.params.get('email')
    password = request.params.get('password')  
     
    result = send_task("users.validate_password", 
                       kwargs=dict(email=email, 
                                   password=password)).get()
    return result



    
@view_config(route_name='01-user-tickets', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL,
                        oauth_scopes.ACCOUNT_MGMT])
def user_tickets(request, oauth2_context):
    """ Lists all tickets of a user.
    
    ============  ============================================================ 
    Scope         Description                 
    ============  ============================================================
    internal      Shows all tickets purchased.
    account_mgmt  Shows all tickets purchased for your events.
    none          n/a
    ============  ============================================================
    
    Request::
    
        GET /0.1/users/{id}/tickets
    
    Parameters:
    
        None
        
    Returns:
        
        A list of all tickets purchased
    
    """
    # URL parameters
    user_id = request.matchdict.get('user_id')
    
    # client_id setting
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        oauth2_context.client_id = None 
    
    # call entrypoint
    result = send_task("tickets.from_user", 
                       kwargs=dict(client_id=oauth2_context.client_id,
                                   user_id=user_id)).get()
    return result



@view_config(route_name='01-user-orders', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL,
                        oauth_scopes.ACCOUNT_MGMT])
def user_orders(request, oauth2_context):
    """ Lists all tickets of a user 
    
    ============  ============================================================ 
    Scope         Description                 
    ============  ============================================================
    internal      Shows all orders.
    account_mgmt  Shows all orders for your events.
    none          n/a
    ============  ============================================================
    
    Request::
    
        GET /0.1/users/{id}/orders
    
    Parameters:
    
        None
        
    Returns:
        
        A list of all orders
    
    """
    # URL parameters
    user_id = request.matchdict.get('user_id')
    
    # client_id setting
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        oauth2_context.client_id = None 
    
    # call entrypoint
    result = send_task("orders.from_user", 
                       kwargs=dict(client_id=oauth2_context.client_id,
                                   user_id=user_id)).get()
    return result


@view_config(route_name='01-user-exists', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL,
                        oauth_scopes.ACCOUNT_MGMT])
def user_exists(request, oauth2_context):
    """Lists all users matching filter. If no user is found, the error key 
    will be available in the response.
    
    Request::
    
        GET /0.1/users/exists
    
    Parameters:
        email (mandatory)
            The user id with this email address will be shown
    
    Returns::
    
        {
            "id": 480
        }
        
    """
    # Mandatory parameter check
    if not set(['email']).issubset(set(request.params)):
        raise HTTPBadRequest()
    
    # Parameters
    email = request.params.get('email')
    
    result = send_task("tickee.users.entrypoints.user_exists", 
                       kwargs=dict(email=email)).get()
    return result



@view_config(route_name='01-user-create', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL,
                        oauth_scopes.ACCOUNT_MGMT])
def user_create(request, oauth2_context):
    """Creates a user and returns his id.
    
    Request::
    
        POST /0.1/users/create
    
    Parameters:
        email (mandatory)
            Specifies the email of the user to create
        password (optional)
            Specifies the password of the newly created user.
    
    Returns::
    
        {
            "id": 480
        }
        
    """
    # Mandatory parameter check
    if not set(['email']).issubset(set(request.params)):
        raise HTTPBadRequest()
    # Parameters
    email = request.params.get('email')
    password = request.params.get('password')  
     
    result = send_task("tickee.users.entrypoints.user_create", 
                       kwargs=dict(client_id=oauth2_context.client_id,
                                   email=email, 
                                   password=password)).get()
    return result



@view_config(route_name='01-user-details', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL,
                        oauth_scopes.ACCOUNT_MGMT])
def user_details(request, oauth2_context):
    """Creates a user and returns his id.
    
    Request::
    
        GET /0.1/users/{id}
    
    Parameters:
        include_orders (optional)
            When set either to true, t or 1, the result will contain all orders placed by the user.
    
    Returns::
    
        {
            "first_name": "John",
            "last_name": "Smith",
            "email": null,
            "orders": [
                {
                    "date": "2011-09-01T07:07:46",
                    "status": "timeout",
                    "id": 19,
                    "tickets": [
                        {
                            "id": "000000004",
                            "checked_in": false
                        },
                        ...
                    ]
                },
                ...
            ]
        }
        
    """
    # URL parameters
    user_id = request.matchdict.get('user_id')
    # Parameters
    include_orders = request.params.get('include_orders') in ['true', 't', '1']
    
    result = send_task("tickee.users.entrypoints.user_details", 
                       kwargs=dict(user_id=user_id,
                                   include_orders=include_orders)).get()
    return result