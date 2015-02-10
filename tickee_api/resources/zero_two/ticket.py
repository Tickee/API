from celery.execute import send_task
from pyramid.httpexceptions import HTTPBadRequest, HTTPAccepted
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes
from tickee_api.core import return_fields, validate_schema
from tickee_api.resources.zero_two import schema


###############################################################################
# /events/:id/tickets
###############################################################################

@view_config(route_name='02-event-tickets', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.SCANNING,
                        oauth_scopes.INTERNAL])
@return_fields(default_fields=["user", "created_at", "checked_in"], 
               mandatory_fields=["id"])
def event_tickets(request, oauth2_context):
    """Retrieves the list of tickets that have been ordered for the event.
    A timestamp will also be included for asking diff-like updates of 
    the ticket states.
    
    Request::
    
        POST /event/{id}/tickets
    
    Parameters:
        tickettype_id (optional)
            Restricts the output to only tickets for a tickettype
        eventpart_id (optional)
            Restricts the output to only tickets for an eventpart
        location_id (optional)
            Restricts the output to only tickets for a location
        include_scan_state (optional)
            Information about the scanned state will be included
        include_user (optional)
            User owning the ticket will be included
        
    """
    event_id = request.matchdict.get('event_id')
    
    since = request.params.get('since')
    try:
        if since is not None: 
            since = int(since)
    except:
        raise HTTPBadRequest
        
    ttype = request.params.get('ttype')
    try:
        if ttype is not None: 
            ttype = int(ttype)
    except:
        raise HTTPBadRequest
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
    
    result = send_task("tickets.from_event", 
                       kwargs=dict(client_id=client_id, 
                                   event_id=event_id,
                                   since=since,
                                   ttype=ttype)).get()
    
    if isinstance(result, dict) and "error" in result:
        request.response.status_int = 404                     
    
    return result

   
###############################################################################
# /users/:id/tickets
###############################################################################
    
@view_config(route_name='02-user-tickets', request_method='GET', 
             renderer='json')
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
    
        GET /users/{id}/tickets
    
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
    
    if isinstance(result, dict) and "error" in result:
        request.response.status_int = 404                                 
    
    return result









@view_config(route_name='02-ticket-mail', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def ticket_mail(request, oauth2_context):
    """ Resends the ticket to the user.
    
    Request::
    
        POST /tickets/{code}/mail
        
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



@view_config(route_name='02-ticket-details', 
             request_method='DELETE', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def ticket_delete(request, oauth2_context):
    """Deletes a ticket"""
    ticket_code = request.matchdict.get('ticket_code')  
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id =  oauth2_context.client_id
    
    result = send_task("tickets.delete", 
                       kwargs=dict(client_id=client_id,
                                   ticket_code=ticket_code)).get()
                                   
    if isinstance(result, dict) and "error" in result:
        request.response.status_int = 404
    else: 
        request.response.status_int = 200
    return result


@view_config(route_name='02-ticket-details', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL,
                        oauth_scopes.SCANNING,
                        oauth_scopes.ACCOUNT_MGMT])
def ticket_details(request, oauth2_context):
    """Returns details of an event."""
    ticket_code = request.matchdict.get('ticket_code')  
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id =  oauth2_context.client_id
    
    result = send_task("tickee.tickets.entrypoints.ticket_details", 
                       kwargs=dict(client_id=client_id,
                                   ticket_code=ticket_code)).get()
                                   
    if isinstance(result, dict) and "error" in result:
        request.response.status_int = 404

    return result


@view_config(route_name='02-ticket-details', 
             request_method='PUT', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
@validate_schema(schema.Ticket)
def ticket_update(request, oauth2_context):
    """Returns details of an event."""
    ticket_code = request.matchdict.get('ticket_code')  
    ticket_info = request.deserialized_body
    
    result = send_task("tickets.update", 
                       kwargs=dict(ticket_info=ticket_info,
                                   ticket_code=ticket_code)).get()
                                   
    if isinstance(result, dict) and "error" in result:
        request.response.status_int = 404

    return result



@view_config(route_name='02-ticket-scans', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.SCANNING,
                        oauth_scopes.INTERNAL])
@return_fields(default_fields=['scanned_at'])
def ticket_scans(request, oauth2_context):
    """Returns a list of scans on a ticket. """
    ticket_code = request.matchdict.get('ticket_code')
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id =  oauth2_context.client_id
    
    result = send_task("scanning.from_ticket", 
                       kwargs=dict(client_id=client_id,
                                   ticket_code=ticket_code)).get()
    
    if isinstance(result, dict) and "error" in result:
        request.response.status_int = 404
    
    return result




@view_config(route_name='02-ticket-scans', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.SCANNING,
                        oauth_scopes.INTERNAL])
def ticket_scan(request, oauth2_context):
    """Scans in a ticket and receives diff updates from the server
    based on the list_* parameters it received."""
    ticket_code = request.matchdict.get('ticket_code')
    
#    scan_info = request.deserialized_body
    
    timestamp = request.params.get('timestamp')
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id =  oauth2_context.client_id
    
    result = send_task("scanning.scan", 
                       kwargs=dict(client_id=client_id,
                                   ticket_code=ticket_code,
                                   scan_timestamp=timestamp)).get()
                                   
    if isinstance(result, dict) and "error" in result:
        if result.get('error_number') == 701:
            request.response.status_int = 403
        else:
            request.response.status_int = 404
    else:
        request.response.status_int = 201
    
    return result
    


@view_config(route_name='02-ticket-reset-scans', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def ticket_reset_scans(request, oauth2_context):
    """Resets all scans of tickets for an event. This reset can be refined
    by only resetting the scans of one of the eventparts or tickettype.
    
    Request::
    
        POST /ticket/resetscans
    
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
                                   tickettype_id=tickettype_id)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
        
    return result