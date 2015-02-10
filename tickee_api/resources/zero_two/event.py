# -*- coding: utf-8 -*-
from celery.execute import send_task
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes
from tickee_api.core import return_fields, validate_schema
from tickee_api.resources.zero_two import schema

###############################################################################
# /events
###############################################################################

@view_config(route_name='02-event-list', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL, oauth_scopes.ACCOUNT_MGMT])
def event_list(request, oauth2_context):
    
    """ Returns a list of upcoming (public) events. """
    include_inactive = request.params.get('include_inactive') in ['true', 't', '1']
    include_private = request.params.get('include_private') in ['true', 't', '1']
    include_past = request.params.get('include_past') in ['true', 't', '1']
    
    result = send_task("tickee.events.entrypoints.event_list", 
                       kwargs=dict(client_id=None,
                                   account_shortname=None,
                                   active_only=not include_inactive,
                                   public_only=not include_private,
                                   past=include_past)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
    
    return result

###############################################################################
# /account/:shortname/events
###############################################################################

@view_config(route_name='02-account-events', request_method='GET', 
             renderer='json')
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
    
    """
    account_shortname = request.matchdict.get('account_id')     
    # parameters
    include_inactive = request.params.get('include_inactive') in ['true', 't', '1']
    include_private = request.params.get('include_private') in ['true', 't', '1']
    include_past = request.params.get('include_past') in ['true', 't', '1']
    include_description = request.params.get('include_description') in ['true', 't', '1']
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
        
    result = send_task("tickee.events.entrypoints.event_list", 
                       kwargs=dict(client_id=client_id,
                                   account_shortname=account_shortname,
                                   active_only=not include_inactive,
                                   public_only=not include_private,
                                   past=include_past)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200                               
        # remove description if not requested
        if not include_description:
            for event in result:
                if 'description' in event:
                    event.pop('description')
    
    return result


@view_config(route_name='02-account-events', request_method='POST', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
@validate_schema(schema.Event, 
                 required_nodes=["name"])
def event_create(request, oauth2_context):
    """ Creates an event and returns its id. """
    account_shortname = request.matchdict.get('account_id')
    event_info = request.deserialized_body
    eventparts = event_info.pop('parts')
    
    # create event linked to account_id
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
        
    result = send_task("tickee.events.entrypoints.event_create", 
                       kwargs=dict(client_id=client_id, 
                                   account_short=account_shortname,
                                   event_info=event_info,
                                   eventparts=eventparts or [])).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 403
    else:
        request.response.status_int = 201
    
    return result


###############################################################################
# /events/:id
###############################################################################

@view_config(route_name='02-event-resource', request_method='DELETE', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def event_delete(request, oauth2_context):
    """Retrieves detailed information about an organizer."""

    event_id = request.matchdict.get('event_id')
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
    
    result = send_task("events.delete", 
                       kwargs=dict(client_id=client_id, 
                                   event_id=event_id)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
    
    return result



@view_config(route_name='02-event-resource', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.SCANNING,
                        oauth_scopes.INTERNAL])
def event_details(request, oauth2_context):
    """Retrieves detailed information about an organizer."""

    event_id = request.matchdict.get('event_id')

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
                                   include_eventparts=include_eventparts)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
    
    return result



@view_config(route_name='02-event-resource', request_method='PUT', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
@validate_schema(schema.Event)
def event_update(request, oauth2_context):
    """Updates event information. If for any reason the update fails, the
    error key will be available in the response. """
    
    # URL Parameters
    event_id = request.matchdict.get('event_id')
    event_info = request.deserialized_body
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
    
    result = send_task("events.update", 
                       kwargs=dict(client_id=client_id, 
                                   event_id=event_id,
                                   event_info=event_info)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
    
    return result

###############################################################################
# /events/:id/statistics
###############################################################################

@view_config(route_name='02-event-statistics', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def event_statistics(request, oauth2_context):
    """Retrieves detailed information about an organizer."""
    event_id = request.matchdict.get('event_id')
    result = send_task("tickee.statistics.entrypoints.event_statistics", 
                       kwargs=dict(client_id=None, 
                                   event_id=event_id))
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
    
    return result.get()

###############################################################################
# /events/:id/eventparts
###############################################################################

@view_config(route_name='02-event-parts', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def eventpart_lists(request, oauth2_context):
    """Lists all eventparts of an event"""
    event_id = request.matchdict.get('event_id')
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
    
    result = send_task("eventparts.from_event", 
                       kwargs=dict(client_id=client_id, 
                                   event_id=event_id)).get()
    
    if type(result) is dict and "error" in result:
            request.response.status_int = 404
    else:
        request.response.status_int = 200
        
    return result


@view_config(route_name='02-event-parts', request_method='POST', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
@validate_schema(schema.EventPart)
def eventpart_create(request, oauth2_context):
    """Lists all eventparts of an event"""
    event_id = request.matchdict.get('event_id')
    eventpart_info = request.deserialized_body
    
    result = send_task("eventparts.create", 
                       kwargs=dict(client_id=None, 
                                   event_id=event_id,
                                   eventpart_info=eventpart_info)).get()
    
    if type(result) is dict and "error" in result:
            request.response.status_int = 404
    else:
        request.response.status_int = 200
        
    return result

###############################################################################
# /eventparts/:id
###############################################################################

@view_config(route_name='02-parts-resource', request_method='DELETE',
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def eventpart_delete(request, oauth2_context):
    """Show details about the eventpart"""
    eventpart_id = request.matchdict.get('eventpart_id')
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
    
    result = send_task("eventparts.delete",
                       kwargs=dict(client_id=client_id,
                                   eventpart_id=eventpart_id)).get()
    
    if type(result) is dict and "error" in result:
            request.response.status_int = 404
    else:
        request.response.status_int = 200
    
    return result


@view_config(route_name='02-parts-resource', request_method='GET',
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL,
                        oauth_scopes.ACCOUNT_MGMT])
def eventpart_details(request, oauth2_context):
    """Show details about the eventpart"""
    eventpart_id = request.matchdict.get('eventpart_id')
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
    
    result = send_task("eventparts.details",
                       kwargs=dict(client_id=client_id,
                                   eventpart_id=eventpart_id)).get()
    
    if type(result) is dict and "error" in result:
            request.response.status_int = 404
    else:
        request.response.status_int = 200
    
    return result


@view_config(route_name='02-parts-resource', request_method='PUT',
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
@validate_schema(schema.EventPart)
def eventpart_update(request, oauth2_context):
    """Update details about the eventpart"""
    eventpart_id = request.matchdict.get('eventpart_id')
    eventpart_info = request.deserialized_body
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id = oauth2_context.client_id
    
    result = send_task("eventparts.update",
                       kwargs=dict(client_id=client_id,
                                   eventpart_id=eventpart_id,
                                   eventpart_info=eventpart_info)).get()
    
    if type(result) is dict and "error" in result:
            request.response.status_int = 404
    else:
        request.response.status_int = 200
    
    return result