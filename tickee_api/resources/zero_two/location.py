from celery.execute import send_task
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes
from tickee_api.core import validate_schema
from tickee_api.resources.zero_two import schema

###############################################################################
# /locations
###############################################################################


@view_config(route_name='02-location-collection', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def location_list(request, oauth2_context):
    """ Returns a list of locations """
    name = request.params.get('name') 
    
    if name is not None:
        venue = send_task("venues.search", 
                         kwargs=dict(name_filter=name)).get()
        return venue
        
    return []

###############################################################################
# /events/:id/locations
###############################################################################

@view_config(route_name='02-event-locations', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def event_locations(request, oauth2_context):
    """Retrieves all locations connected to an event"""
    event_id = request.matchdict.get('event_id')
    
    result = send_task("venues.from_event",
                       kwargs=dict(client_id=None,
                                   event_id=event_id)).get()
    
    if isinstance(result, dict) and "error" in result:
        request.response.status_int = 404 
    else:
        request.response.status_int = 200 
        
    return result

###############################################################################
# /account/:shortname/locations
###############################################################################

@view_config(route_name='02-account-locations', request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def account_locations(request, oauth2_context):
    """Retrieves detailed information about an organizer."""
    account_name = request.matchdict.get('account_id')
    
    result = send_task("venues.from_account",
                       kwargs=dict(client_id=None,
                                   account_name=account_name)).get()
    
    if isinstance(result, dict) and "error" in result:
        request.response.status_int = 403 # forbidden
    else:
        request.response.status_int = 200 # created
        
    return result

@view_config(route_name='02-account-locations', request_method='POST', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
@validate_schema(schema.Location, required_nodes=["name"])
def location_create(request, oauth2_context):
    """Retrieves detailed information about an organizer."""
    location_info = request.deserialized_body
    address_info = location_info.get('address')
    account_name = request.matchdict.get('account_id')
    
    result = send_task("venues.create",
                       kwargs=dict(client_id=None,
                                   location_info=location_info,
                                   address_info=address_info,
                                   account_name=account_name)).get()
    
    if isinstance(result, dict) and "error" in result:
        request.response.status_int = 403 # forbidden
    else:
        request.response.status_int = 201 # created
        
    return result

###############################################################################
# /locations/:id
###############################################################################

@view_config(route_name='02-location-details',  request_method='DELETE', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
def location_delete(request, oauth2_context):
    """Retrieves detailed information about an organizer."""
    # URL Parameters
    location_id = int(request.matchdict.get('location_id'))

    result = send_task("venues.delete", 
                       kwargs=dict(location_id=location_id)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
    
    return result


@view_config(route_name='02-location-details',  request_method='GET', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def location_details(request, oauth2_context):
    """Retrieves detailed information about an organizer."""
    # URL Parameters
    location_id = int(request.matchdict.get('location_id'))

    result = send_task("venues.details", 
                       kwargs=dict(location_id=location_id,
                                   include_address=True)).get()
    
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
    
    return result


@view_config(route_name='02-location-details', request_method='PUT', 
             renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.INTERNAL])
@validate_schema(schema.Location)
def location_update(request, oauth2_context):
    """Updates location information"""
    location_id = int(request.matchdict.get('location_id'))
    location_info = request.deserialized_body
    address_info = location_info.get('address')
    
    result = send_task("venues.update", 
                       kwargs=dict(client_id=None,
                                   location_id=location_id,
                                   location_info=location_info,
                                   address_info=address_info)).get()
                                   
    if type(result) is dict and "error" in result:
        request.response.status_int = 404
    else:
        request.response.status_int = 200
        
    return result
