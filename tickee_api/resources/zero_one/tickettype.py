from celery.execute import send_task
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes
import datetime
import time

#    config.add_route('01-tickettype-create',       '/0.1/tickettype/create')
#    config.add_route('01-tickettype-details',      '/0.1/tickettype/{tickettype_id:\d+}')
#    config.add_route('01-tickettype-update',       '/0.1/tickettype/{tickettype_id:\d+}/update')

@view_config(route_name='01-tickettype-resource', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def tickettype_details(request, oauth2_context):
    """Shows information of a tickettype
    
    Request::
    
        GET /0.1/tickettypes/{id}
    
    Parameters:
    
        None
    """
    # URL Parameters
    tickettype_id = request.matchdict.get('tickettype_id')
    
    # Parameters
    kwargs = dict(request.params)
    kwargs['tickettype_id'] = tickettype_id
    kwargs['client_id'] = oauth2_context.client_id

    result = send_task("tickettypes.details", 
                       kwargs=kwargs)
    return result.get()


@view_config(route_name='01-tickettype-resource', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def tickettype_update(request, oauth2_context):
    """Update a tickettype
    
    Request::
    
        POST /0.1/tickettypes/{id}
    
    Parameters:
    
        name (optional)
            Name of the ticket
        price (optional)
            Price without handling fee.
        currency (optional)
            The currency of the price. 
        quantity (optional)
            Quantity of tickets that can be sold. 
        handling_fee (optional)
            Additional fee to cover the transaction costs of your payment provider. 
        min_order (optional)
            Minimum amount of tickets to order. 
        max_order (optional)
            Maxumum amount of tickets to order at once. 
        sales_start (optional)
            Epoch timestamp when ticket type can be bought. 
        sales_end (optional)
            Epoch timestamp when purchase of this ticket type is stopped. 
        description (optional)
            Additional information about this ticket. 
    """
    # URL Parameters
    tickettype_id = request.matchdict.get('tickettype_id')
    
    # Parameters
    kwargs = dict(request.params)
    kwargs['tickettype_id'] = tickettype_id
    kwargs['client_id'] = oauth2_context.client_id

    result = send_task("tickettypes.update", 
                       kwargs=kwargs)
    return result.get()





@view_config(route_name='01-tickettype-create', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def tickettype_create(request, oauth2_context):
    """Creates a tickettype for an event
    
    Request::
    
        POST /0.1/tickettype/create
    
    Parameters:
        event_id | eventpart_id (mandatory)
            Select where to link this ticket type either choosing the event_id or 
            eventpart_id. In case of eventpart_id, the ticket will only be linked
            to that particular part. When the event_id is passed, it will be linked
            to all eventparts. 
        name (mandatory)
            Name of the ticket
        price (optional)
            Price without handling fee. Defaults to 0 (free).
        currency (optional)
            The currency of the price. 
            Defaults to EUR.
        quantity (optional)
            Quantity of tickets that can be sold. 
            Defaults to 100 units.
        handling_fee (optional)
            Additional fee to cover the transaction costs of your payment provider. 
            Defaults to 0
        min_order (optional)
            Minimum amount of tickets to order. 
            Defaults to 1
        max_order (optional)
            Maxumum amount of tickets to order at once. 
            Defaults to 10. 
        sales_start (optional)
            Epoch timestamp when ticket type can be bought. 
            Defaults to the start of the event/eventpart.
        sales_end (optional)
            Epoch timestamp when purchase of this ticket type is stopped. 
            Defaults to the end of the event/eventpart.
        description (optional)
            Additional information about this ticket. 
            Defaults to empty string.
            
    Returns::
    
        {
            "available": 100,
            "currency": "EUR",
            "price": 0,
            "name": "Regular",
            "id": 5
        }
        
    """
    # Mandatory parameter check
    if not set(['name']).issubset(set(request.params))\
       and ("event_id" in request.params or "eventpart_id" in request.params):
        raise HTTPBadRequest()
    # Parameters
    kwargs = dict(request.params)
    kwargs['client_id'] = oauth2_context.client_id

    
    result = send_task("tickettypes.create", 
                       kwargs=kwargs)
    return result.get()