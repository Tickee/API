from htmllaundry import cleaners
import colander
import htmllaundry
import re

PSP_LIST = ['mspfastcheckout', 'googlecheckout']
LANGUAGE_LIST = ['en', 'nl', 'fr', 'de', 'es', 'it']
CURRENCY_LIST = ['GBP', 'EUR', 'USD']

# -- General deferrers --------------------------------------------------------

@colander.deferred
def deferred_missing(node, kw):
    required_nodes = kw.get('required_nodes')
    if required_nodes and node.name in required_nodes:
        missing = colander.required
    else:
        missing = None
    return missing

def cleanup_html_preparer(value):
    if value is not colander.null:
        return htmllaundry.sanitize(value, cleaner=cleaners.DocumentCleaner, wrap=None)
    else:
        return colander.null

# -- General datatypes --------------------------------------------------------

class LocalizedString(colander.MappingSchema):
    language = colander.SchemaNode(colander.String(),
                                   validator=colander.OneOf(LANGUAGE_LIST))
    text = colander.SchemaNode(colander.String(),
                               preparer=cleanup_html_preparer)

# -- Paymentprovider schema ---------------------------------------------------

class PaymentProvider(colander.MappingSchema):
    data = colander.SchemaNode(colander.Mapping(unknown='preserve'),
                               missing=deferred_missing)
    provider = colander.SchemaNode(colander.String(),
                                   validator=colander.OneOf(PSP_LIST),
                                   missing=deferred_missing)

# -- TicketScan schema --------------------------------------------------------

#class ScanUpdateInformation(colander.MappingSchema):
#    timestamp = colander.SchemaNode(colander.Integer())
#    event_id = colander.SchemaNode(colander.Integer())
#    
#    eventpart_id = colander.SchemaNode(colander.Integer(),
#                                    missing=deferred_missing)
#    tickettype_id = colander.SchemaNode(colander.Integer(),
#                                     missing=deferred_missing)


class TicketScan(colander.MappingSchema):
    timestamp = colander.SchemaNode(colander.Integer())
    

# -- Ticket schema ------------------------------------------------------------

class Ticket(colander.MappingSchema):
    user_id = colander.SchemaNode(colander.Integer())

# -- TicketOrder schema -------------------------------------------------------

class TicketOrder(colander.MappingSchema):
    tickettype = colander.SchemaNode(colander.Integer(), 
                                     missing=deferred_missing)
    user = colander.SchemaNode(colander.Integer(), 
                                missing=deferred_missing)
    amount = colander.SchemaNode(colander.Integer(),  
                                 missing=deferred_missing)
    guest = colander.SchemaNode(colander.Boolean(),
                                missing=False)
    paper = colander.SchemaNode(colander.Boolean(),
                                missing=False)
    users_allocate = colander.SchemaNode(colander.Mapping(unknown='preserve'), missing=deferred_missing)
    
    
class OrderAction(colander.MappingSchema):
    checkout = colander.SchemaNode(colander.Boolean(),
                                   missing=False)
    user = colander.SchemaNode(colander.Integer(),
                               missing=None)
    redirect_url = colander.SchemaNode(colander.String(), 
                                       missing=deferred_missing)
    
    mail = colander.SchemaNode(colander.Boolean(),
                               missing=False)
    gift = colander.SchemaNode(colander.Boolean(),
                               missing=False)

# -- User schema --------------------------------------------------------------

class User(colander.MappingSchema):
    first_name = colander.SchemaNode(colander.String(), 
                                     missing=deferred_missing)
    last_name = colander.SchemaNode(colander.String(), 
                                    missing=deferred_missing)
    email = colander.SchemaNode(colander.String(), 
                                validator=colander.Email(), 
                                missing=deferred_missing)
    password = colander.SchemaNode(colander.String(), 
                                   missing=deferred_missing)
    active = colander.SchemaNode(colander.Boolean(),
                                 missing=deferred_missing)
    social = colander.SchemaNode(colander.Mapping(unknown='preserve'), missing=deferred_missing)
    address = colander.SchemaNode(colander.Mapping(unknown='preserve'), missing=deferred_missing)
    crm = colander.SchemaNode(colander.Mapping(unknown='preserve'), missing=deferred_missing)
    local = colander.SchemaNode(colander.Mapping(unknown='preserve'), missing=deferred_missing)

# -- Account schema -----------------------------------------------------------

def validate_shortname(node, value):
    """ Checks if a shortname only contains alfanumeric characters """
    p = re.compile('^[-\w]+$')
    if p.search(value) is None:
        raise colander.Invalid(node, 'only acolanlphanumeric characters allowed', value)


class Account(colander.MappingSchema):
    name = colander.SchemaNode(colander.String(), missing=deferred_missing)
    subtitle = colander.SchemaNode(colander.String(), missing=deferred_missing, preparer=cleanup_html_preparer)
    short_name = colander.SchemaNode(colander.String(), validator=validate_shortname, missing=deferred_missing)
    owner = colander.SchemaNode(colander.Int(), missing=deferred_missing) 
    email = colander.SchemaNode(colander.String(), validator=colander.Email(), missing=deferred_missing)
    active = colander.SchemaNode(colander.Boolean(), missing=deferred_missing)
    url = colander.SchemaNode(colander.String(), missing=deferred_missing)
    phone = colander.SchemaNode(colander.String(), missing=deferred_missing)
    vat = colander.SchemaNode(colander.Int(), missing=deferred_missing)
    vatnumber = colander.SchemaNode(colander.String(), missing=deferred_missing)
    handling_fee = colander.SchemaNode(colander.Int(), missing=deferred_missing)
    currency = colander.SchemaNode(colander.String(), validator=colander.OneOf(CURRENCY_LIST), missing=deferred_missing)
    preferred_psp = colander.SchemaNode(colander.String(), validator=colander.OneOf(PSP_LIST), missing=deferred_missing)
    theme = colander.SchemaNode(colander.Mapping(unknown='preserve'), missing=deferred_missing)
    social = colander.SchemaNode(colander.Mapping(unknown='preserve'), missing=deferred_missing)
    ext = colander.SchemaNode(colander.Mapping(unknown='preserve'), missing=deferred_missing)

# -- Tickettype schema --------------------------------------------------------

class TicketType(colander.MappingSchema):
    name = colander.SchemaNode(colander.String(),
                               missing=deferred_missing)
    description = LocalizedString(missing=deferred_missing)
    price = colander.SchemaNode(colander.Integer(),
                                missing=deferred_missing)
    currency = colander.SchemaNode(colander.String(),
                                   missing=deferred_missing)
    units = colander.SchemaNode(colander.Integer(),
                                missing=deferred_missing)
    active = colander.SchemaNode(colander.Boolean(),
                                 missing=deferred_missing)
    sales_end = colander.SchemaNode(colander.Integer(),
                                    missing=deferred_missing)

class TicketTypes(colander.SequenceSchema):
    tickettype = TicketType()

# -- Event schema -------------------------------------------------------------

class EventPart(colander.MappingSchema):
    name = colander.SchemaNode(colander.String(),
                               missing="") # TODO: remove hack
    starts_on = colander.SchemaNode(colander.Integer(),
                                    missing=deferred_missing)
    minutes = colander.SchemaNode(colander.Integer(),
                                  missing=deferred_missing)
    venue_id = colander.SchemaNode(colander.Integer(),
                                   missing=deferred_missing)
    description = LocalizedString(missing=deferred_missing)

class EventParts(colander.SequenceSchema):
    eventpart = EventPart()

class Event(colander.MappingSchema):
    name = colander.SchemaNode(colander.String(),
                               missing=deferred_missing)
    url = colander.SchemaNode(colander.String(),
                              missing=deferred_missing)
    active = colander.SchemaNode(colander.Boolean(),
                                 missing=deferred_missing)
    public = colander.SchemaNode(colander.Boolean(),
                                 missing=deferred_missing)
    description = LocalizedString(missing=deferred_missing)
    parts = EventParts(missing=deferred_missing)
    image_url = colander.SchemaNode(colander.String(),
                                    missing=deferred_missing)
    email = colander.SchemaNode(colander.String(),
                                missing=deferred_missing,
                                validator=colander.Email())
    tickettypes = TicketTypes(missing=deferred_missing)
    social = colander.SchemaNode(colander.Mapping(unknown='preserve'),
                                missing=deferred_missing)
    

# -- Location schema ----------------------------------------------------------

class Address(colander.MappingSchema):
    street_line1 = colander.SchemaNode(colander.String(),
                                       missing=deferred_missing)
    street_line2 = colander.SchemaNode(colander.String(),
                                       missing=deferred_missing)
    postal_code = colander.SchemaNode(colander.String(),
                                      missing=deferred_missing)
    city = colander.SchemaNode(colander.String(),
                               missing=deferred_missing)
    country = colander.SchemaNode(colander.String(),
                                  missing=deferred_missing)

class Location(colander.MappingSchema):
    name = colander.SchemaNode(colander.String(),
                               missing=deferred_missing)
    address = Address(missing=deferred_missing)