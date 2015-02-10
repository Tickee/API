# -*- coding: utf-8 -*-
from celery.execute import send_task
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes

#    config.add_route('01-event-access',            '/0.1/event/{event_id:\d+}/access')



@view_config(route_name='01-event-tickettypes', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def event_tickettype_list(request, oauth2_context):
    """Displays a list of tickettypes within an event.
    
    ============  ============================================================ 
    Scope         Description                 
    ============  ============================================================
    account_mgmt  shows all tickettypes, both active and inactive
    none          shows only active tickettypes
    ============  ============================================================
    
    Request::
        
        GET /0.1/events/{id}/tickettypes
    
    ..note:: Not implemented.
    
    """
    pass



@view_config(route_name='01-event-list', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT])
def event_list(request, oauth2_context):
    pass



@view_config(route_name='01-event-create', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def event_create(request, oauth2_context):
    """Creates an event and returns its id.
    
    Request::
    
        POST /0.1/events/create
    
    Parameters:
        event_name (mandatory)
            Name of the event
        account_id (mandatory for INTERNAL scope)
            The event will be linked to this account. This parameter is 
            only used by Tickee.
        venue_id (optional)
            Identifier of the venue where the event will be held
            
    Returns::
    
        {
            "dates": [
                null
            ],
            "account": 1,
            "name": "The Event Name",
            "id": 11
        }
        
    """
    # Mandatory parameter check
    if not set(['event_name']).issubset(set(request.params)):
        raise HTTPBadRequest()
    # Mandatory parameter check for INTERNAL
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        if not 'account_id' in request.params:
            raise HTTPBadRequest()
        
    # Parameters
    try:
        event_name = request.params.get('event_name')
        venue_id = int(request.params.get('venue_id', 0))
        account_id = int(request.params.get('account_id', 0))
    except ValueError:
        raise HTTPBadRequest()
        
    # create event linked to account_id
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        result = send_task("tickee.events.entrypoints.event_create", 
                           kwargs=dict(client_id=None, 
                                       event_name=event_name, 
                                       venue_id=venue_id,
                                       account_id=account_id))
    # create event linked to own account
    elif oauth_scopes.ACCOUNT_MGMT in oauth2_context.scopes:
        result = send_task("tickee.events.entrypoints.event_create", 
                           kwargs=dict(client_id=oauth2_context.client_id, 
                                       event_name=event_name,
                                       venue_id=venue_id, 
                                       account_id=None))
    return result.get()



@view_config(route_name='01-event-resource', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def event_details(request, oauth2_context):
    """Retrieves detailed information about an organizer.
    
    Request::
    
        POST /0.1/event/{id}
    
    Parameters:
        include_visitors (optional)
            The event owner can request a list of all people taking part.
            Default: no visitors will be included.
        include_eventparts (optional)
            Shows all eventparts of the event.
            Default: no eventparts will be included.
            
    Returns::
    
        {
            "account": 1,
            "tickettypes": [
                {
                    "currency": "EUR",
                    "description": "",
                    "price": 10,
                    "sold_out": false,
                    "name": "Ticket",
                    "id": 1
                },
                ...
            ],
            "name": "Galabal",
            "dates": [
                "2011-10-01T18:00:00",
                null
            ],
            "visitors": [
                ...
            ],
            "id": 1
        }
        
    """
    # URL Parameters
    event_id = request.matchdict.get('event_id')
    # Parameters
    include_visitors = request.params.get('include_visitors') in ['true', 't', '1']
    include_eventparts = request.params.get('include_eventparts') in ['true', 't', '1']
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
    
    result = send_task("tickee.events.entrypoints.event_details", 
                       kwargs=dict(client_id=client_id, 
                                   event_id=event_id,
                                   include_visitors=include_visitors,
                                   include_eventparts=include_eventparts))
    return result.get()



@view_config(route_name='01-event-resource', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def event_update(request, oauth2_context):
    """Updates event information. If for any reason the update fails, the
    error key will be available in the response.
    
    Request::
    
        POST /0.1/event/{id}
    
    Parameters:
        event_name (optional)
            Renames event
        venue_id (optional)
            Relocates event
        activate (optional)
            Makes event visible
            
    Returns::
    
        {
            "updated": true
        }
        
    """
    # URL Parameters
    event_id = request.matchdict.get('event_id')
    # Parameters
    try:
        event_name = request.params.get('event_name')
        venue_id = request.params.get('venue_id')
        activate = request.params.get('activate')
    except ValueError:
        raise HTTPBadRequest()
    
    # handle activate
    if activate is not None:
        activate = activate in ['true', 't', '1']
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
    
    result = send_task("tickee.events.entrypoints.event_update", 
                       kwargs=dict(client_id=client_id, 
                                   event_id=event_id,
                                   values_dict=dict(event_name=event_name,
                                                    venue_id=venue_id,
                                                    activate=activate)))
    return result.get()



@view_config(route_name='01-event-tickets', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def event_tickets(request, oauth2_context):
    """Retrieves the list of tickets that have been ordered for the event.
    A timestamp will also be included for asking diff-like updates of 
    the ticket states.
    
    Request::
    
        POST /0.1/event/{id}/tickets
    
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
            
    Returns::
        
        {
            "tickets": [
                {
                    "user": {
                        "first_name": "Kevin",
                        "last_name": "Van Wilder",
                        "id": 2
                    },
                    "checked_in": false,
                    "id": "000000003"
                },
                ...
            ],
            "timestamp": 1319638627
        }
        
    """
    # URL Parameters
    event_id = request.matchdict.get('event_id')
    # Parameters
    tickettype_id = request.params.get('tickettype_id')
    eventpart_id = request.params.get('eventpart_id')
    location_id = request.params.get('location_id')
    include_scan_state = request.params.get('include_scan_state') in ['true', 't', '1']
    include_user = request.params.get('include_user') in ['true', 't', '1']
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
    
    result = send_task("tickee.events.entrypoints.event_tickets", 
                       kwargs=dict(client_id=client_id, 
                                   event_id=event_id,
                                   tickettype_id=tickettype_id,
                                   eventpart_id=eventpart_id,
                                   location_id=location_id,
                                   include_scan_state=include_scan_state,
                                   include_user=include_user))
    return result.get()



@view_config(route_name='01-event-statistics', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT])
def event_statistics(request, oauth2_context):
    """Retrieves detailed information about an organizer.
    
    Request::
    
        GET /0.1/event/{id}/statistics
    
    Parameters:
        
            
    Returns:
    
        
        
    """
    pass



@view_config(route_name='01-event-access', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def event_access(request, oauth2_context):
    """Retrieves detailed information about an organizer.
    
    Request::
    
        GET /0.1/event/{id}/access
    
    Parameters:
        tickettype_id (optional)
            Restricts the output to only tickets for a tickettype
        eventpart_id (optional)
            Restricts the output to only tickets for an eventpart
        location_id (optional)
            Restricts the output to only tickets for a location        
            
    Returns::
    
        {
            "access_code": "{\"account\": 1, \"secret\": \"secret\", \"key\": \"9gWmSwgL\", \"event\": 1}"
        }
        
    """
    # URL Parameters
    event_id = request.matchdict.get('event_id')
    # Parameters
    eventpart_id = request.params.get('eventpart_id')
    tickettype_id = request.params.get('tickettype_id')
    location_id = request.params.get('location_id')
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
    
    result = send_task("tickee.scanning.entrypoints.access_code", 
                       kwargs=dict(client_id=client_id, 
                                   event_id=event_id,
                                   tickettype_id=tickettype_id,
                                   eventpart_id=eventpart_id,
                                   location_id=location_id))
    return result.get()
    
    
@view_config(route_name='01-event-addpart', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT])
def event_addpart(request, oauth2_context):
    """Adds an extra eventpart to an existing event.
    
    Request::
    
        POST /0.1/event/{id}/addpart
    
    Parameters:
        venue_id (mandatory)
            The venue where this part is being held
        name (mandatory)
            The name of the part, e.g. "Day 1" or "Time Square"
        description (optional)
            Small text describing the content of this part.
        starts_on (optional)
            Datetime this part is taking place
        ends_on (optional)
            Datetime this part ends.
            
    Returns::
    
        {
            "dates": [
                null
            ],
            "eventparts": [
                {
                    "name": "Party @ tickee",
                    "venue": "1",
                    "starts_on": null,
                    "ends_on": null,
                    "id": 1,
                    "description": null
                },
                ...
            ],
            "account": 1,
            "name": "Feestje",
            "id": 1
        }
        
    """
    # Mandatory parameter check
    if not set(['venue_id', 'name']).issubset(set(request.params)):
        raise HTTPBadRequest
    # URL Parameters
    event_id = request.matchdict.get('event_id')        
    # Parameters
    try:
        venue_id = request.params.get("venue_id")
        name = request.params.get("name")
        description = request.params.get("description")
        starts_on = request.params.get("starts_on")
        ends_on = request.params.get("ends_on")
    except:
        raise HTTPBadRequest
    
    result = send_task("tickee.events.eventparts.entrypoints.eventpart_create", 
                       kwargs=dict(client_id=oauth2_context.client_id,
                                   event_id=event_id,
                                   venue_id=venue_id,
                                   name=name,
                                   description=description,
                                   starts_on=starts_on,
                                   ends_on=ends_on))
    return result.get()    