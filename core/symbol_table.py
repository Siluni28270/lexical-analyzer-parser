"""
Symbol Table Implementation
Stores and manages information about tokens and identifiers
"""

from collections import defaultdict
from core.token import TokenType

class SymbolTableEntry:
    """Represents a single entry in the symbol table"""
    
    def __init__(self, token):
        """
        Initialize symbol table entry
        
        Args:
            token: Token object to create entry for
        """
        self.token_value = token.value
        self.token_type = token.type
        self.count = 1
        self.positions = [token.position]
        self.first_occurrence = token.position
        self.attributes = self._get_token_attributes(token)
    
    def add_occurrence(self, token):
        """Add another occurrence of this token"""
        self.count += 1
        self.positions.append(token.position)
    
    def _get_token_attributes(self, token):
        """Get additional attributes based on token type"""
        attributes = {}
        
        if token.type == TokenType.ID:
            if token.value.isdigit():
                attributes['category'] = 'NUMERIC'
                attributes['value'] = int(token.value)
            elif token.value.isalpha():
                attributes['category'] = 'ALPHABETIC'
                if token.value.isupper():
                    attributes['case'] = 'UPPERCASE'
                elif token.value.islower():
                    attributes['case'] = 'LOWERCASE'
        elif token.type in [TokenType.PLUS, TokenType.MULTIPLY]:
            attributes['category'] = 'OPERATOR'
            attributes['precedence'] = 2 if token.type == TokenType.MULTIPLY else 1
            attributes['associativity'] = 'LEFT'
        elif token.type in [TokenType.LPAREN, TokenType.RPAREN]:
            attributes['category'] = 'DELIMITER'
        
        return attributes
    
    def get_display_info(self):
        """Get formatted information for display"""
        return {
            'value': self.token_value,
            'type': self.token_type,
            'count': self.count,
            'positions': self.positions,
            'first_occurrence': self.first_occurrence,
            'attributes': self.attributes
        }

class SymbolTable:
    """Symbol Table for storing token information"""
    
    def __init__(self):
        """Initialize empty symbol table"""
        self.entries = {}  # Dictionary mapping token values to entries
        self.total_tokens = 0
        self.unique_tokens = 0
        self.token_types_count = defaultdict(int)
    
    def add_token(self, token):
        """
        Add a token to the symbol table
        
        Args:
            token: Token object to add
        """
        # Skip invalid tokens
        if not token.is_valid():
            return
        
        self.total_tokens += 1
        self.token_types_count[token.type] += 1
        
        # Create unique key (value + type to handle same value, different type)
        key = f"{token.value}_{token.type}"
        
        if key in self.entries:
            # Token already exists, add occurrence
            self.entries[key].add_occurrence(token)
        else:
            # New token, create entry
            self.entries[key] = SymbolTableEntry(token)
            self.unique_tokens += 1
    
    def get_entry(self, token_value, token_type):
        """Get symbol table entry for specific token"""
        key = f"{token_value}_{token_type}"
        return self.entries.get(key)
    
    def get_all_entries(self):
        """Get all symbol table entries"""
        return list(self.entries.values())
    
    def get_entries_by_type(self, token_type):
        """Get all entries of specific token type"""
        return [entry for entry in self.entries.values() 
                if entry.token_type == token_type]
    
    def get_statistics(self):
        """Get symbol table statistics"""
        stats = {
            'total_tokens': self.total_tokens,
            'unique_tokens': self.unique_tokens,
            'token_types': dict(self.token_types_count),
            'identifier_count': self.token_types_count[TokenType.ID],
            'operator_count': (self.token_types_count[TokenType.PLUS] + 
                             self.token_types_count[TokenType.MULTIPLY]),
            'delimiter_count': (self.token_types_count[TokenType.LPAREN] + 
                              self.token_types_count[TokenType.RPAREN])
        }
        return stats
    
    def get_formatted_table(self):
        """Get formatted symbol table for display"""
        if not self.entries:
            return "Symbol table is empty"
        
        # Header
        result = "SYMBOL TABLE\n"
        result += "=" * 80 + "\n"
        result += f"{'Value':<8} {'Type':<12} {'Count':<6} {'Positions':<20} {'Attributes'}\n"
        result += "-" * 80 + "\n"
        
        # Sort entries by first occurrence position
        sorted_entries = sorted(self.entries.values(), 
                              key=lambda x: x.first_occurrence)
        
        # Add each entry
        for entry in sorted_entries:
            positions_str = ', '.join(map(str, entry.positions[:5]))  # Show first 5
            if len(entry.positions) > 5:
                positions_str += f" (+{len(entry.positions)-5} more)"
            
            # Format attributes
            attr_str = ""
            if entry.attributes:
                attr_parts = []
                for key, value in entry.attributes.items():
                    attr_parts.append(f"{key}={value}")
                attr_str = ", ".join(attr_parts)
            
            result += f"{entry.token_value:<8} {entry.token_type:<12} {entry.count:<6} {positions_str:<20} {attr_str}\n"
        
        # Add statistics
        stats = self.get_statistics()
        result += "\n" + "=" * 80 + "\n"
        result += "STATISTICS:\n"
        result += f"Total tokens: {stats['total_tokens']}\n"
        result += f"Unique tokens: {stats['unique_tokens']}\n"
        result += f"Identifiers: {stats['identifier_count']}\n"
        result += f"Operators: {stats['operator_count']}\n"
        result += f"Delimiters: {stats['delimiter_count']}\n"
        
        return result
    
    def clear(self):
        """Clear all entries from symbol table"""
        self.entries.clear()
        self.total_tokens = 0
        self.unique_tokens = 0
        self.token_types_count.clear()
    
    def has_entries(self):
        """Check if symbol table has any entries"""
        return len(self.entries) > 0
    
    def get_token_coverage(self):
        """Get coverage information about token types"""
        coverage = {
            'has_identifiers': self.token_types_count[TokenType.ID] > 0,
            'has_operators': (self.token_types_count[TokenType.PLUS] > 0 or 
                            self.token_types_count[TokenType.MULTIPLY] > 0),
            'has_parentheses': (self.token_types_count[TokenType.LPAREN] > 0 and 
                              self.token_types_count[TokenType.RPAREN] > 0),
            'parentheses_balanced': (self.token_types_count[TokenType.LPAREN] == 
                                   self.token_types_count[TokenType.RPAREN])
        }
        return coverage