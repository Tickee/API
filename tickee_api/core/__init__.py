from functools import wraps
import colander
import json

def validate_schema(schema_klass, **bindings):
    """Decorator that takes a colander schema definition and validates the request body with
    said schema. If it matches, the view function may be executed."""
    
    def schema_validator(f):
        
        def wrapper(*args, **kwargs):          
            request = kwargs.get('request')
            schema = schema_klass().bind(**bindings)
            try:
                deserialized_json_body = schema.deserialize(request.json_body)
                
                kwargs['request'].deserialized_body = deserialized_json_body
                try:
                    kwargs['request'].body = json.dumps(deserialized_json_body)
                except:
                    pass
            except colander.Invalid as e:
                request.response.status_int = 400
                return dict(error='invalid request body',
                            problems=e.asdict())
            except ValueError:
                request.response.status_int = 400
                return dict(error='invalid request body',
                            problems=dict(request='body was not json'))
            else:
                return f(*args, **kwargs)
            
        return wraps(f)(wrapper)
    
    return schema_validator


def return_fields(default_fields=['id'],
                  mandatory_fields=[]):
    """Decorator that only shows specific fields of a result. The default_fields argument specifies which 
    fields should be returned when no specific fields were requested. The mandatory_fields will always be
    sent with the result."""
    def field_returner(f):
        def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            requested_fields = request.params.get('fields')
            if requested_fields is not None:
                requested_fields = requested_fields.split(',')
                requested_fields = map(lambda x: x.strip(), requested_fields)
                fields = set(mandatory_fields + requested_fields)
            else:
                fields = set(mandatory_fields + default_fields)
            
            result = f(*args, **kwargs)
             
            if isinstance(result, dict):
                if "error" in result:
                    return result   
                return filter_dict(result, fields)
            if isinstance(result, list):
                return map(lambda d: filter_dict(d, fields), result)
            
            return result
        return wraps(f)(wrapper)
    return field_returner

def filter_dict(dictionary, fields):
    """Removes all unnecessary keys from a dictionary"""
    # return everything
    if "all" in fields:
        return dictionary
    
    # filter it
    for key in dictionary.keys():
        if key not in fields:
            del dictionary[key]
    return dictionary


#def require_parameters(scope, required_parameters, optional_parameters):
#    """Decorator that validates if all parameters are available in the request"""
#    
#    def parameter_validator(f):
#        
#        def wrapper(*args, **kwargs):
#            request = kwargs.get('request')
#            received_oauth2_context = kwargs.get('oauth2_context')
#            received_parameters = request.params
#            
#            if scope is None:
#                
#            
#            
#        
#        return wraps(f)(wrapper)
#    
#    return parameter_validator