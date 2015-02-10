from celery.execute import send_task
from pyramid.httpexceptions import HTTPBadRequest, HTTPAccepted
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes


@view_config(route_name='01-order-mail', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def order_mail(request, oauth2_context):
    """ Resends the order to the user.
    
    Request::
    
        POST /0.1/orders/{orderkey}/mail
        
    Parameters:
    
        None
        
    Returns::
        
        202 ACCEPTED
    """
    # URL Parameters
    order_key = request.matchdict.get('order_key')
    
    result = send_task("orders.resend", 
                       kwargs=dict(client_id=oauth2_context.client_id,
                                   order_key=order_key)).get()
    return result



@view_config(route_name='01-order-details', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def order_details(request, oauth2_context):
    """Returns all information about an order.
    
    Request::
    
        GET /0.1/orders/{orderkey}
    
    Parameters:
        None
            
    Returns::
    
         {
            "tickets": [
                {
                    "id": "000000003",
                    "checked_in": false
                }
            ],
            "user_mail": "kevin@tick.ee",
            "status": "started",
            "user": "Kevin Van Wilder",
            "id": 18,
            "meta": {
                "redirect_url": 
            }
        }
        
    .. note:: The response of this query is not yet stable.
    """
    # URL Parameters
    order_key = request.matchdict.get('order_key')
    
    result = send_task("tickee.orders.entrypoints.order_details", 
                       kwargs=dict(client_id=oauth2_context.client_id, 
                                   order_key=order_key))
    return result.get()
    



@view_config(route_name='01-order-checkout', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def order_checkout(request, oauth2_context):
    """Will start the checkout procedure with the paymentprovider and returns the
    information necessary to complete the transaction.
    
    Request::
    
        POST /0.1/orders/{orderkey}/checkout
    
    Parameters:
        
        redirect_url (optional)
            An optional url the account owner can set to redirect after the payment
            has been processed completely.
        gift (optional, only available for INTERNAL scope)
            If t, true or 1, the payment process will be skipped and the order will
            be treated as a gift.
            
            
    Returns::
    
        {
            "status": "started",
            "payment_info": {
                "payment_url": "https://testpay.multisafepay.com/checkout/?transaction=1319702165PAbQjyqDt6PYYHR9&lang=NL_be",
                "provider": "Multisafepay"
            },
            "order": {
                "ordered_tickets": [
                    {
                        "amount": 1,
                        "name": "Ticket"
                    },
                    ...
                ],
                "total": 1000,
                "key": "8933daa2f6e372a3f73b72ea056c2283"
            }
        }
        
    """
    # URL Parameters
    order_key = request.matchdict.get('order_key')
    # Optional Parameters
    redirect_url = request.params.get('redirect_url')
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        is_gift = request.params.get('gift') in ['t', 'true', '1']
    else:
        is_gift = False
    
    if is_gift:
        result = send_task('orders.gift',
                           kwargs=dict(client_id=oauth2_context.client_id,
                                       order_key=order_key))
    else:
        result = send_task("tickee.paymentproviders.entrypoints.checkout_order", 
                           kwargs=dict(client_id=oauth2_context.client_id,
                                       order_key=order_key,
                                       redirect_url=redirect_url))
    return result.get()



@view_config(route_name='01-order-add', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def order_add(request, oauth2_context):
    """Creates an event and returns its id.
    
    Request::
    
        POST /0.1/orders/{orderkey}/add
    
    Parameters:
        tickettype_id (mandatory)
        amount (mandatory)        
            
    Returns::
    
        {
            "key": "941e0eba619ea4445d26a1dc23afa9ab"
        }
        
    """
    # URL Parameters
    order_key = request.matchdict.get('order_key')
    # Mandatory parameter check
    if not set(['tickettype_id', 'amount']).issubset(set(request.params)):
        raise HTTPBadRequest()
        
    # Parameters
    try:
        tickettype_id = int(request.params.get('tickettype_id'))
        amount = int(request.params.get('amount'))
    except ValueError:
        raise HTTPBadRequest()
        
    result = send_task("tickee.orders.entrypoints.order_add", 
                       kwargs=dict(client_id=oauth2_context.client_id,
                                   order_key=order_key,
                                   tickettype_id=tickettype_id,
                                   amount=amount))
    return result.get()



@view_config(route_name='01-order-new', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT])
def order_new(request, oauth2_context):
    """Starts a new order that can be purchased using the client's paymentprovider.
    If the user already had an started order for that account, it will be 
    added to that one instead of creating a new one.
    
    Request::
    
        POST /0.1/orders/add
    
    Parameters:
        tickettype_id (mandatory)
            The tickettype to be purchased
        user_id (mandatory)
            The user purchasing the ticket
        amount (mandatory)
            The amount of tickets that the user wishes to purchase
            
    Returns::
    
        {
            "key": "941e0eba619ea4445d26a1dc23afa9ab"
        }
        
    """
    # Mandatory parameter check
    if not set(['tickettype_id', 'user_id', 'amount']).issubset(set(request.params)):
        raise HTTPBadRequest()
        
    # Parameters
    try:
        user_id = int(request.params.get('user_id'))
        tickettype_id = int(request.params.get('tickettype_id'))
        amount = int(request.params.get('amount'))
    except ValueError:
        raise HTTPBadRequest()
        
    result = send_task("tickee.orders.entrypoints.order_new", 
                       kwargs=dict(client_id=oauth2_context.client_id, 
                                   user_id=user_id,
                                   tickettype_id=tickettype_id,
                                   amount=amount))
    return result.get()