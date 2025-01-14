"""Odoo-specific operations for domain testing."""

import odoorpc
from .converter import Variable

def test_in_odoo(domain, model, host, db, username, password, port=8069):
    """Test if domain works in Odoo via OdooRPC.
    
    Args:
        domain: Odoo domain list
        model: Odoo model name (e.g., res.partner)
        host: Odoo server hostname
        db: Database name
        username: User login
        password: User password
        port: Odoo server port (default: 8069)
        
    Returns:
        tuple: (success, message)
            - success (bool): True if domain is valid
            - message (str): Result message or error
    """
    try:
        # Connect to Odoo
        odoo = odoorpc.ODOO(host, port=port, protocol='jsonrpc')
        odoo.login(db, username, password)
        
        # Convert Variable objects to their string values
        processed_domain = []
        for item in domain:
            if isinstance(item, tuple):
                field, operator, value = item
                if isinstance(value, Variable):
                    # Convert self.env to odoo.env
                    value = value.name.replace('self.env', 'odoo.env')
                processed_domain.append((field, operator, value))
            else:
                processed_domain.append(item)
            
        # Search using domain
        Model = odoo.env[model]
        result = Model.search_count(processed_domain)
        return True, f"Valid (found {result} records)"
    except Exception as e:
        return False, str(e)
