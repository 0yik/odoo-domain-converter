#!/usr/bin/env python3
"""
Odoo Domain Expression Converter CLI

This tool converts human-readable logical expressions into Odoo domain format
and validates them against an Odoo server using OdooRPC.

Example expressions:
    name = 'John'                     -> [('name', '=', 'John')]
    age >= 18                         -> [('age', '>=', 18)]
    name = 'John' & active = True     -> ['&', ('name', '=', 'John'), ('active', '=', True)]
    name = 'John' | name = 'Jane'     -> ['|', ('name', '=', 'John'), ('name', '=', 'Jane')]
    
    # Nested conditions
    (name = 'John' & age >= 18) | active = True
    -> ['|', '&', ('name', '=', 'John'), ('age', '>=', 18), ('active', '=', True)]
    
    # Special operators
    parent_id child_of 1              -> [('parent_id', 'child_of', 1)]
    name not_like 'Test%'             -> [('name', 'not like', 'Test%')]
    name not_ilike 'Test%'            -> [('name', 'not ilike', 'Test%')]
    category_id in [1, 2]             -> [('category_id', 'in', [1, 2])]
    tag_ids not_in [1, 2, 3]         -> [('tag_ids', 'not in', [1, 2, 3])]
    
    # Odoo expressions
    user_id = odoo.env.user.id        -> [('user_id', '=', odoo.env.user.id)]
    company_id = odoo.env.company.id  -> [('company_id', '=', odoo.env.company.id)]

Note on operators:
    For operators with spaces ('not like', 'not ilike', 'not in'), use underscore:
    - 'not_like' instead of 'not like'
    - 'not_ilike' instead of 'not ilike'
    - 'not_in' instead of 'not in'
"""

import argparse
from .converter import ComplexDomainConverter
from .odoo import test_in_odoo

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--host', required=True,
                       help='Odoo server hostname (e.g., localhost)')
    parser.add_argument('--port', '-p', type=int, default=8069,
                       help='Odoo server port (default: 8069)')
    parser.add_argument('--database', '-d', required=True,
                       help='Database name')
    parser.add_argument('--username', '-u', required=True,
                       help='Username')
    parser.add_argument('--password', '-w', required=True,
                       help='Password')
    parser.add_argument('--model', '-m', required=True,
                       help='Model name (e.g., res.partner)')
    parser.add_argument('--expression', '-e', required=True,
                       help='Logical expression to convert')
    
    args = parser.parse_args()
    
    converter = ComplexDomainConverter()
    
    print(f"\nTesting with Odoo at {args.host}:{args.port}")
    print(f"Model: {args.model}")
    print("-" * 60)
    
    try:
        print(f"\nExpression: {args.expression}")
        domain = converter.to_domain(args.expression)
        
        # Convert self.env to odoo.env in the domain display
        domain_str = str(domain).replace('self.env', 'odoo.env')
        print(f"Domain: {domain_str}")
        
        success, message = test_in_odoo(domain, args.model, args.host, args.database, 
                                      args.username, args.password, args.port)
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ Invalid: {message}")
            
    except Exception as e:
        print(f"✗ Conversion error: {str(e)}")
        
    print("-" * 60)

if __name__ == "__main__":
    main()
