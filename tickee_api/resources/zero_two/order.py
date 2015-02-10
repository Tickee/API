from celery.execute import send_task
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes
from tickee_api.core import validate_schema
from tickee_api.resources.zero_two import schema

###############################################################################
# /events/:id/orders
###############################################################################

@view_config(route_name='02-event-orders', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def event_orders(request, oauth2_context):
    """ Returns orders associated with an event  """
    event_id = request.matchdict.get('event_id')
    
    # client_id setting
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id 
    
    # call entrypoint
    result = send_task("orders.from_event", 
                       kwargs=dict(client_id=client_id,
                                   event_id=event_id)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404

    return result

###############################################################################
# /accounts/:id/orders
###############################################################################

@view_config(route_name='02-account-orders-collection', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def account_orders(request, oauth2_context):
    """ Returns orders associated with an event  """
    account_id = request.matchdict.get('account_id')
    
    # client_id setting
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id 
    
    # call entrypoint
    result = send_task("orders.from_account", 
                       kwargs=dict(client_id=client_id,
                                   account_id=account_id)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404

    return result

###############################################################################
# /users/:id/orders
###############################################################################

@view_config(route_name='02-user-orders', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
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
    
        GET /users/{id}/orders
    
    Parameters:
    
        None
        
    Returns:
        
        A list of all orders
    
    """
    user_id = request.matchdict.get('user_id')
    
    include_private = request.params.get('include_private') in ['t', 'true', '1']
    
    # client_id setting
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id 
    
    # call entrypoint
    result = send_task("orders.from_user", 
                       kwargs=dict(client_id=client_id,
                                   user_id=user_id,
                                   include_failed=include_private)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404

    return result



###############################################################################
# /account/{shortname}/orders
###############################################################################

@view_config(route_name='02-account-orders-collection', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
@validate_schema(schema.TicketOrder, required_nodes=["tickettype", "amount"])
def order_new(request, oauth2_context):
    """ Starts a new order that can be purchased using the client's paymentprovider.
    If the user already had a started order for that account, it will be 
    added to that one instead of creating a new one. """
    
    account_short = request.matchdict.get('account_id')
    ticketorder_info = request.deserialized_body
    as_guest = ticketorder_info.get('guest')
    as_paper = ticketorder_info.get('paper')
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
    
    result = send_task("tickee.orders.entrypoints.order_new", 
                       kwargs=dict(client_id=client_id, 
                                   account_short=account_short,
                                   user_id=ticketorder_info.get('user'),
                                   tickettype_id=ticketorder_info.get('tickettype'),
                                   amount=ticketorder_info.get('amount'),
                                   as_guest=as_guest,
                                   as_paper=as_paper)).get()
                                   
    if type(result) is dict and "error" in result:
        request.response.status_int = 403
    else:
        request.response.status_int = 201
    
    return result

###############################################################################
# /orders
###############################################################################

@view_config(route_name='02-orders',
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def orders_list(request, oauth2_context):
    """ Returns a list of orders matching the given criteria """
    order_id = request.params.get('id')
    
    if order_id is None:
        return []
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
    
    result = send_task("orders.list",
                       kwargs=dict(client_id=client_id,
                                   order_id=order_id)).get()
            
    return result


###############################################################################
# /orders/{order_key}
###############################################################################

@view_config(route_name='02-orders-detail', 
             request_method='DELETE', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def order_delete(request, oauth2_context):
    """ Returns all information about an order. """
    
    order_key = request.matchdict.get('order_key')
    
    result = send_task("orders.delete", 
                       kwargs=dict(client_id=oauth2_context.client_id, 
                                   order_key=order_key)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
    
    return result

@view_config(route_name='02-orders-detail', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def order_details(request, oauth2_context):
    """ Returns all information about an order. """
    
    order_key = request.matchdict.get('order_key')
    
    result = send_task("tickee.orders.entrypoints.order_details", 
                       kwargs=dict(client_id=oauth2_context.client_id, 
                                   order_key=order_key)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    
    return result


@view_config(route_name='02-orders-detail', 
             request_method='PUT', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
@validate_schema(schema.TicketOrder, required_nodes=["tickettype", "amount"])
def order_add(request, oauth2_context):
    
    order_key = request.matchdict.get('order_key')
    ticketorder_info = request.json_body
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
        
    result = send_task("tickee.orders.entrypoints.order_add", 
                       kwargs=dict(client_id=client_id,
                                   order_key=order_key,
                                   tickettype_id=ticketorder_info.get('tickettype'),
                                   amount=ticketorder_info.get('amount'),
                                   meta=ticketorder_info)).get()
                                   
    if type(result) is dict and "error" in result:
        request.response.status_int = 403
    
    return result



@view_config(route_name='02-orders-detail', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
@validate_schema(schema.OrderAction)
def order_action(request, oauth2_context):
    """ Returns all information about an order. """
    
    order_key = request.matchdict.get('order_key')
    actions = request.json_body

    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
    
    if actions.get('checkout'):
        user_id = actions.get('user')
        redirect_url = actions.get('redirect_url')
        result = send_task("orders.checkout", 
                           kwargs=dict(client_id=client_id,
                                       order_key=order_key,
                                       user_id=user_id,
                                       redirect_url=redirect_url)).get() 
    elif actions.get('mail'):
        result = send_task("orders.resend", 
                           kwargs=dict(client_id=client_id,
                                       order_key=order_key)).get()
                                       
    else:
        request.response.status_int = 400
        result = None
        
    if type(result) is dict and "error" in result:
        request.response.status_int = 403
    
    return result

###############################################################################
# /orders/started/{order_key}
###############################################################################

@view_config(route_name='02-orders-started-detail', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def order_started_details(request, oauth2_context):
    """ Returns all information about an order. """
    
    order_key = request.matchdict.get('order_key')
    
    result = send_task("orders.started.details", 
                       kwargs=dict(client_id=oauth2_context.client_id, 
                                   order_key=order_key)).get()
    
    if "error" in result:
        request.response.status_int = 404
        return None
    else:
        return result