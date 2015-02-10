from celery.execute import send_task
from pyramid.view import view_config


#config.add_route('01-paymentprovider-notify',  '/0.1/payments/{psp_id:\d+}')


@view_config(route_name='01-psp-notify', 
             renderer='string')
def psp_notify(request):
    """Handles notifications received from the payment service providers.
    
    Request::
    
        [GET,POST] /0.1/psp/{id}/notify
    
    Parameters:
        Anything
            
    Returns:
        Each payment service provider requires a different response.
        The creation of the response information is handled by the provider class 
        of the payment service provider. 
        
    """
    # URL Parameters
    psp_id = int(request.matchdict.get('psp_id'))
    
    context = dict(message = request.body,
                   params = request.params.dict_of_lists())
    
    result = send_task("tickee.paymentproviders.entrypoints.notification", 
                       kwargs=dict(psp_id=psp_id,
                                   context=context))
    return result.get()