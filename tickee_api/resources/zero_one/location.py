from celery.execute import send_task
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config
from pyramid_oauth2.decorator import oauth2
from tickee_api import oauth_scopes

    
@view_config(route_name='01-location-list', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def location_list(request, oauth2_context):
    """Retrieves detailed information about an organizer.
    
    Request::
    
        GET /0.1/location
    
    Parameters:
               
            
    Returns:
    
        
        
    """




@view_config(route_name='01-location-search', 
             request_method='GET', renderer='json')
def location_search(request):
    """Retrieves detailed information about an organizer.
    
    Request::
    
        GET /0.1/location/create
    
    Parameters:
        name (mandatory)
            Case insensitive substring of the location name
        limit (optional)
            Sets a maximum to the amount of results to be returned.
            
    Returns::
    
        [
            {
                "name": "'t Smis",
                "id": 2
            },
            ...
        ]
        
    """
    # Mandatory parameter check
    if not set(['name']).issubset(set(request.params)):
        raise HTTPBadRequest()
    
    # Parameters
    try:
        name_filter = request.params.get('name')
        limit = min(int(request.params.get('tickettype_id', 100)), 100)
    except Exception:
        raise HTTPBadRequest
    
    result = send_task("tickee.venues.entrypoints.location_search", 
                       kwargs=dict(name_filter=name_filter,
                                   limit=limit))
    return result.get()



@view_config(route_name='01-location-details', 
             request_method='GET', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def location_details(request, oauth2_context):
    """Retrieves detailed information about an organizer.
    
    Request::
    
        GET /0.1/location/{id}
    
    Parameters:
        include_address (optional)
            Includes the address for each result
            
    Returns::
    
        {
            "id": 1,
            "name": "Kunsthal Sint-Pietersabdij",
            "address": {
                "country": "BE",
                "street_line1": "Sint-Pietersplein 9",
                "street_line2": null,
                "postal_code": "9000",
                "city": "Gent"
            }
        }
        
    """
    # URL Parameters
    location_id = int(request.matchdict.get('location_id'))
    # Parameters
    include_address = request.params.get('include_address') in ['true', 't', '1']

    result = send_task("tickee.venues.entrypoints.location_details", 
                       kwargs=dict(location_id=location_id,
                                   include_address=include_address))
    return result.get()



@view_config(route_name='01-location-create', 
             request_method='POST', renderer='json')
@oauth2(allowed_scopes=[oauth_scopes.ACCOUNT_MGMT,
                        oauth_scopes.INTERNAL])
def location_create(request, oauth2_context):
    """Retrieves detailed information about an organizer.
    
    Request::
    
        POST /0.1/location/create
    
    Parameters:
        location_name (mandatory)
            name of the venue
        street_line1 (mandatory)
            first address line
        street_line2 (optional)
            second address line
        postal_code (mandatory)
        city (mandatory)
        country_code (mandatory)
            two character country code following the ISO-3166 standard
        latlng (optional)
            comma seperated latitude/longtitude of the venue location
        account_id (mandatory if INTERNAL)
            Account to which the location belongs
            
    Returns::
    
        {
            "id": 6,
            "name": "Markthal",
            "address": {
                "country": "BE",
                "street_line1": "Markt 3",
                "street_line2": null,
                "postal_code": "9160",
                "city": "Lokeren"
            }
        }
        
    """
    # Mandatory parameter check
    if not set(['location_name', 'street_line1', 'postal_code',
                'city', 'country_code']).issubset(set(request.params)):
        raise HTTPBadRequest
    # Mandatory parameter check for INTERNAL
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        if not 'account_id' in request.params:
            raise HTTPBadRequest
        
    # Parameters
    try:
        location_name = request.params.get("location_name")
        latlng = request.params.get("latlng")
        street_line1 = request.params.get("street_line1")
        street_line2 = request.params.get("street_line2")
        postal_code = request.params.get("postal_code")
        city = request.params.get("city")
        country_code = request.params.get("country_code")
        account_id = int(request.params.get("account_id", 0))
    except:
        raise HTTPBadRequest
    
    # create location linked to account_id
    if oauth_scopes.INTERNAL in oauth2_context.scopes:
        result = send_task("tickee.venues.entrypoints.location_create", 
                           kwargs=dict(client_id=None,
                                       location_name=location_name,
                                       latlng=latlng,
                                       address_dict=dict(street_line1=street_line1,
                                                        street_line2=street_line2,
                                                        postal_code=postal_code,
                                                        city=city,
                                                        country_code=country_code),
                                       account_id=account_id))
    # create location linked to own account
    elif oauth_scopes.ACCOUNT_MGMT in oauth2_context.scopes:
        result = send_task("tickee.venues.entrypoints.location_create", 
                           kwargs=dict(client_id=oauth2_context.client_id,
                                       location_name=location_name,
                                       latlng=latlng,
                                       address_dict=dict(street_line1=street_line1,
                                                        street_line2=street_line2,
                                                        postal_code=postal_code,
                                                        city=city,
                                                        country_code=country_code),
                                       account_id=None))
    return result.get()    
