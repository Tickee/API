'''

'''

INTERNAL = 'scope_internal'
"""OAuth2 scope only for clients developed by Tickee BVBA."""

ACCOUNT_MGMT = 'scope_account_mgmt'
"""OAuth2 scope of the account owner. Read and write access to everything owned
by the account."""

ACCOUNT_READ = 'scope_account_read'
"""OAuth2 scope for reading account information. Read access to everything owned
by the account."""

ORDER_MGMT = 'scope_order_mgmt'
"""OAuth2 scope for third party plugins that are allowed to make orders for an
event"""

SCANNING = 'scope_scanning'
"""OAuth2 scope for third party applications to scan tickets"""