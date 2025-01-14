#!/usr/bin/env python3
"""
Odoo Domain Expression Converter

This module contains the core converter logic for transforming
human-readable logical expressions into Odoo domain format.
"""

import odoorpc

class Variable:
    """Represents a variable reference in Odoo domain."""
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return self.name
        
    def __str__(self):
        return self.name

class ComplexDomainConverter:
    """Converts logical expressions to Odoo domain format."""
    
    def __init__(self):
        self.operators = {
            '=', '!=', '>', '<', '>=', '<=',
            'like', 'not_like', 'ilike', 'not_ilike',  # Changed to use underscore
            'in', 'not_in', '=?', 'child_of'
        }
        self.python_literals = {'True', 'False', 'None'}

    def tokenize(self, expr):
        """Split expression into tokens while preserving quotes and parentheses.
        
        Args:
            expr: Expression string
            
        Returns:
            list: Tokens
            
        Example:
            "name = 'John' & age >= 18"
            -> ["name", "=", "'John'", "&", "age", ">=", "18"]
        """
        tokens = []
        current = []
        in_quotes = False
        quote_char = None
        
        i = 0
        while i < len(expr):
            char = expr[i]
            
            # Handle quotes
            if char in ["'", '"']:
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                current.append(char)
                i += 1
                continue
                
            # Handle parentheses and logical operators when not in quotes
            if not in_quotes and char in ['(', ')', '&', '|']:
                if current:
                    tokens.append(''.join(current).strip())
                    current = []
                tokens.append(char)
                i += 1
                continue
                
            # Handle regular characters
            current.append(char)
            i += 1
                
        if current:
            tokens.append(''.join(current).strip())
            
        return [t for t in tokens if t]

    def parse_condition(self, condition_str):
        """Parse a single condition into Odoo domain tuple.
        
        Args:
            condition_str: String like "field operator value"
            
        Returns:
            tuple: (field, operator, value)
            
        Examples:
            "name = 'John'"    -> ('name', '=', 'John')
            "age >= 18"        -> ('age', '>=', 18)
            "ids in [1,2,3]"   -> ('ids', 'in', [1,2,3])
        """
        # Split condition into parts while preserving quotes
        parts = []
        current = []
        in_quotes = False
        quote_char = None
        
        for char in condition_str:
            if char in ["'", '"']:
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                current.append(char)
            elif char.isspace() and not in_quotes:
                if current:
                    parts.append(''.join(current).strip())
                    current = []
            else:
                current.append(char)
                
        if current:
            parts.append(''.join(current).strip())
            
        # Find the operator
        if not parts:
            raise ValueError(f"Empty condition: {condition_str}")
            
        field = parts[0]
        rest = ' '.join(parts[1:])
        
        # Find the longest matching operator
        operator = None
        value = None
        for op in sorted(self.operators, key=len, reverse=True):
            if rest.startswith(op):
                operator = op
                value = rest[len(op):].strip()
                break
                
        if not operator:
            raise ValueError(f"Invalid operator in: {condition_str}. Must be one of: {', '.join(sorted(self.operators))}")
            
        if not value:
            raise ValueError(f"Missing value in: {condition_str}")
            
        # Convert underscore operators back to space
        if operator in {'not_like', 'not_ilike', 'not_in'}:
            operator = operator.replace('_', ' ')
            
        # Parse the value
        if value in self.python_literals:
            value = eval(value)
        elif value.startswith(("'", '"')) and value.endswith(("'", '"')):
            value = value[1:-1]
        elif value.replace('.', '').isdigit():
            value = float(value) if '.' in value else int(value)
        elif value.startswith('[') and value.endswith(']'):
            value = value[1:-1].split(',')
            value = [v.strip().strip("'\"") for v in value]
            parsed_value = []
            for v in value:
                if v in self.python_literals:
                    parsed_value.append(eval(v))
                elif v.replace('.', '').isdigit():
                    parsed_value.append(float(v) if '.' in v else int(v))
                elif v.startswith(("'", '"')) and v.endswith(("'", '"')):
                    parsed_value.append(v[1:-1])
                else:
                    parsed_value.append(v)
            value = parsed_value
        else:
            value = Variable(value.strip())
            
        return (field, operator, value)

    def _to_prefix(self, operands):
        """Convert infix expression to prefix notation."""
        if len(operands) == 1:
            return operands[0]
            
        # Find the rightmost OR operator first
        or_index = None
        nested_level = 0
        for i, token in enumerate(reversed(operands)):
            i = len(operands) - 1 - i
            if token == '(':
                nested_level += 1
            elif token == ')':
                nested_level -= 1
            elif nested_level == 0 and token == '|':
                or_index = i
                break
                
        # If no OR, find rightmost AND
        if or_index is None:
            for i, token in enumerate(reversed(operands)):
                i = len(operands) - 1 - i
                if token == '(':
                    nested_level += 1
                elif token == ')':
                    nested_level -= 1
                elif nested_level == 0 and token == '&':
                    or_index = i
                    break
                    
        # If no operator found, default to AND
        if or_index is None:
            operator = '&'
            left = operands[0] if len(operands) == 1 else self._to_prefix(operands[:-1])
            right = operands[-1]
        else:
            operator = operands[or_index]
            left = self._to_prefix(operands[:or_index]) if or_index > 0 else operands[0]
            right = self._to_prefix(operands[or_index + 1:]) if or_index < len(operands) - 1 else operands[-1]
            
        return [operator, right, left]

    def _flatten(self, expr):
        """Flatten nested expressions."""
        if not isinstance(expr, list):
            return [expr]
            
        result = []
        for item in expr:
            if isinstance(item, list):
                result.extend(self._flatten(item))
            else:
                result.append(item)
        return result

    def parse_expression(self, tokens):
        """Convert tokens to Odoo domain using prefix notation.
        
        Args:
            tokens: List of expression tokens
            
        Returns:
            list: Odoo domain in prefix notation
            
        Example:
            ["name", "=", "'John'", "&", "age", ">=", "18"]
            -> ['&', ('name', '=', 'John'), ('age', '>=', 18)]
        """
        if not tokens:
            return []
            
        # Parse tokens into nested structure
        stack = []
        current = []
        
        for token in tokens:
            if token == '(':
                stack.append(current)
                current = []
            elif token == ')':
                if stack:
                    expr = current
                    current = stack.pop()
                    if expr:
                        current.extend(expr)
            else:
                if token in ['&', '|']:
                    current.append(token)
                else:
                    current.append(self.parse_condition(token))
                    
        if stack:
            raise ValueError("Mismatched parentheses")
            
        if not current:
            return []
            
        return self._flatten(self._to_prefix(current))

    def to_domain(self, expr):
        """Convert expression to Odoo domain format.
        
        Args:
            expr: Expression string
            
        Returns:
            list: Odoo domain
            
        Example:
            "name = 'John' & age >= 18"
            -> ['&', ('name', '=', 'John'), ('age', '>=', 18)]
        """
        tokens = self.tokenize(expr)
        return self.parse_expression(tokens)

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
