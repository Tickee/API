import colander

class Account(colander.MappingSchema):
    """
    {
        "name": "UniqueNameNoSpaces",
        "full_name": "Account name with spaces",
        "active": True,
        "website": "http://www.example.com",
        "email": "account@example.com"
        "vat": 21
    }
    """
    name = colander.SchemaNode(colander.String())
    full_name = colander.SchemaNode(colander.String())
    email = colander.SchemaNode(colander.Email())
    active = colander.SchemaNode(colander.Boolean())
    website = colander.SchemaNode(colander.String())
    vat = colander.SchemaNode(colander.Int())
    