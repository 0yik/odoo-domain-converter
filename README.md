# odoo-domain-converter
This tool converts human-readable logical expressions into Odoo domain format and validates them against an Odoo server using OdooRPC.

## Installation

You can install the package directly from PyPI:

```bash
pip install odoo-domain-converter
```

Or install from source:

```bash
git clone https://github.com/0yik/odoo-domain-converter.git
cd odoo-domain-converter
pip install -e .
```

## Usage

### As a Command Line Tool

```bash
odoo-domain-converter --host localhost --port 8069 --database mydb \
                     --username admin --password admin \
                     --model res.partner \
                     --expression "name = 'John' & is_company = True"
```

### As a Python Package

```python
from odoo_domain_converter import ComplexDomainConverter

# Initialize the converter
converter = ComplexDomainConverter()

# Convert an expression to Odoo domain
expression = "name = 'John' & is_company = True"
domain = converter.to_domain(expression)
print(domain)  # ['&', ('name', '=', 'John'), ('is_company', '=', True)]

# Test the domain against an Odoo server
from odoo_domain_converter import test_in_odoo

success, message = test_in_odoo(
    domain=domain,
    model='res.partner',
    host='localhost',
    db='mydb',
    username='admin',
    password='admin'
)
print(message)  # "Valid (found X records)"
```

## Example Expressions

All examples below use real fields from `res.partner` model:

```
# Basic conditions
name = 'John'                           -> [('name', '=', 'John')]
email = 'john@example.com'              -> [('email', '=', 'john@example.com')]
is_company = True                       -> [('is_company', '=', True)]
active = True                           -> [('active', '=', True)]

# Logical combinations
name = 'John' & is_company = False      -> ['&', ('name', '=', 'John'), ('is_company', '=', False)]
email ilike '%@example.com' | email ilike '%@test.com'  
-> ['|', ('email', 'ilike', '%@example.com'), ('email', 'ilike', '%@test.com')]

# Nested conditions
(name = 'John' & is_company = True) | active = True
-> ['|', '&', ('name', '=', 'John'), ('is_company', '=', True), ('active', '=', True)]

# Special operators
parent_id child_of 1                    -> [('parent_id', 'child_of', 1)]
name not_like 'Test%'                   -> [('name', 'not like', 'Test%')]
name not_ilike 'test%'                  -> [('name', 'not ilike', 'test%')]
category_id in [1, 2]                   -> [('category_id', 'in', [1, 2])]
user_ids not_in [1, 2, 3]              -> [('user_ids', 'not in', [1, 2, 3])]

# Odoo expressions
user_id = self.env.user.id             -> [('user_id', '=', self.env.user.id)]
company_id = self.env.company.id       -> [('company_id', '=', self.env.company.id)]
```

## Note on Operators

For operators with spaces, use underscore:
- Use `not_like` instead of `not like`
- Use `not_ilike` instead of `not ilike`
- Use `not_in` instead of `not in`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
