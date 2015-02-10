from celery.execute import send_task
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes
from tickee_api.core import return_fields, validate_schema
from tickee_api.resources.zero_two import schema

###############################################################################
# /eventparts/:id/tickettypes
###############################################################################

@view_config(route_name='02-parts-tickettypes', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def eventpart_tickettype_list(request, oauth2_context):
    """Displays a list of tickettypes within an eventpart"""
    eventpart_id = request.matchdict.get('eventpart_id')
    include_private = request.params.get('include_private') in ['true', 't', '1']
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id =  oauth2_context.client_id
    
    result = send_task("tickettypes.from_eventpart", 
                       kwargs=dict(client_id=client_id,
                                   eventpart_id=eventpart_id,
                                   include_private=include_private)).get()

    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200                               
    
    return result


@view_config(route_name='02-parts-tickettypes', request_method='POST', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
@validate_schema(schema.TicketType)
def eventpart_tickettype_create(request, oauth2_context):
    """Displays a list of tickettypes within an eventpart"""
    eventpart_id = request.matchdict.get('eventpart_id')
    
    tickettype_info = request.deserialized_body

    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id =  oauth2_context.client_id
    
    result = send_task("tickettypes.create", 
                       kwargs=dict(client_id=client_id, 
                                   tickettype_info=tickettype_info, 
                                   eventpart_id=eventpart_id)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 403
        
    return result


###############################################################################
# /events/:id/tickettypes
###############################################################################

@view_config(route_name='02-event-tickettypes', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
@return_fields(mandatory_fields=['id', 'name', 'price', 'availability', 'active'])
def event_tickettype_list(request, oauth2_context):
    """Displays a list of tickettypes within an event."""
    event_id = request.matchdict.get('event_id')
    include_private = request.params.get('include_private') in ['true', 't', '1']
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id =  oauth2_context.client_id
    
    result = send_task("tickettypes.from_event", 
                       kwargs=dict(client_id=client_id,
                                   event_id=event_id,
                                   include_private=include_private)).get()

    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200                               
    
    return result


@view_config(route_name='02-event-tickettypes', request_method='POST', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
@validate_schema(schema.TicketType)
def tickettype_create(request, oauth2_context):
    """Creates a tickettype for an event"""
    event_id = request.matchdict.get('event_id')
    tickettype_info = request.deserialized_body

    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id =  oauth2_context.client_id
    
    result = send_task("tickettypes.create", 
                       kwargs=dict(client_id=client_id, 
                                   tickettype_info=tickettype_info, 
                                   event_id=event_id)).get()
                                   
    if type(result) is dict and "error" in result:
        request.response.status_int = 403
        
    return result

###############################################################################
# /tickettypes/:id
###############################################################################

@view_config(route_name='02-tickettype-resource', request_method='DELETE', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def tickettype_delete(request, oauth2_context):
    """Deletes a tickettype"""
    # URL Parameters
    tickettype_id = request.matchdict.get('tickettype_id')
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id =  oauth2_context.client_id
    
    result = send_task("tickettypes.delete", 
                       kwargs=dict(client_id=client_id,
                                   tickettype_id=tickettype_id)).get()
                       
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
    return result

@view_config(route_name='02-tickettype-resource', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def tickettype_details(request, oauth2_context):
    """Shows information of a tickettype"""
    # URL Parameters
    tickettype_id = request.matchdict.get('tickettype_id')
    
    # Parameters
    kwargs = dict(request.params)
    kwargs['tickettype_id'] = tickettype_id
    kwargs['client_id'] = oauth2_context.client_id

    result = send_task("tickettypes.details", 
                       kwargs=kwargs).get()
                       
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
        
    return result


@view_config(route_name='02-tickettype-resource', request_method='PUT', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
@validate_schema(schema.TicketType)
def tickettype_update(request, oauth2_context):
    """Update a tickettype"""
    tickettype_id = request.matchdict.get('tickettype_id')
    tickettype_info = request.deserialized_body
    
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        client_id = None
    else:
        client_id =  oauth2_context.client_id
    
    # Parameters
    kwargs = dict(request.params)
    kwargs['tickettype_id'] = tickettype_id
    kwargs['client_id'] = oauth2_context.client_id

    result = send_task("tickettypes.update", 
                       kwargs=dict(client_id=client_id,
                                   tickettype_id=tickettype_id,
                                   tickettype_info=tickettype_info)).get()
                                   
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
        
    return result




