from celery.execute import send_task
from pyramid.httpexceptions import HTTPBadRequest, HTTPAccepted
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes


@view_config(route_name='01-ticket-mail', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def ticket_mail(request, oauth2_context):
    """ Resends the ticket to the user.
    
    Request::
    
        POST /0.1/tickets/{code}/mail
        
    Parameters:
    
        None
        
    Returns::
        
        200 OK
        
        true or false depending on whether the mail was sent correctly.
        
    """
    # URL Parameters
    ticket_code = request.matchdict.get('ticket_code')
    
    result = send_task("tickets.resend", 
                       kwargs=dict(client_id=oauth2_context.client_id,
                                   ticket_code=ticket_code)).get()
    return result



@view_config(route_name='01-ticket-details', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def ticket_details(request, oauth2_context):
    """Creates an event and returns its id.
    
    Request::
    
        GET /0.1/tickets/{code}
    
    Parameters:
        None.
            
    Returns::
    
        {
            "checked_in": false,
            "created_at": "2011-10-10T23:59:59",
            "venues": [
                {
                    "city": "Ghent",
                    "name": "ven 1",
                    "id": 1
                },
                ...
                {
                    "city": "Ghent",
                    "name": "ven 2",
                    "id": 2
                }
            ],
            "user": {
                "first_name": "Kevin",
                "last_name": "Van Wilder",
                "id": 1
            },
            "id": "000000001",
            "tickettype": {
                "currency": "EUR",
                "price": 10,
                "description": null,
                "id": 1,
                "name": "Regular"
            }
        }
        
    """
    # URL Parameters
    ticket_code = request.matchdict.get('ticket_code')
    
    result = send_task("tickee.tickets.entrypoints.ticket_details", 
                       kwargs=dict(client_id=None,
                                   ticket_code=ticket_code))
    return result.get()


@view_config(route_name='01-ticket-scan', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def ticket_scan(request, oauth2_context):
    """Scans in a ticket and receives diff updates from the server
    based on the list_* parameters it received.
    
    Request::
    
        POST /0.1/ticket/{code}/scan
    
    Parameters:
        scanned_at (mandatory)
        list_timestamp (mandatory)
        list_eventpart_id (mandatory)
        list_event_id (mandatory)
        list_tickettype_id (mandatory)
            
    Returns::
    
        {
            "timestamp": 1319721237,
            "scanned": true,
            "updates": [
                {
                    "user_id": 1,
                    "id": "000000001",
                    "scanned_at": "2011-10-26T16:17:08"
                },
                ...
            ],
            "new_tickets": [
                {
                    "id": "000000001",
                    "user": {
                        "first_name": "Koen",
                        "last_name": "Betsens",
                        "id": 1
                    }
                },
                ...
            ]
        }
        
    """
    # Mandatory parameter check
    if not set(['scanned_at', 'list_timestamp', 'list_eventpart_id', 
                'list_event_id', 'list_tickettype_id']).issubset(set(request.params)):
        raise HTTPBadRequest()
    # URL Parameters
    ticket_code = request.matchdict.get('ticket_code')
    # Parameters
    try:
        scanned_at = request.POST.pop('scanned_at')
        list_timestamp = request.POST.pop('list_timestamp')
        list_eventpart_id = int(request.POST.pop('list_eventpart_id'))
        list_event_id = int(request.POST.pop('list_event_id'))
        list_tickettype_id = int(request.POST.pop('list_tickettype_id'))
    except:
        raise HTTPBadRequest()
    
    result = send_task("tickee.scanning.entrypoints.ticket_scan", 
                       kwargs=dict(client_id=oauth2_context.client_id,
                                   ticket_code=ticket_code,
                                   scan_datetime=scanned_at,
                                   list_timestamp=list_timestamp, 
                                   list_eventpart_id=list_eventpart_id, 
                                   list_event_id=list_event_id,
                                   list_tickettype_id=list_tickettype_id,
                                   extra_info=request.POST.dict_of_lists()))
    return result.get()
    


@view_config(route_name='01-ticket-reset-scans', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def ticket_reset_scans(request, oauth2_context):
    """Resets all scans of tickets for an event. This reset can be refined
    by only resetting the scans of one of the eventparts or tickettype.
    
    Request::
    
        POST /0.1/ticket/resetscans
    
    Parameters:
        event_id (mandatory)
            Limits the reset to ticketscan for the event
        eventpart_id (optional)
            Restricts the reset even further for only a specific eventpart
        tickettype_id (optional)
            Restricts the reset even further for only a specific tickettype
            
    Returns::
    
        {
            "deleted": 9
        }
        
    """
    # Mandatory parameter check
    if not set(['event_id']).issubset(set(request.params)):
        raise HTTPBadRequest()
        
    # Parameters
    try:
        event_id = request.params.get('event_id')
        if "eventpart_id" in request.params:
            eventpart_id = int(request.params.get('eventpart_id'))
        else:
            eventpart_id = None
        if "tickettype_id" in request.params:
            tickettype_id = int(request.params.get('tickettype_id'))
        else:
            tickettype_id = None
    except:
        raise HTTPBadRequest()
        
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
        
    result = send_task("scanning.reset", 
                       kwargs=dict(client_id=client_id,
                                   event_id=event_id, 
                                   eventpart_id=eventpart_id, 
                                   tickettype_id=tickettype_id))
    return result.get()