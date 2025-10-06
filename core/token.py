"""
Token class for lexical analysis
Represents individual tokens found in the input string
"""

class Token:
    """Represents a token with type, value, and position information"""
    
    def __init__(self, token_type, value, position, line=1, column=None):
        """
        Initialize a token
        
        Args:
            token_type (str): Type of token (PLUS, MULTIPLY, ID, etc.)
            value (str): The actual string value
            position (int): Position in the input string
            line (int): Line number (default 1)
            column (int): Column number (calculated if None)
        """
        self.type = token_type
        self.value = value
        self.position = position
        self.line = line
        self.column = column if column is not None else position + 1
    
    def __str__(self):
        """String representation of the token"""
        return f"Token({self.type}, '{self.value}', pos:{self.position})"
    
    def __repr__(self):
        """Detailed representation for debugging"""
        return f"Token(type='{self.type}', value='{self.value}', position={self.position}, line={self.line}, column={self.column})"
    
    def is_valid(self):
        """Check if token is valid (not INVALID type)"""
        return self.type != 'INVALID'
    
    def get_display_info(self):
        """Get formatted information for display"""
        return {
            'type': self.type,
            'value': self.value,
            'position': self.position,
            'line': self.line,
            'column': self.column
        }

# Token type constants for consistency
class TokenType:
    """Constants for different token types"""
    PLUS = 'PLUS'
    MULTIPLY = 'MULTIPLY'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    ID = 'ID'
    INVALID = 'INVALID'
    EOF = 'EOF'  # End of file/input